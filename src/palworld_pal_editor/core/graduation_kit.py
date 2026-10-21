"""Offline, additive endgame presets. All changes remain pending until Save Changes.

The nickname is an intentional, visible idempotency marker, scoped to the owner's
world Palbox. Renaming/moving a gift out of that box permits another copy.
"""
from palworld_pal_editor.core.pal_entity import PalEntity
from palworld_pal_editor.core.pal_mutations import TouchedParents
from palworld_pal_editor.core.pal_objects import PalObjects
from palworld_pal_editor.core.pal_storage_adapters import WorldPalAdapter
from palworld_pal_editor.utils.data_provider import DataProvider, PAL_ATTACKS, PAL_DATA, PAL_PASSIVES


COMBAT = ('IceHorse_Dark', 'BlueSkyDragon', 'JetDragon', 'ThunderDragonMan', 'PoseidonOrca',
          'IceHorse', 'BlackCentaur', 'SaintCentaur', 'DarkMechaDragon', 'NightLady_Dark',
          'KingBahamut_Dragon', 'SnowTigerBeastman', 'BlackGriffon', 'GhostDragon_Fire',
          'LegendDeer', 'WingGolem', 'FlowerPrince', 'Anubis', 'LilyQueen', 'Umihebi_Fire')
BASE = ('KabukiMan', 'BlueSkyDragon', 'FlowerPrince', 'ThunderDragonMan', 'MonochromeQueen',
        'JetDragon', 'WhiteDeer_Dark', 'DomeArmorDragon', 'Mothman', 'SnowTigerBeastman',
        'WingGolem_Fire', 'ChickenPal', 'CowPal', 'SoldierBee', 'LazyCatfish', 'WhiteMoth')
MOUNTS = ('JetDragon', 'GhostDragon_Fire', 'DarkMechaDragon', 'BlackCentaur', 'PoseidonOrca')
GROUPS = {'combat': COMBAT, 'base': BASE, 'mounts': MOUNTS}
PASSIVES = {
    'combat': ('Legend', 'PAL_ALLAttack_up3', 'CoolTimeReduction_Up_1', 'MutationPal_Immortal'),
    'base': ('CraftSpeed_up3', 'CraftSpeed_up2', 'PAL_CorporateSlave', 'CraftSpeed_up1'),
    'mounts': ('Legend', 'MoveSpeed_up_3', 'Stamina_Up_3', 'Stamina_Up_1'),
}
EQUIPMENT = ('AncientHelmet_5', 'AncientArmorWeight_5', 'Shield_07', 'SkyBow_5',
             'BeamLauncher_5', 'ElectricArcAssaultRifle_5', 'WingGlider', 'SphereModule_Homing',
             'Accessory_AT_1', 'Accessory_HP_1', 'Accessory_AirDash3', 'Accessory_JumpAir_2')
SUPPLIES = (('ElectricArcAssaultRifleBullet', 300), ('BeamLauncherBullet', 100), ('SkyBowArrow', 100),
            ('WingGlider_Fuel', 100), ('PalSphere_Ancient_2', 100), ('Potion_Extreme', 20),
            ('Salad', 20), ('Money', 10000), ('Wood', 20), ('Stone', 10), ('CopperIngot', 10))


def definition(preset='all'):
    if preset not in (*GROUPS, 'core', 'all'):
        raise ValueError('Unknown graduation preset')
    groups = GROUPS if preset == 'all' else {'combat': COMBAT[:5]} if preset == 'core' else {preset: GROUPS[preset]}
    return [(role, species) for role, species_list in groups.items() for species in species_list]


def marker(role, species):
    return f'Graduation-{role}-{species}'


def catalog():
    return {preset: [{'role': role, 'species': species, 'name': DataProvider.get_pal_i18n(species)}
                     for role, species in definition(preset)]
            for preset in ('all', 'core', *GROUPS)}


