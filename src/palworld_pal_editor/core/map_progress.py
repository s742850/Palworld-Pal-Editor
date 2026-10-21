"""Player travel flags and the host client's LocalData exploration masks.

Only verified 1.0 layouts are editable. Unrelated client records remain opaque.
The catalog documents its pinned actor-ID sources; no network is used at runtime.
"""
import copy
import hashlib
from functools import lru_cache
from pathlib import Path

from palworld_save_tools.gvas import GvasFile
from palworld_save_tools.palsav import compress_gvas_to_sav, decompress_sav_to_gvas
from palworld_save_tools.paltypes import PALWORLD_CUSTOM_PROPERTIES, PALWORLD_TYPE_HINTS

from palworld_pal_editor.core.pal_objects import PalObjects
from palworld_pal_editor.core.save_codec import skip_decode, skip_encode
from palworld_pal_editor.utils.data_provider import load_json

HOST_UID = '00000000-0000-0000-0000-000000000001'
LOCAL_CODEC = dict(PALWORLD_CUSTOM_PROPERTIES)
for _field in ('Local_MaxFriendshipPalIds', 'Local_MapObjectPaintPalette'):
    LOCAL_CODEC['.SaveData.' + _field] = (skip_decode, skip_encode)
MASK_LENGTHS = {'MainMap': 4194304, 'Tree': 1048576}


@lru_cache(maxsize=1)
def travel_catalog():
    catalog = load_json('fast_travel_points.json')
    for group in ('ids', 'warp_ids'):
        if len(catalog[group]) != len(set(catalog[group])) or any(
            len(value) != 32 or any(c not in '0123456789ABCDEF' for c in value)
            for value in catalog[group]
        ):
            raise ValueError('Invalid bundled travel-point catalog')
    return catalog


def flag_property(value):
    if value is None:
        return PalObjects.MapProperty('NameProperty', 'BoolProperty')
    if not isinstance(value, dict) or value.get('type') != 'MapProperty' or value.get('key_type') != 'NameProperty' or value.get('value_type') != 'BoolProperty':
        raise ValueError('Unsupported travel-flag map layout')
    entries = value.get('value')
    if not isinstance(entries, list) or any(
        not isinstance(e, dict) or not isinstance(e.get('key'), str) or type(e.get('value')) is not bool for e in entries
    ) or len({e['key'] for e in entries}) != len(entries):
        raise ValueError('Invalid or duplicate travel flags')
    return value


def unlocked_flags(original, ids):
    result = copy.deepcopy(flag_property(original))
    known = set(ids)
    present = set()
    for entry in result['value']:
        present.add(entry['key'])
        if entry['key'] in known:
            entry['value'] = True
    result['value'].extend({'key': point, 'value': True} for point in ids if point not in present)
    return result


