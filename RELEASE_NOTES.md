# Release notes / 更新說明

## 2026-10-23 · Adventure assistant / 冒險助手

- 保留畢業套組，新增獨立冒險助手。選擇探索捕捉、準備戰鬥、基地生產或移動探索後，依目前等級、已解鎖科技、捕捉紀錄與現有夥伴提供建議；可降低協助等級上限。
- 逐項「查看新增內容 → 套用並新增」，取消不寫入。物品只補建議差額；帕魯限已捕捉的精選普通物種，個體值 0、無額外被動、不提升濃縮。已有適用夥伴時優先建議使用。仍需按「儲存變更」。
- 修正捕捉次數原先將 MapProperty 清單當字典、導致一律讀成 0 的問題。重新載入存檔或推薦條件改變時，舊確認失效；容量不足不覆寫既有內容，中途失敗回滾。新增不會繞過夥伴科技解鎖門檻。
- 第一版為精選入門清單，不是完整後期攻略。僅統計一般背包，不含基地箱子；沒有持久領取冷卻。繁中、簡中、英文介面，其他語言的新文案使用英文後備，遊戲物種與物品名稱仍依介面語言。
- Endgame kits are preserved. A separate Adventure assistant explains curated suggestions and adds only after explicit per-item confirmation. Recommendations use level limits, unlocked recipes, capture history and existing world Pals. Supply top-ups and ordinary partners remain pending until Save Changes; stale confirmations and capacity failures cannot overwrite possessions. The capture-count getter now reads native MapProperty entries correctly. This is a limited starter rule set, with no persistent allowance/cooldown.
- 驗證 / Validation：測試副本涵蓋新增、容量、重複與過期確認、儲存往返、回滾及 API 權限；前端操作測試與正式建置通過；Chrome 模擬 API 驗證查看、取消、套用、過期更新、空狀態及 360px 排版。未讀寫玩家實際存檔，未進行遊戲內驗收。 / Fixture-only backend validation, frontend tests and production build; real Chrome with a mocked API verifies the confirmation workflow and narrow layout. No live saves edited; in-game acceptance remains unverified.

## 2026-10-23 · Mount kit backpack-capacity fix / 坐騎套組背包容量修正

- 飛行／陸地／水上坐騎套組不再因一般背包缺少 21 個終盤物資空格而整批停止；該套組只新增 5 隻坐騎及缺少的對應鞍具，重要物品欄仍維持容量預檢與整批回滾。
- 完整、戰鬥及核心戰鬥套組仍會補齊終盤裝備與物資，並維持原本的一般背包容量檢查。
- The air/land/water mount preset no longer aborts because the common backpack lacks 21 slots for the combat loadout. It adds the five mounts and missing matching saddles, while retaining atomic Key Item capacity checks and rollback.
- Complete, combat, and core-combat presets still add the endgame loadout and retain their common-backpack capacity preflight.
- 驗證 / Validation：26 個畢業套組測試、235 個前端測試及正式建置通過；另有 486 個後端測試與 407 個子測試通過，3 項與本次修改無關的封裝／發布工具測試因本機缺少未追蹤審核輸出與 `npm` 指令而失敗。僅使用測試副本，未進行遊戲內驗收。 / 26 graduation-kit tests, 235 frontend tests, and the production build passed. The wider backend run passed 486 tests and 407 subtests; three unrelated packaging/publisher-tool tests failed because this checkout lacks an untracked review artifact and an `npm` executable. Fixture copies only; in-game acceptance remains unverified.

## 2026-10-22 · Localized endgame nicknames / 畢業套組暱稱在地化

- 畢業套組暱稱依選擇的介面語言顯示物種名稱及戰鬥／基地／坐騎後綴，區分同種不同用途的個體。
- 再次套用會更新所選套組中可辨識的舊版與跨語言預設暱稱；切換語言不會重複新增。自行命名的帕魯保持原名。仍需按「儲存變更」。
- Endgame nicknames now use the selected interface language with Combat / Base / Mount suffixes to distinguish roles of the same species.
- Reapplying updates recognized legacy and localized default names in the selected preset without language-induced duplicates. Custom names are preserved. Save Changes is still required.
- 驗證 / Validation：25 個套組測試通過，涵蓋 17 種語言、舊名稱轉換、跨語言去重、改名保留、存檔往返與失敗回滾；前端正式建置通過。僅使用測試副本，未進行遊戲內驗收。 / 25 kit tests passed, covering 17 locales, legacy migration, cross-language deduplication, custom-name preservation, save/reload and rollback. Frontend production build passed. Fixture copies only; in-game acceptance remains unverified.

## 2026-10-21 · 4. Endgame combat, workers and mounts / 戰鬥、基地與坐騎畢業套組

### 繁體中文

