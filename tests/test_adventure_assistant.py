"""Assistance must be opt-in, bounded, stale-safe and reversible on failure."""
import copy
import shutil
from pathlib import Path

import pytest
from flask_jwt_extended import create_access_token

from palworld_pal_editor.config import Config
from palworld_pal_editor.core.adventure_assistant import (
    recommendations, apply_recommendation, StaleRecommendation, PAL_RULES, ITEM_RULES,
)
from palworld_pal_editor.core.map_progress import HOST_UID
from palworld_pal_editor.core.save_manager import SaveManager
from palworld_pal_editor.utils.data_provider import PAL_DATA, DataProvider


@pytest.fixture
def world(tmp_path, monkeypatch):
    monkeypatch.setattr(Config, 'i18n', 'en')
    monkeypatch.setattr(SaveManager, '_instance', None)
    source = tmp_path / 'source'
    shutil.copytree(Path(__file__).parent / 'saves/1.0/8C439FF04713B5F986F9CAB485575089', source)
    manager = SaveManager()
    assert manager.open(str(source))
    player = manager.get_player(HOST_UID)
    player.Level = 15
    for name in list(player.UnlockedRecipeTechnologyNames or []):
        player.toggle_UnlockedRecipeTechnologyNames(name, False)
    player.toggle_UnlockedRecipeTechnologyNames('Special_PalSphere_Grade_01', True)
    data = manager.item_container_data
    for slot in data.inventory_snapshot(player)['containers']['common']['slots']:
        if slot['count']:
            data.patch_slot(player, 'common', slot['slot_index'], None, 0, allow_overstack=False)
    data.patch_slot(player, 'common', 0, 'PalSphere', 3, allow_overstack=False)
    return manager, player


def state(manager, player):
    return copy.deepcopy((manager.item_container_data.container_entries,
                          manager.item_container_data.dynamic_entries,
                          [r.native_record for r in manager.pal_repository.records()],
                          manager.container_data.get_container(player.PalStorageContainerId).snapshot_slots(),
                          manager.guild_data.get_group(player.group_id).snapshot_handles(),
                          player._player_save_data))


def apply(manager, player, row, goal='explore', ceiling=None):
    return apply_recommendation(manager, player, goal, ceiling, row['id'], row['token'])


def item_row(manager, player):
    return next(r for r in recommendations(manager, player)['recommendations'] if r['kind'] == 'item')


def missing_pal(world, monkeypatch):
    manager, player = world
    # Arrange a known capture, but no currently owned workers. Restrict the owner
    # query rather than deleting fixture records and touching unrelated guilds.
    monkeypatch.setattr(manager.pal_repository, 'records_for_owner', lambda uid: [])
    player.try_create_pal_record_data()
    player.PalCaptureCount[:] = [{'key': 'Penguin', 'value': 1}]
    player.Level = 20
    player.toggle_UnlockedRecipeTechnologyNames('SkillUnlock_Penguin', True)
    row = next(r for r in recommendations(manager, player, 'base')['recommendations'] if r['can_apply'])
    return row


def test_rules_are_supported_normal_catalog_entries():
    for rules in PAL_RULES.values():
        for species, _, _ in rules:
            assert not PAL_DATA[species]['Invalid']
            assert PAL_DATA[species]['RegularlyObtainable']
            assert PAL_DATA[species]['VariantKind'] == 'base'
    for rules in ITEM_RULES.values():
        for item, count, weapons in rules:
            data = DataProvider.get_item(item)
            assert data['Legal'] and not data['Disabled'] and not data['MonsterOnly']
            assert count <= data['MaxStackCount']
            assert any(item in t.get('UnlockItems', []) for t in DataProvider.get_tech_data().values())
            for weapon in weapons:
                assert DataProvider.get_item(weapon), weapon


def test_read_is_pure_and_level_does_not_unlock_recipes(world):
    manager, player = world
    before = state(manager, player)
    row = item_row(manager, player)
    assert row['owned'] == 3 and row['quantity'] == 7 and row['target'] == 10
    assert state(manager, player) == before
    player.Level = 80
    rows = recommendations(manager, player)['recommendations']
    assert [r['key'] for r in rows if r['kind'] == 'item'] == ['PalSphere']
    assert not [r for r in recommendations(manager, player, ceiling=1)['recommendations'] if r['kind'] == 'item']


def test_unknown_captures_do_not_reveal_species(world, monkeypatch):
    manager, player = world
    monkeypatch.setattr(manager.pal_repository, 'records_for_owner', lambda uid: [])
    player.PalCaptureCount[:] = []
    assert recommendations(manager, player, 'base')['recommendations'] == []


