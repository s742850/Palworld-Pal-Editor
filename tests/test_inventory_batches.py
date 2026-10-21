import copy
import threading
from types import SimpleNamespace

import pytest
from flask_jwt_extended import create_access_token

from palworld_pal_editor.core.item_container_data import ItemContainerData
from palworld_pal_editor.utils.data_provider import DataProvider
from palworld_pal_editor.webui import app


def inventory(size=230):
    cid = '11111111-1111-1111-1111-111111111111'
    entry = {'key': {'ID': {'value': cid}}, 'value': {
        'SlotNum': {'value': size}, 'Slots': {'value': {'values': []}}}}
    world = {'ItemContainerSaveData': {'value': [entry]},
             'DynamicItemSaveData': {'value': {'values': []}}}
    data = ItemContainerData(SimpleNamespace(properties={'worldSaveData': {'value': world}}))
    player = SimpleNamespace(InventoryContainerIds={'key_items': cid, 'common': cid})
    return data, player


def test_add_all_gear_is_complete_and_idempotent_without_replacing_items():
    data, player = inventory()
    first = data.patch_slot(player, 'key_items', 0, 'Lantern', 1, allow_overstack=False)
    result = data.add_all_pal_gear(player)
    expected = {i['InternalName'] for i in DataProvider.get_item_data().values()
                if i['TypeB'] == 'Essential_PalGear' and i['Legal'] and not i['Disabled'] and not i['MonsterOnly']}
    snapshot = data.inventory_snapshot(player)['containers']['key_items']['slots']
    assert {s['static_id'] for s in snapshot if s['count']} == expected | {'Lantern'}
    assert snapshot[0] == first
    before = copy.deepcopy(data.container_entries)
    assert data.add_all_pal_gear(player)['added'] == 0
    assert data.container_entries == before
    assert result['added'] == len(expected)
    assert not data.dynamic_entries


def test_insufficient_capacity_and_invalid_batch_do_not_partially_apply():
    data, player = inventory(2)
    before = copy.deepcopy(data.container_entries)
    with pytest.raises(ValueError, match='Not enough empty slots'):
        data.add_all_pal_gear(player)
    assert data.container_entries == before
    with pytest.raises(ValueError, match='Unknown item'):
        data.add_missing_items(player, 'common', [('Wood', 5), ('nonexistent', 1)])
    assert data.container_entries == before


def test_batch_api_requires_auth_and_returns_inventory(monkeypatch):
    from palworld_pal_editor.api import players
    data, player = inventory()
    monkeypatch.setattr(players, 'SaveManager', lambda: SimpleNamespace(
        session_lock=threading.RLock(), item_container_data=data))
    monkeypatch.setattr(players, 'require_player', lambda _: player)
    app.config['JWT_SECRET_KEY'] = 'test-secret-key-with-at-least-32-bytes'
    with app.app_context():
        token = create_access_token(identity='test')
    client = app.test_client()
    route = '/api/players/test/inventory/pal-gear'
    assert client.post(route).status_code == 401
    response = client.post(route, headers={'Authorization': f'Bearer {token}'})
    assert response.status_code == 200
    assert response.json['result']['added'] > 100
    assert response.json['inventory']['containers']['key_items']['slots']