- 新增「畢業套組」頁籤，列出實際名單：戰鬥 20 隻、基地 16 隻、坐騎 5 隻、完整 41 隻，並保留核心 5 隻。依使用者後續需求納入基地與坐騎，不再限定只有一隊。
- 戰鬥、工作、坐騎分別配置四個被動；同種不同用途產生不同個體。以編輯器支援的合法養成上限（Lv.80、滿信賴、4 星、潛力 100、魂 Rank 20、覺醒、已有工種適性 10）建立普通可取得帕魯，不加入塔主或型錄拒絕的物種。
- 自然習得招式保留於已學列表，以型錄威力選 3 招裝備；不宣稱此簡化選招是所有流派的 DPS 最佳解。網路查閱和用途選擇記錄在 `ENDGAME_KIT.md`，數據仍以內建型錄核對。
- 新增帕魯放入所選玩家本世界終端；補齊合法終盤武器、防具、實用飾品、彈藥、球、藥品、少量素材及對應鞍具。裝備放背包供自行穿戴，保留既有裝備與玩家等級／能力點。沒有啟用停用物品或假造高階飾品。
- 空間不足整批拒絕，帕魯或物品中途失敗整批回滾；不覆蓋占用格，已有物品不補堆疊。可見的預設名稱仍在原玩家終端時跳過重複帕魯，改名或移走後可再次新增。
- 仍需手動儲存變更。基地工人需自行派駐；牧場產量、搬運、走位和 SAN 仍受遊戲機制影響。完整限制與名單見 `ENDGAME_KIT.md`。
- 自動 Nightly 發布流程會附上本檔中英文說明；這項流程調整不代表 GitHub 已產出安裝檔，須以遠端 Actions／Release 的實際結果為準。
- 驗證：6 個新增後端整合測試涵蓋 41 隻完整套組存檔往返、原內容保留、重複執行、空間不足、兩種中途失敗回滾、API 權限與不自動存檔；235 個前端測試及正式建置通過。只用測試副本，未啟動遊戲。
- 最終完整回歸：297 個後端測試與 230 個子測試全部通過；唯一警告來自測試刻意簽發舊短金鑰以確認拒絕，而非執行環境採用該金鑰。

### English

- Added an Endgame kit tab with visible rosters: combat 20, workers 16, mounts 5, all 41, or core 5. Includes base and mount builds following the user's expanded requirements.
- Creates normal supported Pals with role-specific passives and this editor's supported progression limits: level 80, maximum friendship, four stars, 100 talents, soul ranks 20, awakening and level-10 existing work types. Different roles create separate individuals of the same species; tower bosses and catalog-invalid species are excluded.
- Grants supported natural skills and equips the three highest catalog-power skills. This is not a universal DPS optimizer. Research and selection rationale are documented in `ENDGAME_KIT.md`; IDs are validated against bundled data.
- Pals go into the selected player's world Palbox. Missing enabled endgame gear, accessories, ammunition, spheres, medicine, a few materials and matching saddles are added. Equipment stays in the backpack for manual equipping; existing gear, player level and stat allocations are preserved. Disabled higher-numbered accessory variants are excluded.
- Preflights all capacity; failures roll back the entire batch. Existing slots/stacks remain unchanged. Default-named gifts still in that player's Palbox are skipped; renaming/moving them permits another copy.
- Save Changes is still required. Assign workers yourself; ranch yields, hauling, pathing and SAN remain subject to game mechanics. See `ENDGAME_KIT.md` for the roster and limits.
- The existing Nightly publisher now includes this bilingual changelog. This workflow change does not itself confirm a published binary; check the remote Actions/Release result.
- Validation: 6 new backend integration tests cover the full-41 save/reload, preservation, idempotence, capacity refusal, two mid-batch rollback cases, authentication and no auto-save; 235 frontend tests and production build passed. Only fixture copies were used; the game was not launched.
- Final full regression: all 297 backend tests and 230 subtests passed. The sole warning comes from a test deliberately signing with an old short key to verify rejection, not from the runtime using that key.

## 2026-10-21 · 3. Map reveal and fast travel / 地圖全開與傳送點

### 繁體中文

- 玩家頁新增「地圖與傳送點」：清除主地圖／世界樹迷霧，並解鎖固定 1.0 型錄中的 182 個傳送點與單機主機的 8 個本地 Warp 標記。
- 迷霧只更動 RGBA 遮罩的 alpha；保留 RGB、地圖標記及其他進度。僅允許單機主機操作目前世界的 `LocalData.sav`，不替其他多人玩家猜測本地檔案。
- 以記憶體編輯、儲存變更、備份及失敗回滾整合 LocalData。檔案若被遊戲或外部程式改動，拒絕覆蓋並要求重新載入。
- 避開上游原生壓縮器在大量零值遮罩的已知錯誤：LocalData 使用標準 Oodle 複製區塊，保留 PlM 格式並在寫入前解碼比對；檔案可能增至約 5 MB。
- 未知格式停用；未列於型錄的旗標保留，不宣稱自動涵蓋未來版本。來源見 `DATA_SOURCES.md`。
- 驗證：10 個相關測試與 34 個子測試通過；另重跑 5 個地圖測試，包含中斷 LocalData 寫入後還原與重試、重新讀取及其他欄位不變。前端 234 個測試及正式建置通過；未開啟使用者遊戲。