def _plan(manager, player, preset):
    entries = definition(preset)
    container = manager.container_data.get_container(player.PalStorageContainerId)
    if container is None:
        raise ValueError('Player world Palbox is missing')
    descriptor = manager.storage_directory.descriptor(container.ID)
    if descriptor is None or not descriptor.movable_into or str(descriptor.owner_player_uid) != str(player.PlayerUId):
        raise ValueError('Player world Palbox ownership could not be verified')
    group = manager.guild_data.get_group(player.group_id)
    if group is None:
        raise ValueError('Player guild is missing')
    indexes = [slot.SlotIndex for slot in container.slots]
    if len(set(indexes)) != len(indexes) or any(type(i) is not int or not 0 <= i < container.SlotNum for i in indexes):
        raise ValueError('Palbox has invalid slot indexes')
    records = manager.pal_repository.records_for_storage(WorldPalAdapter.storage_key(container.ID))
    existing = {(r.pal.CharacterID, r.pal.NickName) for r in records
                if r.storage_kind == 'world' and str(r.pal.OwnerPlayerUId) == str(player.PlayerUId)}
    missing = [(role, species) for role, species in entries if (species, marker(role, species)) not in existing]
    free = container.SlotNum - len(container.slots)
    if free < len(missing):
        raise ValueError(f'Not enough world Palbox slots: need {len(missing)}, available {free}; nothing changed')
    for role, species in entries:
        if species not in PAL_DATA or PAL_DATA[species].get('Invalid') or PAL_DATA[species].get('VariantKind') != 'base':
            raise ValueError(f'Unsupported normal Pal: {species}')
        if any(p not in PAL_PASSIVES for p in PASSIVES[role]):
            raise ValueError('Preset passive is absent from the bundled catalog')
        if not _attacks(species):
            raise ValueError(f'No supported natural attacks: {species}')
    items = DataProvider.get_item_data()
    gear = [(f'SkillUnlock_{species}', 1) for _, species in entries
            if f'SkillUnlock_{species}' in items]
    batches = [('common', [(i, 1) for i in EQUIPMENT] + list(SUPPLIES)), ('key_items', list(dict.fromkeys(gear)))]
    # Check every container before creating even one Pal or item.
    for kind, requested in batches:
        manager.item_container_data.add_missing_items(player, kind, requested, dry_run=True)
    return container, group, entries, missing, batches


def _attacks(species):
    return [attack for attack in DataProvider.get_attacks_to_learn(species, PalEntity.MAX_LEVEL)
            if attack in PAL_ATTACKS and not PAL_ATTACKS[attack].get('Invalid')
            and not PAL_ATTACKS[attack].get('Disabled') and not PAL_ATTACKS[attack].get('BossSkill')]


def add_kit(manager, player, preset='all'):
    container, group, entries, missing, batches = _plan(manager, player, preset)
    touched = TouchedParents()
    touched.watch_container(container)
    touched.watch_group(group)
    data = manager.item_container_data
    for kind, _ in batches:
        _, native = data._container_for(player, kind)
        touched.watch_dict(native)
    original_dynamics = list(data.dynamic_entries)
    before_records = set(manager.pal_repository.records())
    try:
        for role, species in missing:
            parameter = PalObjects.DefaultPalSaveParameter(player.PlayerUId, container.ID, 0)
            parameter['value']['CharacterID'] = PalObjects.NameProperty(species)
            parameter['value']['EquipWaza']['value']['values'] = []
            record = manager.pal_mutations.create_world_pal(player.PlayerUId, parameter, container.ID)
            pal = record.pal
            pal.NickName = marker(role, species)
            pal.maximize_progression()
            pal.replace_PassiveSkillList(list(PASSIVES[role]))
            attacks = _attacks(species)
            for attack in attacks:
                pal.add_MasteredWaza(attack)
            pal.EquipWaza[:] = sorted(attacks, key=lambda a: (-PAL_ATTACKS[a].get('Power', 0), a))[:3]
            pal.Hp = pal.ComputedMaxHP
        results = [data.add_missing_items(player, kind, requested) for kind, requested in batches]
    except Exception:
        # Includes a failure immediately after registration, not just returned records.
        for record in set(manager.pal_repository.records()) - before_records:
            manager.world_adapter.remove(record.native_record)
            manager.pal_repository.unregister(record)
        touched.restore()
        data.dynamic_entries[:] = original_dynamics
        data._rebuild_indexes()
        manager.storage_directory.invalidate()
        raise
    return {'pals_added': len(missing), 'pals_skipped': len(entries) - len(missing),
            'items_added': sum(r['added'] for r in results), 'items_skipped': sum(r['skipped'] for r in results)}
