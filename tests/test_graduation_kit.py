import copy
import shutil
from pathlib import Path

import pytest
from flask_jwt_extended import create_access_token

from palworld_pal_editor.config import Config
from palworld_pal_editor.core.graduation_kit import (
    add_kit,
    definition,
    marker,
    PASSIVES,
    EQUIPMENT,
    MOUNTS,
    ROLE_LABELS,
)
from palworld_pal_editor.utils.data_provider import PAL_DATA, I18N_LIST
from palworld_pal_editor.core.map_progress import HOST_UID
from palworld_pal_editor.core.save_manager import SaveManager

FIXTURE = Path(__file__).parent / 'saves/1.0/8C439FF04713B5F986F9CAB485575089'


@pytest.fixture
def world(tmp_path, monkeypatch):
    monkeypatch.setattr(Config, 'i18n', 'en')
    monkeypatch.setattr(SaveManager, '_instance', None)
    manager = SaveManager()
    source = tmp_path / 'source'
    shutil.copytree(FIXTURE, source)
    assert manager.open(str(source))
    player = manager.get_player(HOST_UID)
    # The tracked fixture has an almost-full backpack. Make room in this temporary
    # copy while retaining one occupied slot to exercise preservation.
    data = manager.item_container_data
    for kind in ('common', 'key_items'):
        occupied = [s for s in data.inventory_snapshot(player)['containers'][kind]['slots'] if s['count']]
        for slot in occupied[1:]:
            data.patch_slot(player, kind, slot['slot_index'], None, 0, allow_overstack=False)
    return manager, player


def state(manager, player):
    box = manager.container_data.get_container(player.PalStorageContainerId)
    group = manager.guild_data.get_group(player.group_id)
    return (len(manager.pal_repository), box.snapshot_slots(), group.snapshot_handles(),
            copy.deepcopy(manager.item_container_data.container_entries),
            copy.deepcopy(manager.item_container_data.dynamic_entries),
            set(manager.pal_repository.created_records()))


@pytest.mark.parametrize('locale', I18N_LIST)
def test_nickname_localizes_species_and_distinguishes_roles(locale, monkeypatch):
    monkeypatch.setattr(Config, 'i18n', locale)
    names = [marker(role, 'JetDragon') for role in ('combat', 'base', 'mounts')]
    assert len(set(names)) == 3
    for name, suffix in zip(names, ROLE_LABELS[locale]):
        assert name == f"{PAL_DATA['JetDragon']['I18n'][locale]}－{suffix}"


def test_reapply_migrates_legacy_and_other_languages_without_duplicates(world, monkeypatch, tmp_path):
    manager, player = world
    add_kit(manager, player)
    gifts = list(manager.pal_repository.created_records())
    roles = {marker(role, species): role for role, species in definition()}
    expected = {}
    for index, record in enumerate(gifts):
        pal = record.pal
        role = roles[pal.NickName]
        expected[record.record_key] = marker(role, pal.CharacterID, 'zh-TW')
        if index % 2:
            pal.NickName = f'Graduation-{role}-{pal.CharacterID}'
    # A user-renamed gift remains untouched.
    custom = gifts[0]
    custom.pal.NickName = 'My own nickname'
    expected[custom.record_key] = custom.pal.NickName
    monkeypatch.setattr(Config, 'i18n', 'zh-TW')
    result = add_kit(manager, player)
    assert result['pals_added'] == 1  # Only the deliberately renamed gift permits another copy.
    assert all(manager.get_record(key).pal.NickName == name for key, name in expected.items())
    assert add_kit(manager, player)['pals_added'] == 0
    output = tmp_path / 'localized'
    manager.save(str(output))
    assert manager.open(str(output))
    assert add_kit(manager, manager.get_player(HOST_UID))['pals_added'] == 0
    monkeypatch.setattr(Config, 'i18n', 'ja')
    assert add_kit(manager, manager.get_player(HOST_UID))['pals_added'] == 0


def test_renaming_existing_gifts_rolls_back_on_item_failure(world, monkeypatch):
    manager, player = world
    add_kit(manager, player, 'core')
    original = {r.record_key: copy.deepcopy(r.native_record) for r in manager.pal_repository.records()}
    monkeypatch.setattr(Config, 'i18n', 'zh-TW')
    data = manager.item_container_data
    add_items = data.add_missing_items
    def interrupted(*args, **kwargs):
        if not kwargs.get('dry_run'):
            raise ValueError('injected item failure')
        return add_items(*args, **kwargs)
    monkeypatch.setattr(data, 'add_missing_items', interrupted)
    with pytest.raises(ValueError, match='injected item failure'):
        add_kit(manager, player, 'core')
    assert all(manager.get_record(key).native_record == value for key, value in original.items())


