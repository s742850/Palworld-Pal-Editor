# 畢業套組 / Endgame kit

查閱與實作日期 / Reviewed and implemented: 2026-10-21。

## 使用 / Usage

關閉遊戲，先備份，再用 `start-local.cmd` 啟動。開啟 **TEST** 世界並選玩家，進入「畢業套組」，選核心 5 隻、戰鬥 20 隻、基地 16 隻、坐騎 5 隻，或完整 41 隻；按「一鍵新增所選畢業套組」。檢查新增名單和背包後按「儲存變更」，關閉修改器，再由使用者登入 TEST 驗收。

Close the game and back up first. Start with `start-local.cmd`, open TEST, select the player, then use Endgame kit. Choose core 5, combat 20, workers 16, mounts 5, or all 41. Review the pending Pals/inventory, Save Changes, close the editor, and test in-game yourself.

- 帕魯加入所選玩家的**本世界帕魯終端**，不塞進隊伍、基地或跨界終端。工人需自行派駐，坐騎需自行編入隊伍。完整／戰鬥／核心戰鬥套組的新裝備放背包，不覆蓋現有穿戴裝備；基地與坐騎套組不要求一般背包空格，只加入對應的重要物品。不同用途同種帕魯是不同個體，故 41 隻不是 41 個不同物種。
- Pals land in the selected player's world Palbox. Assign workers and party mounts yourself. Complete, combat, and core-combat presets put equipment in the backpack while preserving worn gear. Worker and mount presets do not require common-backpack space and add only matching Key Items. The same species may appear as separate individuals for different roles; 41 Pals does not mean 41 distinct species.
- 只加入缺少的物品，已有堆疊保留原數量。暱稱依目前介面語言使用「物種名稱－用途」，例如「空渦龍－戰鬥／基地／坐騎」。再次套用會辨識所有支援語言的預設暱稱及舊版 `Graduation-用途-物種ID`，並更新為目前語言，不因語言切換重複新增；只處理所選套組、此玩家終端內的個體。自行改名、移出終端或刪除後，再按可能新增另一隻。原有未標記帕魯不會被強化或取代。
- Missing item IDs are added once; existing stacks retain their counts. Nicknames use the selected interface language and a role suffix, e.g. `Jetragon－Combat`, `Jetragon－Base`, or `Jetragon－Mount`. Reapplying recognizes default names in every supported language and legacy `Graduation-role-species` names, updating matching gifts to the current language without duplicates. This only affects the selected preset in this player's Palbox. Custom renaming, moving or deleting a gift permits another copy. Existing unmarked Pals are preserved.
- 預先檢查所有帕魯及物品空格；不足則整批拒絕。中途例外會還原本批內容。API 不自動存檔；真正存檔使用既有備份及回滾流程。
- Every target is checked before mutation. Insufficient space rejects the entire batch; unexpected failures roll it back. The API never auto-saves; Save Changes uses the normal backup/rollback path.

## 養成 / Progression

採用本版本編輯器支援的上限：等級 80、滿信賴、4 星濃縮（存檔 Rank 5）、HP／攻擊／防禦潛力 100、四項帕魯之魂 Rank 20、覺醒、原本具有的工作適性提升至 10。只賦予該物種在等級 80 可自然習得、未停用且非首領限定的招式；以型錄威力挑選 3 招裝備，其餘保留在已學習列表。這是安全範圍內的便利配置，不是招式 DPS 模擬或所有版本、所有流派的最強證明。玩家等級與能力點不會改動。

Uses this editor's supported limits: level 80, maximum friendship, four-star condensation (saved Rank 5), 100 HP/attack/defense talents, four soul ranks of 20, awakening, and level-10 suitability for work types the species already has. Only enabled, non-boss natural skills learned by level 80 are granted; the three highest catalog-power skills are equipped. This is a convenience preset, not a DPS simulation or universal optimal-build guarantee. Player level and stat allocations are unchanged.

| 用途 / Role | 四被動 / Four passives |
| --- | --- |
| 戰鬥 / Combat | Legend, Demon God, Serenity, Immortality |
| 基地 / Workers | Remarkable Craftsmanship, Artisan, Work Slave, Serious |
| 坐騎 / Mounts | Legend, Swift, Eternal Engine, Infinite Stamina |

基地組涵蓋 11 種工作和牧場常用蛋、奶、蜂蜜、油、布產物。牧場產量主要靠伙伴技能／濃縮；工作速度被動不能當成牧場產量加成。基地大小、走位、搬運距離、SAN、食物及支援伙伴技能也會影響效率，仍需依你的基地安排人數；本工具不會建立建築或自動修改工種分配。

Workers cover eleven jobs plus common ranch egg/milk/honey/oil/cloth production. Ranch yield relies on partner skill/condensation, not a direct work-speed multiplier. Layout, pathing, hauling distance, SAN, food and support skills affect output. This tool does not build structures or assign workstations.

