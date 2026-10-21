# Windows Steam 版：安裝、物品編輯與防護

這份修改建立在原始專案既有的物品存檔讀寫功能上，補上明確的材料／裝備新增入口、空格加號、常駐刪除按鈕與繁體中文。原本的 Steam 遊戲不需安裝 MOD，也不需把修改器放進遊戲目錄。

## 這台電腦直接使用

專案：`C:\github\Palworld-Pal-Editor`。完成安裝後雙擊根目錄的 `start-local.cmd`。
它會啟動這份原始碼建置的介面；之前下載的舊版 EXE 不會自動包含這次修改。

## 換電腦或重新安裝

支援本安裝流程的平台為 Windows x64。先備妥 Python 3.11 以上（包含 headers 與 libs 的完整安裝）、Git、Node.js 22 以上與 pnpm 11.25.0。用一般使用者權限執行即可。

在 repo 根目錄開啟 PowerShell：

```powershell
pnpm --version
python --version
git --version
powershell -NoProfile -ExecutionPolicy Bypass -File .\install-local.ps1
```

`ExecutionPolicy Bypass` 只作用於該次 PowerShell 程序，不修改全機設定，也不要求關閉防毒。執行前可閱讀 `install-local.ps1` 與 `scripts/build_ooz_windows.py`。

腳本會建立 `.venv`、安裝依賴、從指定 Git commit 建置新版存檔需要的壓縮模組，再依 `pnpm-lock.yaml` 安裝前端並建置。使用 `--ignore-scripts` 停用套件安裝生命週期腳本；Vite 建置仍會執行專案及依賴程式碼。所有步驟遇錯即停止。首次需要網路，壓縮編譯可能需要幾分鐘。

原本上游依賴會要求 Microsoft C++ Build Tools；這個流程改用專案環境內的 Zig 0.13.0 建置同一個固定版本的原始碼，不修改系統工具鏈。不能改裝 PyPI 的 `pyooz==0.0.8` 取代：該版本只有解壓縮，無法寫入這份專案的新版存檔。

安裝完成後執行：

```powershell
.\start-local.cmd
```

若桌面視窗無法開啟，可使用同樣只監聽本機的瀏覽器模式：

```powershell
$env:PYTHONPATH = "$PWD\src"
$env:PYTHONUTF8 = '1'
Remove-Item Env:PAL_EDITOR_ALLOW_REMOTE -ErrorAction SilentlyContinue
.\.venv\Scripts\python.exe -m palworld_pal_editor --mode web --lang zh-TW --nocli
```

## 修改材料、背包與裝備

1. 完全退出遊戲，等待 Steam 存檔同步完成。
2. 按 `Win+R`，輸入 `%LOCALAPPDATA%\Pal\Saved\SaveGames`。先另外備份整個相關 Steam ID 目錄，包含世界、`Players` 與可能存在的 `GlobalPalStorage.sav`。
3. 修改器中選擇含 `Level.sav` 的世界資料夾並載入；多人伺服器存檔必須取得伺服器上的世界與玩家資料，只有本機用戶端檔案不夠。
4. 點選要修改的玩家，進入玩家的物品／背包頁籤。
5. **新增材料**：背包上方選「材料」，按「新增物品」，搜尋名稱或內部 ID，設定數量後「套用」。也可以點空格的 `+`。新增只使用既有空欄位，背包已滿時需先刪除物品。
6. **新增裝備**：選「裝備」可放進背包；要直接穿戴則點右側對應的武器、防具、飾品、護盾或滑翔傘欄位。介面只顯示該裝備欄可接受的類型。
7. **修改**：點已有物品，可更換物品或調整可堆疊物品數量。套用同一件裝備會保留它原本的 GUID、耐久、彈藥與被動技能。更換成不同裝備會建立新裝備資料。裝備欄數量固定為 1。
8. **刪除**：按格子右上方 `×`，或在物品視窗按「刪除此欄物品」。沒有型錄圖示的未知物品也能刪除。刪除的是整個堆疊，減少數量請用修改。
9. 按主工具列的「儲存變更」才會寫回磁碟；只在物品視窗按「套用」仍是記憶體中的變更。儲存後再進入遊戲確認。

一般模式遵守物品型錄的最大堆疊數。沒有正確建構資料的帕魯蛋不提供新增。部分上游物品型錄的最大耐久資料為 0（例如某些抓鉤槍），建立後的遊戲行為仍需自行確認；這次沒有憑空填入未驗證的耐久值。

若要還原，先關閉遊戲及修改器，從你另外保留的備份還原整組世界／玩家資料。遊戲運行期間不要覆蓋存檔。

## 本次防護變更與限制

「重要物品」頁籤的「一鍵新增全部鞍具／帕魯裝備」會補齊內建型錄中的合法鞍具與伙伴技能專用裝備。已有物品保留，不建立重複項目；空格不足時整批不執行。完成後仍需按「儲存變更」。

