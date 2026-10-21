import copy
import shutil
from pathlib import Path
from types import SimpleNamespace

import pytest

from palworld_pal_editor.core.map_progress import (
    HOST_UID, LocalMapData, local_map, progress_status, travel_catalog, unlock_all_travel,
)
from palworld_pal_editor.core.pal_objects import PalObjects

FIXTURE = Path(__file__).parents[1] / 'tests/saves/1.0/8C439FF04713B5F986F9CAB485575089'


def player(uid=HOST_UID):
    return SimpleNamespace(PlayerUId=uid, _player_save_data={
        'RecordData': PalObjects.PalLoggedinPlayerSaveDataRecordData({'Unrelated': PalObjects.IntProperty(7)})})


def without_masks(doc):
    values = copy.deepcopy(doc.gvas.properties)
    data = values['SaveData']['value']
    for entry in data.get('WorldMapUISaveDataMap', {}).get('value', []):
        entry['value']['MaskTextureData']['value']['values'] = None
    return values


def test_real_local_data_reveal_roundtrips_without_changing_other_fields(tmp_path):
    doc = LocalMapData(FIXTURE / 'LocalData.sav')
    assert doc.summary()['available']
    outside = without_masks(doc)
    rgb = {name: bytes(p['value']['values']) for name, p in doc.masks()}
    doc.reveal()
    for name, prop in doc.masks():
        mask = bytes(prop['value']['values'])
        assert not any(mask[3::4])
        for offset in (0, 1, 2):
            assert mask[offset::4] == rgb[name][offset::4]
    target = tmp_path / 'LocalData.sav'
    target.write_bytes(doc.serialize())
    reopened = LocalMapData(target)
    assert without_masks(reopened) == outside
    assert all(m['revealed'] == m['pixels'] for m in reopened.summary()['maps'])


def test_unknown_map_and_external_changes_are_refused(tmp_path):
    path = tmp_path / 'LocalData.sav'
    path.write_bytes((FIXTURE / 'LocalData.sav').read_bytes())
    doc = LocalMapData(path)
    path.write_bytes(b'external change')
    with pytest.raises(ValueError, match='changed outside'):
        doc.serialize()
    assert not LocalMapData(path).summary()['available']


def test_unlock_initializes_flags_and_preserves_unknown_entries(tmp_path):
    p = player('22222222-2222-2222-2222-222222222222')
    manager = SimpleNamespace(local_map_data=None, file_path=tmp_path)
    flags = PalObjects.MapProperty('NameProperty', 'BoolProperty')
    flags['value'] = [{'key': 'future-or-unrelated', 'value': False}]
    record = p._player_save_data['RecordData']['value']
    record['FastTravelPointUnlockFlag'] = flags
    unlock_all_travel(manager, p)
    assert record['Unrelated']['value'] == 7
    assert record['FastTravelPointUnlockFlag']['value'][0] == {'key': 'future-or-unrelated', 'value': False}
    status = progress_status(manager, p)
    assert status['travel']['unlocked'] == status['travel']['total'] == 182
    assert not status['fog']['available']
    assert manager.local_map_data is None
    before = copy.deepcopy(record)
    unlock_all_travel(manager, p)
    assert record == before


def test_invalid_local_warp_layout_does_not_partially_unlock_player():
    p = player()
    doc = LocalMapData(FIXTURE / 'LocalData.sav')
    doc.data()['Local_WarpPointUnlockFlag']['value_type'] = 'IntProperty'
    manager = SimpleNamespace(local_map_data=doc)
    before = copy.deepcopy(p._player_save_data)
    with pytest.raises(ValueError):
        unlock_all_travel(manager, p)
    assert p._player_save_data == before


def test_save_manager_writes_local_data_and_reopens_it(tmp_path, monkeypatch):
    from palworld_pal_editor.core.save_manager import SaveManager
    from palworld_pal_editor.core.save_io import SaveFailed
    monkeypatch.setattr(SaveManager, '_instance', None)
    manager = SaveManager()
    source = tmp_path / 'source'
    shutil.copytree(FIXTURE, source)
    original_local = (source / 'LocalData.sav').read_bytes()
    assert manager.open(str(source))
    host = manager.get_player(HOST_UID)
    assert host
    local_map(manager).reveal()
    unlock_all_travel(manager, host)
    original_write = Path.write_bytes
    fail_once = [True]
    def fail_local_write(path, data):
        if path == source / 'LocalData.sav' and fail_once[0]:
            fail_once[0] = False
            original_write(path, data[:64])
            raise OSError('simulated interrupted LocalData write')
        return original_write(path, data)
    monkeypatch.setattr(Path, 'write_bytes', fail_local_write)
    with pytest.raises(SaveFailed):
        manager.save(str(source))
    assert (source / 'LocalData.sav').read_bytes() == original_local
    assert local_map(manager).dirty
    output = tmp_path / 'output'
    manager.save(str(output))
    assert (output / 'LocalData.sav').exists()
    assert manager.open(str(output))
    state = progress_status(manager, manager.get_player(HOST_UID))
    assert state['travel']['unlocked'] == 182
    assert all(m['revealed'] == m['pixels'] for m in state['fog']['maps'])
    assert len(travel_catalog()['warp_ids']) == 8