def test_addition_cannot_unlock_partner_technology_on_save(world, monkeypatch):
    manager, player = world
    missing_pal(world, monkeypatch)
    player.toggle_UnlockedRecipeTechnologyNames('SkillUnlock_Penguin', False)
    row = recommendations(manager, player, 'base')['recommendations'][0]
    assert row['reason'] == 'technology' and not row['can_apply']
    before = state(manager, player)
    with pytest.raises(StaleRecommendation):
        apply(manager, player, row, 'base')
    assert state(manager, player) == before


def test_full_higher_tier_does_not_offer_lower_tier_stock(world):
    manager, player = world
    player.toggle_UnlockedRecipeTechnologyNames('Special_PalSphere_Grade_02', True)
    manager.item_container_data.patch_slot(player, 'common', 1, 'PalSphere_Mega', 8, allow_overstack=False)
    assert not [r for r in recommendations(manager, player)['recommendations'] if r['kind'] == 'item']


def test_mount_requires_saddle_technology_and_ammo_requires_matching_weapon(world, monkeypatch):
    manager, player = world
    monkeypatch.setattr(manager.pal_repository, 'records_for_owner', lambda uid: [])
    player.PalCaptureCount[:] = [{'key': species, 'value': 1}
                                for species in ('Alpaca', 'Boar', 'HawkBird')]
    assert recommendations(manager, player, 'mounts')['recommendations'] == []
    player.toggle_UnlockedRecipeTechnologyNames('SkillUnlock_HawkBird', True)
    assert [r['key'] for r in recommendations(manager, player, 'mounts')['recommendations']] == ['HawkBird']
    player.toggle_UnlockedRecipeTechnologyNames('Arrow', True)
    data = manager.item_container_data
    for slot in data.inventory_snapshot(player)['containers']['weapons']['slots']:
        if slot['count']:
            data.patch_slot(player, 'weapons', slot['slot_index'], None, 0, allow_overstack=False)
    assert not [r for r in recommendations(manager, player, 'combat')['recommendations'] if r['kind'] == 'item']
    data.patch_slot(player, 'common', 1, 'WeakerBow', 1, allow_overstack=False)
    assert [r['key'] for r in recommendations(manager, player, 'combat')['recommendations'] if r['kind'] == 'item'] == ['Arrow']


def test_item_topup_counts_all_stacks_and_preserves_other_items(world, tmp_path):
    manager, player = world
    data = manager.item_container_data
    data.patch_slot(player, 'common', 1, 'PalSphere', 2, allow_overstack=False)
    data.patch_slot(player, 'common', 2, 'Wood', 17, allow_overstack=False)
    row = item_row(manager, player)
    assert row['quantity'] == 5
    assert apply(manager, player, row)['quantity'] == 5
    slots = data.inventory_snapshot(player)['containers']['common']['slots']
    assert sum(s['count'] for s in slots if s['static_id'] == 'PalSphere') == 10
    assert slots[2]['static_id'] == 'Wood' and slots[2]['count'] == 17
    with pytest.raises(StaleRecommendation):
        apply(manager, player, row)
    output = tmp_path / 'output'
    assert manager.save(str(output))
    assert manager.open(str(output))
    assert not [r for r in recommendations(manager, manager.get_player(HOST_UID))['recommendations'] if r['kind'] == 'item']


def test_changed_stock_or_ceiling_requires_new_confirmation(world):
    manager, player = world
    row = item_row(manager, player)
    manager.item_container_data.patch_slot(player, 'common', 0, 'PalSphere', 4, allow_overstack=False)
    before = state(manager, player)
    with pytest.raises(StaleRecommendation):
        apply(manager, player, row)
    with pytest.raises(StaleRecommendation):
        apply(manager, player, item_row(manager, player), ceiling=10)
    assert state(manager, player) == before


def test_item_failure_restores_original_stack(world, monkeypatch):
    manager, player = world
    row = item_row(manager, player)
    before = state(manager, player)
    patch = manager.item_container_data.patch_slot
    def fail(*args, **kwargs):
        patch(*args, **kwargs)
        raise RuntimeError('injected after write')
    monkeypatch.setattr(manager.item_container_data, 'patch_slot', fail)
    with pytest.raises(RuntimeError):
        apply(manager, player, row)
    assert state(manager, player) == before