## 名單 / Roster

### combat (20)

| 名稱 / Name | ID | 用途 / Purpose |
| --- | --- | --- |
| 喚夜獸 / Frostallion Noct | `IceHorse_Dark` | 戰鬥替補 / Combat reserve |
| 霄龍 / Shaolong | `BlueSkyDragon` | 戰鬥替補 / Combat reserve |
| 空渦龍 / Jetragon | `JetDragon` | 戰鬥替補 / Combat reserve |
| 波魯傑克斯 / Orserk | `ThunderDragonMan` | 戰鬥替補 / Combat reserve |
| 海皇鯨 / Neptilius | `PoseidonOrca` | 戰鬥替補 / Combat reserve |
| 喚冬獸 / Frostallion | `IceHorse` | 戰鬥替補 / Combat reserve |
| 混沌騎士 / Necromus | `BlackCentaur` | 戰鬥替補 / Combat reserve |
| 聖光騎士 / Paladius | `SaintCentaur` | 戰鬥替補 / Combat reserve |
| 傑諾多蘭 / Xenolord | `DarkMechaDragon` | 戰鬥替補 / Combat reserve |
| 貝菈露潔 / Bellanoir Libero | `NightLady_Dark` | 戰鬥替補 / Combat reserve |
| 歿殃 / Blazamut Ryu | `KingBahamut_Dragon` | 戰鬥替補 / Combat reserve |
| 霜牙王 / Bastigor | `SnowTigerBeastman` | 戰鬥替補 / Combat reserve |
| 異構格里芬 / Shadowbeak | `BlackGriffon` | 戰鬥替補 / Combat reserve |
| 獄熙龍 / Eidrolon Ignis | `GhostDragon_Fire` | 戰鬥替補 / Combat reserve |
| 默世鹿 / Hartalis | `LegendDeer` | 戰鬥替補 / Combat reserve |
| 泰鋒 / Knocklem | `WingGolem` | 戰鬥替補 / Combat reserve |
| 夜蔓爵 / Dandilord | `FlowerPrince` | 戰鬥替補 / Combat reserve |
| 阿努比斯 / Anubis | `Anubis` | 戰鬥替補 / Combat reserve |
| 百合女王 / Lyleen | `LilyQueen` | 戰鬥替補 / Combat reserve |
| 騰炎龍 / Jormuntide Ignis | `Umihebi_Fire` | 戰鬥替補 / Combat reserve |

### base (16)

| 名稱 / Name | ID | 用途 / Purpose |
| --- | --- | --- |
| 燎火舞伶 / Renjishi | `KabukiMan` | 生火 / Kindling |
| 霄龍 / Shaolong | `BlueSkyDragon` | 澆水 / Watering |
| 夜蔓爵 / Dandilord | `FlowerPrince` | 播種 / Planting |
| 波魯傑克斯 / Orserk | `ThunderDragonMan` | 發電 / Electricity |
| 墨羅娜 / Solenne | `MonochromeQueen` | 手工作業 / Handiwork |
| 空渦龍 / Jetragon | `JetDragon` | 採集 / Gathering |
| 織夜鹿 / Celesdir Noct | `WhiteDeer_Dark` | 伐木 / Lumbering |
| 磐甲龍 / Aegidron | `DomeArmorDragon` | 採礦 / Mining |
| 暮塵蛾 / Silvance | `Mothman` | 製藥 / Medicine |
| 霜牙王 / Bastigor | `SnowTigerBeastman` | 冷卻 / Cooling |
| 丹烽 / Knocklem Ignis | `WingGolem_Fire` | 搬運 / Transport |
| 皮皮雞 / Chikipi | `ChickenPal` | 牧場蛋 / Eggs |
| 波霸牛 / Mozzarina | `CowPal` | 牧場奶 / Milk |
| 騎士蜂 / Beegarde | `SoldierBee` | 牧場蜂蜜 / Honey |
| 趴趴鯰 / Dumud | `LazyCatfish` | 牧場油 / Oil |
| 綢笠蛾 / Sibelyx | `WhiteMoth` | 牧場布 / Cloth |

### mounts (5)

| 名稱 / Name | ID | 用途 / Purpose |
| --- | --- | --- |
| 空渦龍 / Jetragon | `JetDragon` | 飛行 / Air |
| 獄熙龍 / Eidrolon Ignis | `GhostDragon_Fire` | 飛行 / Air |
| 傑諾多蘭 / Xenolord | `DarkMechaDragon` | 飛行 / Air |
| 混沌騎士 / Necromus | `BlackCentaur` | 陸地 / Land |
| 海皇鯨 / Neptilius | `PoseidonOrca` | 水上 / Water |

## 裝備與物品 / Equipment and supplies

