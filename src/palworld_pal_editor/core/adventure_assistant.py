"""Conservative, explainable suggestions; only an explicit apply mutates a save.

Rules are deliberately a small curated list, not a ranking of every legal Pal.
Captured species and unlocked recipes are evidence, not proof of natural progress.
All writes are additive and stay pending until the normal Save Changes operation.
"""
import hashlib
import json
from statistics import median

from palworld_pal_editor.config import Config
from palworld_pal_editor.core.pal_entity import PalEntity
from palworld_pal_editor.core.pal_mutations import TouchedParents
from palworld_pal_editor.core.pal_objects import PalObjects
from palworld_pal_editor.utils.data_provider import DataProvider, PAL_DATA, PAL_ATTACKS, TECH_DATA

GOALS = ('explore', 'combat', 'base', 'mounts')
# These levels are conservative assistance limits, not claims about spawn levels.
PAL_RULES = {
    'explore': (('PinkCat', 3, 'Transport'), ('SheepBall', 3, 'Handcraft')),
    'combat': (('Kitsunebi', 5, 'Fire'), ('Penguin', 5, 'Water'), ('PlantSlime', 5, 'Grass')),
    'base': (('Penguin', 5, 'Watering'), ('Kitsunebi', 5, 'EmitFlame'),
             ('PlantSlime', 5, 'Seeding'), ('PinkCat', 3, 'Mining')),
    'mounts': (('Alpaca', 5, 'land'), ('Boar', 6, 'land'), ('HawkBird', 15, 'air')),
}
# item, target stock, compatible weapons (empty means no weapon requirement).
ITEM_RULES = {
    'explore': (('PalSphere', 10, ()), ('PalSphere_Mega', 8, ()), ('PalSphere_Giga', 5, ())),
    'combat': (('Arrow', 20, ('WeakerBow', 'Bow_Triple', 'BowGun')),
               ('HandgunBullet', 30, ('HandGun_Default',))),
    'base': (), 'mounts': (),
}


class StaleRecommendation(ValueError):
    pass


def _item_name(key):
    names = DataProvider.get_item(key).get('I18n', {})
    return (names.get(Config.i18n) or names.get('en') or {}).get('Name', key)


def _legal_item(key):
    item = DataProvider.get_item(key)
    return bool(item and item.get('Legal') and not item.get('Disabled')
                and not item.get('MonsterOnly') and item.get('DynamicType') is None)


def _recipe(key, unlocked, level):
    return next((name for name, tech in TECH_DATA.items()
                 if name.casefold() in unlocked and key in tech.get('UnlockItems', [])
                 and tech.get('Level', 999) <= level and not tech.get('BossTechnology')), None)


def _owned(manager, player):
    return [r.pal for r in manager.pal_repository.records_for_owner(player.PlayerUId)
            if r.storage_kind == 'world' and not r.pal.IsHuman]


def _fingerprint(manager, player, goal, ceiling, row):
    # Do not trust client-provided species, amounts or stats. Rebuild this row on
    # apply and reject a changed preview, including after a save/player switch.
    payload = [manager.adventure_session_id, str(player.PlayerUId), goal, ceiling, row]
    return hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()