def test_complete_kit_preserves_existing_and_roundtrips(world, tmp_path):
    manager, player = world
    original = {r.record_key: copy.deepcopy(r.native_record) for r in manager.pal_repository.records()}
    level = player.Level
    result = add_kit(manager, player, 'all')
    assert result['pals_added'] == 41
    created = list(manager.pal_repository.created_records())
    assert len(created) == 41
    expected = {(species, marker(role, species)): role for role, species in definition()}
    for record in created:
        pal = record.pal
        role = expected[(pal.CharacterID, pal.NickName)]
        assert record.storage_kind == 'world'
        assert str(pal.OwnerPlayerUId) == str(player.PlayerUId)
        assert pal.Level == pal.MAX_LEVEL
        assert pal.Rank == pal.MAX_CONDENSATION_RANK
        assert pal.FriendshipLevel == pal.MAX_FRIENDSHIP_LEVEL
        assert (pal.Talent_HP, pal.Talent_Shot, pal.Talent_Defense) == (100, 100, 100)
        assert (pal.Rank_HP, pal.Rank_Attack, pal.Rank_Defence, pal.Rank_CraftSpeed) == (20, 20, 20, 20)
        assert pal.PassiveSkillList == list(PASSIVES[role])
        assert len(pal.EquipWaza) == 3
        assert set(pal.EquipWaza) <= set(pal.MasteredWaza)
        assert pal.Hp == pal.ComputedMaxHP
    assert player.Level == level
    assert all(manager.get_record(key).native_record == value for key, value in original.items())
    before = state(manager, player)
    assert add_kit(manager, player)['pals_added'] == 0
    assert state(manager, player) == before
    snapshot = manager.item_container_data.inventory_snapshot(player)
    assert set(EQUIPMENT) <= {s['static_id'] for s in snapshot['containers']['common']['slots']}
    output = tmp_path / 'output'
    manager.save(str(output))
    assert manager.open(str(output))
    player = manager.get_player(HOST_UID)
    assert player.Level == level
    gifts = [r for r in manager.pal_repository.records() if (r.pal.CharacterID, r.pal.NickName) in expected]
    assert len(gifts) == 41
    assert all(r.pal.Level == r.pal.MAX_LEVEL and len(r.pal.PassiveSkillList) == 4 for r in gifts)
    assert add_kit(manager, player)['pals_added'] == 0


def test_capacity_checks_refuse_entire_batch(world):
    manager, player = world
    box = manager.container_data.get_container(player.PalStorageContainerId)
    box.SlotNum = len(box.slots)
    before = state(manager, player)
    with pytest.raises(ValueError, match='Not enough world Palbox slots'):
        add_kit(manager, player)
    assert state(manager, player) == before


def test_backpack_capacity_refuses_before_creating_pals(world):
    manager, player = world
    data = manager.item_container_data
    _, bag = data._container_for(player, 'common')
    size = data._slot_num(bag)
    occupied = {s['slot_index'] for s in data.inventory_snapshot(player)['containers']['common']['slots'] if s['count']}
    for index in range(size):
        if index not in occupied:
            data.patch_slot(player, 'common', index, 'Wood', 1, allow_overstack=False)
    before = state(manager, player)
    with pytest.raises(ValueError, match='Not enough empty slots'):
        add_kit(manager, player)
    assert state(manager, player) == before


def test_mount_kit_does_not_require_space_for_combat_supplies(world):
    manager, player = world
    data = manager.item_container_data
    _, bag = data._container_for(player, 'common')
    size = data._slot_num(bag)
    occupied = {s['slot_index'] for s in data.inventory_snapshot(player)['containers']['common']['slots'] if s['count']}
    for index in range(size):
        if index not in occupied:
            data.patch_slot(player, 'common', index, 'Wood', 1, allow_overstack=False)
    common_before = copy.deepcopy(data._slot_values(bag))

    result = add_kit(manager, player, 'mounts')

    assert result['pals_added'] == len(MOUNTS)
    assert data._slot_values(bag) == common_before
    key_items = {slot['static_id'] for slot in data.inventory_snapshot(player)['containers']['key_items']['slots']}
    assert {f'SkillUnlock_{species}' for species in MOUNTS} <= key_items


def test_mid_batch_failure_restores_palbox_guild_records_and_items(world, monkeypatch):
    manager, player = world
    original = manager.pal_mutations.create_world_pal
    before = state(manager, player)
    calls = []
    def interrupted(*args, **kwargs):
        record = original(*args, **kwargs)
        calls.append(record)
        if len(calls) == 2:
            raise ValueError('injected failure after registration')
        return record
    monkeypatch.setattr(manager.pal_mutations, 'create_world_pal', interrupted)
    with pytest.raises(ValueError, match='injected failure'):
        add_kit(manager, player, 'core')
    assert state(manager, player) == before


def test_item_write_failure_restores_already_created_pals_and_dynamic_items(world, monkeypatch):
    manager, player = world
    data = manager.item_container_data
    original = data.add_missing_items
    before = state(manager, player)
    def interrupted(p, kind, requested, **kwargs):
        result = original(p, kind, requested, **kwargs)
        if not kwargs.get('dry_run') and kind == 'key_items':
            raise ValueError('injected item failure')
        return result
    monkeypatch.setattr(data, 'add_missing_items', interrupted)
    with pytest.raises(ValueError, match='injected item failure'):
        add_kit(manager, player, 'core')
    assert state(manager, player) == before


def test_api_is_authenticated_validates_preset_and_does_not_save(world, monkeypatch):
    from palworld_pal_editor.api import players
    from palworld_pal_editor.webui import app
    manager, player = world
    monkeypatch.setattr(players, 'SaveManager', lambda: manager)
    monkeypatch.setattr(players, 'require_player', lambda _: player)
    monkeypatch.setattr(manager, 'save', lambda *_: pytest.fail('API must not auto-save'))
    app.config['JWT_SECRET_KEY'] = 'test-secret-key-with-at-least-32-bytes'
    with app.app_context():
        token = create_access_token(identity='test')
    client = app.test_client()
    route = '/api/players/test/graduation-kit'
    headers = {'Authorization': f'Bearer {token}'}
    assert client.get(route).status_code == 401
    assert client.post(route, json={'preset': 'all'}).status_code == 401
    reply = client.get(route, headers=headers)
    assert len(reply.json['presets']['all']) == 41
    before = state(manager, player)
    assert client.post(route, headers=headers, json={}).status_code == 400
    assert client.post(route, headers=headers, json={'preset': '../../bad'}).status_code == 400
    assert state(manager, player) == before
    reply = client.post(route, headers=headers, json={'preset': 'core'})
    assert reply.status_code == 200, reply.json
    assert reply.json['result']['pals_added'] == 5
