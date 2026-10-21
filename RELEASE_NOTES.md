# Release notes / 更新說明

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