def recommendations(manager, player, goal='explore', ceiling=None):
    if goal not in GOALS:
        raise ValueError('Unknown assistance goal')
    if ceiling is not None and (type(ceiling) is not int or not 1 <= ceiling <= PalEntity.MAX_LEVEL):
        raise ValueError('Invalid assistance level ceiling')
    level = min(player.Level or 1, ceiling or PalEntity.MAX_LEVEL, PalEntity.MAX_LEVEL)
    unlocked = {name.casefold() for name in player.UnlockedRecipeTechnologyNames or []}
    owned = _owned(manager, player)
    species_owned = {DataProvider.resolve_pal_key(p.CharacterID) for p in owned}
    party_levels = [p.Level or 1 for p in owned if str(p.ContainerId) == str(player.OtomoCharacterContainerId)]
    # Without an active party, give a level-1 partner rather than deriving strength
    # from a Palbox that may already contain endgame-kit Pals.
    gift_level = max(1, min(level, int(median(party_levels)) if party_levels else 1, 20))
    inventory = manager.item_container_data.inventory_snapshot(player)
    bag = inventory['containers']['common']
    stock = {}
    for slot in bag['slots']:
        if slot['count'] > 0:
            stock[slot['static_id']] = stock.get(slot['static_id'], 0) + slot['count']
    weapons = {s['static_id'] for kind in ('weapons', 'common')
               for s in inventory['containers'][kind]['slots'] if s['count'] > 0}
    rows = []
    for item, target, compatible in ITEM_RULES[goal]:
        recipe = _recipe(item, unlocked, level)
        if not recipe or not _legal_item(item) or not bag['editable']:
            continue
        if compatible and not any(w == base or w in {f'{base}_{i}' for i in range(2, 6)}
                                  for w in weapons for base in compatible):
            continue
        held = stock.get(item, 0)
        rows.append({'id': f'item:{item}', 'kind': 'item', 'key': item,
                     'name': _item_name(item), 'owned': held, 'target': target,
                     'quantity': target - held, 'recipe': DataProvider.get_tech_name(recipe),
                     'reason': 'supplies', 'can_apply': True})
    # Only the highest available sphere tier is offered, not three supply grants.
    if goal == 'explore' and rows:
        rows = rows[-1:]
    rows = [row for row in rows if row['quantity'] > 0]
    pal_rows = []
    for species, minimum, role in PAL_RULES[goal]:
        data = PAL_DATA.get(species, {})
        if (level < minimum or data.get('Invalid', True) or data.get('VariantKind') != 'base'
                or not data.get('RegularlyObtainable')):
            continue
        record_id = DataProvider.get_pal_paldeck_record_id(species)
        captured = bool(record_id and player.get_pal_capture_count(record_id) > 0)
        existing = species in species_owned
        if not captured and not existing:
            continue  # Do not reveal undiscovered species.
        gear = f'SkillUnlock_{species}'
        # Existing save settlement unlocks a created Pal's partner technology.
        # Only offer additions whose technology is already unlocked, so this
        # assistance path cannot silently skip a technology gate on save.
        gear_ready = gear not in TECH_DATA or bool(_recipe(gear, unlocked, level))
        if goal == 'mounts' and not _recipe(gear, unlocked, level):
            continue
        if goal in ('base', 'explore'):
            if data.get('Suitabilities', {}).get(f'EPalWorkSuitability::{role}', 0) <= 0:
                continue
            covered = any(PAL_DATA.get(DataProvider.resolve_pal_key(p.CharacterID), {})
                          .get('Suitabilities', {}).get(f'EPalWorkSuitability::{role}', 0) > 0
                          for p in owned)
        else:
            covered = existing
        pal_rows.append({'id': f'pal:{species}', 'kind': 'pal', 'key': species,
                         'name': DataProvider.get_pal_i18n(species), 'role': role,
                         'level': gift_level, 'quantity': 1, 'owned': int(existing),
                         'reason': 'owned' if existing else 'covered' if covered else 'captured' if gear_ready else 'technology',
                         'can_apply': captured and not covered and gear_ready,
                         'required_tech': DataProvider.get_tech_name(gear) if not gear_ready else None,
                         'gear': DataProvider.get_tech_name(gear) if goal == 'mounts' else None})
    # Fill actual gaps before showing alternatives already available to the player.
    rows.extend(sorted(pal_rows, key=lambda row: not row['can_apply'])[:3])
    for row in rows:
        row['token'] = _fingerprint(manager, player, goal, ceiling, row)
    return {'level': player.Level or 1, 'effective_level': level,
            'tech_count': len(unlocked), 'owned_count': len(owned),
            'capture_data_available': player.PalCaptureCount is not None,
            'goal': goal, 'recommendations': rows}