### English

- Added a Map & Fast Travel tab: reveal MainMap/Tree fog, unlock 182 known 1.0 travel IDs and the single-player host's 8 local Warp IDs.
- Changes only fog-mask alpha bytes, preserving RGB, custom markers and unrelated progress. LocalData editing is restricted to the single-player host in the loaded world.
- LocalData participates in Save Changes, backups and rollback. External file changes are detected before overwrite.
- Avoided a native encoder bug on cleared textures by using standard Oodle copied blocks for LocalData, preserving PlM format and verifying decoded bytes before writing. LocalData may grow to about 5 MB.
- Unknown layouts are disabled; non-catalog flags remain unchanged. Future game-map compatibility is not assumed. See `DATA_SOURCES.md`.
- Validation: 10 related tests plus 34 subtests passed; 5 map tests were rerun including interrupted-write rollback/retry, reload and unrelated-field preservation. 234 frontend tests and production build passed. The user's game was not launched.

## 2026-10-21 · 2. All Pal saddles and gear / 一鍵新增全部鞍具與專用裝備

### 繁體中文

- 在「重要物品」新增一鍵按鈕，依內建遊戲型錄加入全部合法的帕魯鞍具及伙伴技能專用裝備（包含專用武器、手套等）。
- 只補缺少的物品，每件 1 個，保留原有欄位與其他重要物品；重複執行不會重複新增。空格不足或資料驗證失敗時整批拒絕，不會只加入一半。
- 仍需按「儲存變更」才寫入存檔，不操作跨界終端或其他玩家。
- 驗證：23 個相關後端測試與 33 個子測試、234 個前端測試及正式建置通過。

### English

- Added an all-Pal-gear button to Key Items, using the bundled legal item catalog for saddles and partner-skill equipment, including dedicated weapons and gloves.
- Adds one of each missing item into empty slots, preserves existing items, and skips duplicates on repeated clicks. Capacity/validation failures reject the entire batch before mutation.
- Save Changes is still required to write to disk. Shared Global Pal Storage and other players are untouched.
- Validation: 23 related backend tests plus 33 subtests, 234 frontend tests and the production build passed.

## 2026-10-21 · 1. Inventory, equipment and local security / 物品、裝備與本機防護

### 繁體中文

- 在既有存檔編輯功能上補齊明確的材料／裝備新增入口、空格加號與常駐刪除按鈕，支援搜尋、數量修改及相容裝備欄位。
- 套用同一件裝備時保留其耐久、彈藥、GUID 與被動技能；切換玩家時避免顯示過期的背包回應。
- 補充繁體中文物品介面、Windows 隔離安裝腳本、雙擊啟動入口及使用手冊。
- 預設只允許本機連線；登入金鑰每次啟動隨機產生；新設定檔不保存密碼／金鑰；拒絕不可信任的 Host 與跨來源寫入；隱藏對外例外堆疊並更新已知漏洞依賴。
- 贊助頁可選配公開加密貨幣地址／HTTPS 收款頁，清楚區分修改版維護者與原作者，不需要錢包連線或私鑰。
- 驗證：安裝與正式建置通過；283 個後端測試（含單獨重跑的封裝測試）、234 個前端測試通過。TEST 世界離線寫入／重新讀取通過；其他世界檔案雜湊一致。遊戲內驗收由使用者完成。
- 「跨界帕魯終端（GPS）」是上游原本就有的 Global Pal Storage 編輯入口，對應世界資料夾外的 `GlobalPalStorage.sav`，屬共用資料；本次沒有新增該入口，也沒有以此修改其他世界。

### English

- Added explicit material/equipment creation controls, empty-slot affordances and visible delete controls on top of the existing save editor, including search, stack counts and equipment compatibility checks.
- Reapplying the same equipment preserves its GUID, durability, ammunition and passive skills. Inventory responses are discarded when the selected player/session changes.
- Added Traditional Chinese inventory labels, an isolated Windows installer, a double-click launcher and a usage guide.
- Defaulted network binding to loopback, randomized JWT signing keys per process, removed passwords/signing keys from newly saved configuration, rejected untrusted Hosts/cross-origin writes, removed client-facing tracebacks and updated vulnerable dependencies.
- Added optional public cryptocurrency addresses/HTTPS payment links with separate fork-maintainer attribution. No wallet connection or private keys are required.
- Validation: installation and production build passed; 283 backend tests (including a separately rerun packaging test) and 234 frontend tests passed. Offline TEST-world save/reload passed; other-world hashes were unchanged. In-game acceptance remains user-run.
- The GPS entry is an existing upstream editor for shared `GlobalPalStorage.sav`, outside an individual world folder. It was not introduced by this change; shared storage must be treated separately from world-local Pals.

Known limitations / 已知限制：GitHub/native dependencies are not fully covered by vulnerability databases. Some upstream item durability metadata is incomplete. Back up saves and exit the game before writing. / 漏洞資料庫無法完整涵蓋 GitHub 與原生依賴；部分上游物品耐久資料不完整。修改前請備份並離開遊戲。