選型僅使用合法、未停用、非怪物專用物品。包含傳說終盤武器／防具與型錄可用的實用飾品；沒有捏造更高階已停用的版本。耐久及彈匣採用型錄數據，型錄為零的滑翔裝備／飾品不虛構上限。

Only legal, enabled, player-usable items are included: endgame legendary weapons/armor and useful enabled accessories. Disabled legacy/higher-numbered variants are excluded. Durability and magazines use bundled catalog values; zero-valued glider/accessory maxima are not invented.

| 物品 / Item | 數量 / Count | ID |
| --- | --- | --- |
| 遠古頭盔 / Ancient Helm | 1 | `AncientHelmet_5` |
| 輕便遠古盔甲 / Lightweight Ancient Armor | 1 | `AncientArmorWeight_5` |
| 遠古護盾 / Ancient Shield | 1 | `Shield_07` |
| 機械弓 / Mechanical Bow | 1 | `SkyBow_5` |
| 光束炮發射器 / Beam Launcher | 1 | `BeamLauncher_5` |
| 等離子步槍 / Plasma Rifle | 1 | `ElectricArcAssaultRifle_5` |
| 飛翼背包 / Wing Pack | 1 | `WingGlider` |
| 追蹤模組 / Homing Module | 1 | `SphereModule_Homing` |
| 攻擊吊墜 / Attack Pendant | 1 | `Accessory_AT_1` |
| 生命吊墜 / Life Pendant | 1 | `Accessory_HP_1` |
| 空中三段衝刺靴 / Triple Air Dash Boots | 1 | `Accessory_AirDash3` |
| 空中漫步者 Mk-Ⅱ / Air Walker Mk II | 1 | `Accessory_JumpAir_2` |
| 等離子步槍彈藥 / Plasma Rifle Ammo | 300 | `ElectricArcAssaultRifleBullet` |
| 光束炮發射器彈藥 / Beam Launcher Ammo | 100 | `BeamLauncherBullet` |
| 機械弓箭矢 / Mechanical Bow Ammo | 100 | `SkyBowArrow` |
| 飛翼能量單元 / Wing Cell | 100 | `WingGlider_Fuel` |
| 遠古帕魯球 / Ancient Sphere | 100 | `PalSphere_Ancient_2` |
| 至高恢復藥 / Advanced Recovery Meds | 20 | `Potion_Extreme` |
| 沙拉 / Salad | 20 | `Salad` |
| 金幣 / Gold Coin | 10000 | `Money` |
| 木材 / Wood | 20 | `Wood` |
| 石頭 / Stone | 10 | `Stone` |
| 金屬錠 / Ingot | 10 | `CopperIngot` |

有對應且可編輯的專用鞍具／伙伴裝備時，會另外放入重要物品。物品不保證不超重；請自行整理負重。

Matching editable saddles/partner gear are added to Key Items. The kit does not guarantee remaining under your carrying limit; organize your load before traveling.

## 參考與限制 / References and limits

網路討論只協助挑選用途，未下載任何修改器執行檔，也沒有在執行時連網取得名單。物種、招式、被動和物品 ID 一律與本專案內建 `pal_data.json`、`pal_attacks.json`、`pal_passives.json`、`items.json` 核對；型錄拒絕的項目不加入。社群對「最強」和坐騎速度仍有不同條件與意見；本名單是依資料與用途作出的選擇。

Online discussions inform role selection only. No trainer binary was downloaded; the preset is fully bundled/offline at runtime. Species, skills, passives and item IDs are checked against this project's bundled catalogs. Rankings and mount speed depend on assumptions; this roster is an implementation choice based on roles and supported data.

- [1.0 終盤戰鬥與流派實際討論 / Player build discussion](https://www.reddit.com/r/Palworld/comments/1uyo73w/best_combat_pals_in_10/)
- [1.0 基地工人實際討論 / Player worker discussion](https://www.reddit.com/r/Palworld/comments/1vtf3c3/best_base_pals_10/)
- [飛行速度與續航的條件比較 / Mount comparison](https://www.reddit.com/r/Palworld/comments/1uyd4ng/since_people_keep_asking_fastest_air_mounts/)
- [終盤配裝實際討論 / Endgame build discussion](https://www.reddit.com/r/Palworld/comments/1x3citb/endgame_priorities/)

驗證只使用專案已追蹤存檔的暫存副本，包含 41 隻完整套組存檔往返、保留原資料、重複執行、空間不足、帕魯與物品中途失敗回滾及 API 權限。未啟動遊戲；遊戲內驗收由使用者在 TEST 執行。

Validation uses temporary copies of the repository's tracked fixture: complete-41 save/reload, preservation, repeat execution, capacity refusal, Pal/item failure rollback and API authorization. The game was not launched. The user performs in-game acceptance in TEST.