- GUI 與 Web 預設只監聽 `127.0.0.1`；`start-local.cmd` 會清除遠端啟用環境變數。
- 登入 JWT 金鑰每次啟動重新隨機產生，不接受舊設定中的公開固定金鑰，因此重新啟動後需要重新登入。
- 新寫出的設定檔不儲存密碼或簽章金鑰，日誌不顯示密碼。既有設定或舊備份內的密碼不會因此自動消失，需要自行清理；不要公開整個設定／日誌資料夾。
- 本機模式拒絕不受信任 Host，未允許的跨來源寫入在處理登入／存檔前即拒絕。
- HTTP 回應限制 iframe 嵌入、MIME 猜測與 Referer 外洩；內部例外堆疊只記錄於本機，不回傳給瀏覽器。
- 已更新掃描報告涉及的 Flask、aiohttp、requests、Pillow、setuptools、wheel 與安裝環境 pip。
- 安裝及更新仍需信任第三方依賴。漏洞資料庫掃描不能證明沒有惡意程式，也不能完整涵蓋 GitHub 來源的存檔工具與本機編譯的原生壓縮程式。只打開你信任的存檔，不需要管理員權限或關閉防毒。
- 程式啟動／前端可能向 GitHub 檢查新版本，贊助頁連結只有點擊才開啟。這次未做網路封包動態稽核，也未用你的實際遊戲存檔驗證遊戲內結果。

若明確需要遠端服務，必須同時設定 `PAL_EDITOR_ALLOW_REMOTE=1`、`--mode web` 與至少 12 字元的密碼。內建 HTTP 沒有 TLS；個人使用保持預設即可，不要直接做路由器轉發。

## 自訂加密貨幣贊助入口

複製 `frontend/palworld-pal-editor-webui/.env.example` 為同目錄的 `.env.local`。可以使用 HTTPS 收款頁，或直接顯示公開地址。例如下面的地址必須自行替換，不能照抄當作真實地址：

```dotenv
VITE_SUPPORT_NAME=修改版維護者名稱
VITE_SUPPORT_URL=
VITE_SUPPORT_ADDRESS=你的公開收款地址
VITE_SUPPORT_ASSET=USDT
VITE_SUPPORT_NETWORK=實際使用的網路名稱
```

直接顯示地址時必須填寫幣種與網路。若使用收款頁，`VITE_SUPPORT_URL` 僅接受沒有帳密的 `https://` 連結。未設定或格式不合法時，不顯示修改版收款入口。

重新執行安裝腳本會重建前端並套用設定。程式不連接錢包、不發起交易、不要求簽名。所有 `VITE_` 內容都會變成公開前端資源，絕不能放私鑰、助記詞、交易所 API Key 或密碼。

贊助區明確區分「此修改版維護者」與原作者；原作者署名與原始贊助入口仍保留。尚未提供真實地址前，不會替你填寫任何收款對象。

## 本機驗證紀錄（2026-10-21）

- 安裝腳本、前端正式建置、283 個後端測試、234 個前端測試通過；另有 223 個後端子測試。完整套件封裝測試初次因環境缺 npm 失敗，補入隔離工具後單獨重跑通過。
- Python 與前端套件的已知漏洞掃描未再回報漏洞；GitHub 來源／自行編譯的依賴不能視為已被完整覆蓋。
- 已用可見介面驗證材料新增、數量修改、刪除與裝備新增。
- 額外只操作你的 **TEST** 世界：資料夾 `33F0D4B34BC0DF26E32AE0A6421CE0BE`，玩家 `s742850`。寫入後重新載入確認：木材 ×20、石頭 ×10、武器欄木棍、身體欄布衣、護盾欄普通護盾；測試用纖維已刪除。
- TEST 原始備份在本機 `.venv/test-world-backup-<timestamp>`。只寫入 TEST 的 Level／Players 資料，驗收服務另加了路徑限制以拒絕共用倉庫寫入。
- 非測試世界的 315 個檔案已在操作前後比對 SHA256，全數一致。驗證紀錄在本機 `.venv/protected-world-verification.json`。
- **未啟動遊戲**。遊戲內顯示、穿戴及使用由你登入 TEST 驗收；程式的離線重新讀取成功不等於遊戲內驗收完成。

## 使用的技術

| 技術 | 用途 |
| --- | --- |
| Python 3.11+ | 存檔載入、資料驗證、物品／裝備讀寫 |
| Flask、Waitress | 提供本機 REST API 與介面資源 |
| Flask-JWT-Extended、Werkzeug、Python secrets | 登入權杖、密碼比對、隨機簽章金鑰 |
| Vue 3、JavaScript、Pinia、Vue Router | 背包格子、物品搜尋、裝備編輯與前端狀態 |
| Vite、pnpm | 前端建置與鎖定依賴安裝 |
| pywebview | 把本機網頁介面放進 Windows 桌面視窗 |
| palworld-save-tools、GVAS、pyooz／ooz | Unreal Engine 存檔解析與新版 Oodle 格式壓縮 |
| C++、Zig 0.13.0、Python Wheel | 在隔離環境編譯並安裝原生壓縮模組 |
| PowerShell、CMD、venv | 安裝自動化、雙擊啟動、隔離 Python 套件 |
| pytest、Node test runner、Vue SSR | API、存檔往返、來源限制與前端回歸驗證 |
| pip-audit、pnpm audit | 已知依賴漏洞掃描；不等於完整資安認證 |

版本更新內容請見 RELEASE_NOTES.md；程式碼以各里程碑 commit 發布。原始專案與第三方壓縮程式各自的授權需保留及檢視；本次未做對外散布的授權審核。