def test_full_backpack_can_top_up_existing_stack_but_never_overwrites(world):
    manager, player = world
    data = manager.item_container_data
    for slot in data.inventory_snapshot(player)['containers']['common']['slots'][1:]:
        data.patch_slot(player, 'common', slot['slot_index'], 'Wood', 1, allow_overstack=False)
    assert apply(manager, player, item_row(manager, player))['quantity'] == 7
    data.patch_slot(player, 'common', 0, 'Wood', 1, allow_overstack=False)
    row = item_row(manager, player)
    before = state(manager, player)
    with pytest.raises(ValueError, match='Not enough backpack space'):
        apply(manager, player, row)
    assert state(manager, player) == before


def test_pal_is_ordinary_and_roundtrips(world, monkeypatch, tmp_path):
    manager, player = world
    row = missing_pal(world, monkeypatch)
    assert row['level'] == 1
    before = {r.record_key: copy.deepcopy(r.native_record) for r in manager.pal_repository.records()}
    apply(manager, player, row, 'base')
    created = manager.pal_repository.created_records()
    assert len(created) == 1
    pal = created[0].pal
    assert pal.CharacterID == 'Penguin' and pal.Level == 1
    assert (pal.Talent_HP, pal.Talent_Shot, pal.Talent_Defense) == (0, 0, 0)
    assert (pal.Rank or 1) == 1 and not pal.PassiveSkillList
    assert pal.EquipWaza and set(pal.EquipWaza) <= set(pal.MasteredWaza)
    technologies = list(player.UnlockedRecipeTechnologyNames)
    assert all(manager.get_record(k).native_record == v for k, v in before.items())
    # Restore normal owner lookup so save settlement sees the new Pal.
    monkeypatch.undo()
    output = tmp_path / 'ordinary'
    assert manager.save(str(output))
    assert manager.open(str(output))
    restored = [r.pal for r in manager.pal_repository.records() if r.pal.InstanceId == pal.InstanceId]
    assert len(restored) == 1 and restored[0].Level == 1
    assert restored[0].Talent_HP == 0
    assert manager.get_player(HOST_UID).get_pal_capture_count('penguin') == 2
    assert manager.get_player(HOST_UID).UnlockedRecipeTechnologyNames == technologies
    assert not [r for r in recommendations(manager, manager.get_player(HOST_UID), 'base')['recommendations']
                if r['key'] == 'Penguin' and r['can_apply']]


def test_pal_capacity_and_post_registration_failure_are_atomic(world, monkeypatch):
    manager, player = world
    row = missing_pal(world, monkeypatch)
    box = manager.container_data.get_container(player.PalStorageContainerId)
    size = box.SlotNum
    box.SlotNum = len(box.slots)
    before = state(manager, player)
    with pytest.raises(ValueError):
        apply(manager, player, row, 'base')
    assert state(manager, player) == before
    box.SlotNum = size
    before = state(manager, player)
    create = manager.pal_mutations.create_world_pal
    def fail(*args, **kwargs):
        create(*args, **kwargs)
        raise RuntimeError('injected after registration')
    monkeypatch.setattr(manager.pal_mutations, 'create_world_pal', fail)
    with pytest.raises(RuntimeError):
        apply(manager, player, row, 'base')
    assert state(manager, player) == before
    assert not manager.pal_repository.created_records()


def test_api_auth_preview_apply_and_stale_load(world):
    from palworld_pal_editor.webui import app
    manager, player = world
    app.config['JWT_SECRET_KEY'] = 'test-adventure-secret-at-least-32-bytes'
    with app.app_context():
        token = create_access_token(identity='test', expires_delta=False)
    client = app.test_client()
    path = f'/api/players/{HOST_UID}/adventure'
    headers = {'Authorization': f'Bearer {token}'}
    before = state(manager, player)
    assert client.get(path).status_code == 401
    assert client.post(path, json={}).status_code == 401
    rows = client.get(path, headers=headers).get_json()['recommendations']
    assert state(manager, player) == before
    row = next(r for r in rows if r['kind'] == 'item')
    payload = dict(goal='explore', ceiling=None, recommendationId=row['id'], token=row['token'])
    assert client.post(path, json={**payload, 'quantity': 999}, headers=headers).status_code == 400
    assert client.post(path, json=payload, headers=headers).status_code == 200
    assert client.post(path, json=payload, headers=headers).status_code == 409
    assert client.get(path + '?ceiling=oops', headers=headers).status_code == 400
    # Same player, same path, freshly loaded data must not accept an old preview.
    assert manager.open(str(manager.file_path))
    assert client.post(path, json=payload, headers=headers).status_code == 409