class LocalMapData:
    def __init__(self, path):
        self.path = Path(path)
        self.dirty = False
        self.error = None
        self.gvas = None
        try:
            self.original = self.path.read_bytes()
            raw, self.save_type = decompress_sav_to_gvas(self.original)
            self.gvas = GvasFile.read(raw, PALWORLD_TYPE_HINTS, LOCAL_CODEC)
            if self.gvas.header.save_game_class_name != '/Script/Pal.PalLocalWorldSaveGame':
                raise ValueError('Not a LocalData save')
            self.masks()  # Refuse unknown versions before offering the control.
        except Exception:
            self.gvas = None
            self.error = 'LocalData.sav is missing or has an unsupported map layout'

    def data(self):
        if self.gvas is None:
            raise ValueError(self.error)
        return self.gvas.properties['SaveData']['value']

    def masks(self):
        data = self.data()
        if 'WorldMapUISaveDataMap' in data:
            prop = data['WorldMapUISaveDataMap']
            if prop.get('type') != 'MapProperty' or prop.get('key_type') != 'NameProperty' or prop.get('value_type') != 'StructProperty':
                raise ValueError('Unsupported map table')
            pairs = [(e['key'], e['value']['MaskTextureData']) for e in prop['value']]
            if len(pairs) != 2 or {n for n, _ in pairs} != set(MASK_LENGTHS):
                raise ValueError('Unsupported map set')
        else:
            legacy = [key for key in ('WorldMapMaskTextureV4', 'worldMapMaskTexture') if key in data]
            if len(legacy) != 1:
                raise ValueError('Missing or ambiguous map texture')
            pairs = [('MainMap', data[legacy[0]])]
        for name, prop in pairs:
            values = prop.get('value', {}).get('values')
            if prop.get('type') != 'ArrayProperty' or prop.get('array_type') != 'ByteProperty' or not isinstance(values, (list, bytes, bytearray)):
                raise ValueError('Unsupported mask texture')
            if len(values) != MASK_LENGTHS[name]:
                raise ValueError('Unsupported mask dimensions')
            bytes(values)  # Also checks the byte range.
        return pairs

    def reveal(self):
        staged = []
        for _, prop in self.masks():
            mask = bytearray(prop['value']['values'])
            mask[3::4] = bytes(len(mask) // 4)  # Preserve RGB; alpha=0 reveals fog.
            staged.append((prop, bytes(mask)))
        for prop, mask in staged:
            if bytes(prop['value']['values']) != mask:
                prop['value']['values'] = mask
                self.dirty = True

    def summary(self):
        if self.error:
            return {'available': False, 'reason': self.error, 'maps': []}
        return {'available': True, 'reason': None, 'maps': [
            {'name': name, 'pixels': len(prop['value']['values']) // 4,
             'revealed': bytes(prop['value']['values'])[3::4].count(0)}
            for name, prop in self.masks()]}

    def serialize(self):
        if hashlib.sha256(self.path.read_bytes()).digest() != hashlib.sha256(self.original).digest():
            raise ValueError('LocalData.sav changed outside the editor; reload the save first')
        raw = copy.deepcopy(self.gvas).write(LOCAL_CODEC)
        if self.save_type == 0x31:
            # The pinned native encoder advances twice after a uniform 128-KiB
            # subchunk. Cleared fog textures hit that bug. Standard Oodle copied
            # blocks keep the PLM format without passing those textures through
            # the faulty compression branch. Each block resets the decoder.
            payload = b''.join(b'\xcc\x0a' + raw[i:i + 0x40000]
                               for i in range(0, len(raw), 0x40000))
            encoded = len(raw).to_bytes(4, 'little') + len(payload).to_bytes(4, 'little') + b'PlM\x31' + payload
        else:
            encoded = compress_gvas_to_sav(raw, self.save_type)
        if decompress_sav_to_gvas(encoded)[0] != raw:
            raise ValueError('LocalData encoding failed its verification; no save was written')
        return encoded


def local_map(manager):
    if manager.local_map_data is None:
        manager.local_map_data = LocalMapData(manager.file_path / 'LocalData.sav')
    return manager.local_map_data


def player_record(player):
    record = player._player_save_data.get('RecordData')
    if not isinstance(record, dict) or record.get('type') != 'StructProperty' or record.get('struct_type') != 'PalLoggedinPlayerSaveDataRecordData':
        raise ValueError('Player record layout is unsupported')
    return record['value']


def progress_status(manager, player):
    catalog = travel_catalog()
    try:
        flags = flag_property(player_record(player).get('FastTravelPointUnlockFlag'))
        values = {e['key']: e['value'] for e in flags['value']}
        travel = {'available': True, 'unlocked': sum(values.get(k) is True for k in catalog['ids']),
                  'total': len(catalog['ids']), 'reason': None}
    except (KeyError, TypeError, ValueError) as error:
        travel = {'available': False, 'reason': str(error), 'total': len(catalog['ids'])}
    if str(player.PlayerUId) == HOST_UID:
        fog = local_map(manager).summary()
    else:
        fog = {'available': False, 'reason': 'LocalData belongs to the local host; client fog editing is supported only for the single-player host', 'maps': []}
    return {'travel': travel, 'fog': fog, 'catalog': catalog['game']}


def unlock_all_travel(manager, player):
    record = player_record(player)
    catalog = travel_catalog()
    prepared = unlocked_flags(record.get('FastTravelPointUnlockFlag'), catalog['ids'])
    local = local_map(manager) if str(player.PlayerUId) == HOST_UID else None
    prepared_warps = None
    if local is not None and local.gvas is not None:
        prepared_warps = unlocked_flags(local.data().get('Local_WarpPointUnlockFlag'), catalog['warp_ids'])
    record['FastTravelPointUnlockFlag'] = prepared
    if prepared_warps is not None and local.data().get('Local_WarpPointUnlockFlag') != prepared_warps:
        local.data()['Local_WarpPointUnlockFlag'] = prepared_warps
        local.dirty = True