def _item_plan(manager, player, row):
    data = manager.item_container_data
    _, native = data._container_for(player, 'common')
    if native is None:
        raise ValueError('Player backpack is unavailable')
    raw = [s['RawData']['value'] for s in data._slot_values(native)]
    indexes = [s['slot_index'] for s in raw]
    if len(set(indexes)) != len(indexes) or any(type(i) is not int or not 0 <= i < data._slot_num(native) for i in indexes):
        raise ValueError('Backpack has invalid slot indexes')
    slots = data.inventory_snapshot(player)['containers']['common']['slots']
    remaining = row['quantity']
    maximum = DataProvider.get_item(row['key'])['MaxStackCount']
    plan = []
    candidates = [s for s in slots if s['static_id'] == row['key'] and s['count'] > 0]
    candidates += [s for s in slots if not s['count']]
    for slot in candidates:
        if slot.get('warning'):
            raise ValueError('Backpack contains an unreadable item')
        addition = min(remaining, max(0, maximum - slot['count']))
        if addition:
            count = slot['count'] + addition
            data._validate_item('common', slot['slot_index'], row['key'], count, False)
            plan.append((slot['slot_index'], count))
            remaining -= addition
        if not remaining:
            break
    if remaining:
        raise ValueError('Not enough backpack space; nothing changed')
    return native, plan


def apply_recommendation(manager, player, goal, ceiling, recommendation_id, token):
    if not isinstance(recommendation_id, str) or not isinstance(token, str):
        raise ValueError('A recommendation and its preview token are required')
    current = recommendations(manager, player, goal, ceiling)
    row = next((r for r in current['recommendations'] if r['id'] == recommendation_id), None)
    if row is None or not row['can_apply'] or token != row['token']:
        raise StaleRecommendation('Recommendation changed; refresh and confirm again')
    touched = TouchedParents()
    data = manager.item_container_data
    before = set(manager.pal_repository.records())
    dynamics = list(data.dynamic_entries)
    if row['kind'] == 'item':
        native, plan = _item_plan(manager, player, row)
        touched.watch_dict(native)
    else:
        box = manager.container_data.get_container(player.PalStorageContainerId)
        group = manager.guild_data.get_group(player.group_id)
        if box is None or group is None:
            raise ValueError('Player Palbox or guild is unavailable')
        # The mutation service verifies ownership, container integrity and capacity.
        touched.watch_container(box)
        touched.watch_group(group)
    try:
        if row['kind'] == 'item':
            for index, count in plan:
                data.patch_slot(player, 'common', index, row['key'], count, allow_overstack=False)
        else:
            parameter = PalObjects.DefaultPalSaveParameter(player.PlayerUId, box.ID, 0)
            parameter['value']['CharacterID'] = PalObjects.NameProperty(row['key'])
            parameter['value']['EquipWaza']['value']['values'] = []
            for name in ('Talent_HP', 'Talent_Shot', 'Talent_Defense'):
                parameter['value'][name] = PalObjects.ByteProperty(0)
            record = manager.pal_mutations.create_world_pal(player.PlayerUId, parameter, box.ID)
            record.pal.Level = row['level']
            attacks = [a for a in DataProvider.get_attacks_to_learn(row['key'], row['level'])
                       if a in PAL_ATTACKS and not PAL_ATTACKS[a].get('Invalid')
                       and not PAL_ATTACKS[a].get('Disabled') and not PAL_ATTACKS[a].get('BossSkill')]
            record.pal.EquipWaza[:] = attacks[:3]
            record.pal.Hp = record.pal.ComputedMaxHP
    except Exception:
        for record in set(manager.pal_repository.records()) - before:
            manager.world_adapter.remove(record.native_record)
            manager.pal_repository.unregister(record)
        touched.restore()
        data.dynamic_entries[:] = dynamics
        data._rebuild_indexes()
        manager.storage_directory.invalidate()
        raise
    return {'kind': row['kind'], 'name': row['name'], 'quantity': row['quantity']}
