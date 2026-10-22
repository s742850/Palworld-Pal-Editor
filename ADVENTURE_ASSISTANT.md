# 冒險助手 / Adventure assistant

畢業套組保留。新增獨立「冒險助手」頁籤，流程為：選擇目的 → 查看建議與依據 → 查看新增內容 →「套用並新增」。沒有預選項目或自動發放；取消不寫入。套用僅修改編輯器記憶體，沿用「儲存變更」寫入存檔。

## 判斷依據

- 等級是上限，不是進度的唯一證據。使用者可選較低的協助上限，無法以此越過玩家等級、科技或捕捉門檻。
- 物品必須列在精選規則中，且已解鎖的內建科技型錄 `UnlockItems` 包含該物品；科技等級亦須符合上限。不憑科技 ID 與物品 ID 名字相似推斷。
- 捕捉紀錄用原生 MapProperty 的 `{key, value}` 清單讀取，缺資料時不推定捕捉過。
- 帕魯限精選、可正常取得的普通物種。未捕捉且未擁有的物種不顯示，避免劇透；已有物種優先建議直接使用。基地／探索用途已有任何夥伴具備該工種時，不再提供新增。
- 坐騎另要求已解鎖對應鞍具科技；本次不附送鞍具，介面說明需自行製作／準備。
- 既有新增帕魯的儲存結算會解鎖其夥伴科技，因此助手對所有新增候選另檢查：有對應夥伴科技時須先解鎖且符合等級上限。尚未符合時只顯示建議，不提供新增，避免儲存時越級解鎖科技。
- 捕捉與科技紀錄無法證明是自然遊玩取得。舊修改器產生的紀錄也可能被讀取，介面提供降低上限的方式，不聲稱可自動復原玩家原始進度。

## 第一版精選規則

| 目的 | 補給 | 帕魯用途候選（須符合上述條件） |
| --- | --- | --- |
| 探索捕捉 | `PalSphere` 補至 10、`PalSphere_Mega` 補至 8、`PalSphere_Giga` 補至 5；只取已解鎖的最高候選，已足量不改發低階球 | `PinkCat` 搬運、`SheepBall` 手工作業 |
| 準備戰鬥 | 普通箭補至 20、手槍子彈補至 30；必須在背包或武器欄持有相容武器 | `Kitsunebi` 火、`Penguin` 水、`PlantSlime` 草 |
| 基地生產 | 不推定基地箱子缺料，不送材料 | `Penguin` 澆水、`Kitsunebi` 生火、`PlantSlime` 播種、`PinkCat` 採礦 |
| 移動探索 | 不另送物資 | `Alpaca`、`Boar` 陸地，`HawkBird` 飛行 |

名稱使用目前語言的遊戲型錄；上述物種 ID 供維護規則使用。規則位於 `core/adventure_assistant.py`，屬保守的入門協助清單，不是完整的後期進度攻略或最強排行榜。UI 最多顯示 3 個帕魯候選，優先顯示可補足的用途。

## 新增限制

- 補給數量 = 建議目標 − 一般背包所有相同物品堆疊總數；先補既有堆疊，再使用空格。庫存不包含基地箱子、掉落物或其他玩家。
- 每次確認只新增一項建議。帕魯一次一隻，個體值固定為 0、無額外被動、不提升濃縮、魂或工作適性；使用該等級自然習得的招式。
- 帕魯等級取玩家協助上限、隨身隊伍等級中位數、20 三者最小值；沒有隨身隊伍時為 1。不是依整個終端的最高帕魯判斷。
- 帕魯放入所選玩家本世界終端。儲存時沿用既有新帕魯結算，會更新捕捉／圖鑑與相應既有結算效果。
- 物品足量或已有適用帕魯後不再提供同項新增；沒有跨遊玩階段額度或持久冷卻。消耗資源或移除夥伴後，可能重新出現建議。

## 寫入與驗證

`GET /api/players/<uid>/adventure?goal=explore&ceiling=10` 只產生建議。`POST` 僅接受 `goal`、`ceiling`、`recommendationId`、`token`。伺服器在 session lock 內重新產生推薦，驗證本次載入識別、玩家與預覽內容；過期推薦回應 409，前端重新讀取，使用者需再次確認。客戶端不能指定任意物種、數量或能力。

容量與物品合法性在寫入前檢查。中途失敗恢復容器、群組與新增記錄；不覆寫其他物品與帕魯。前端防止重複點擊，忽略舊玩家／舊存檔／舊查詢的回應。

測試僅使用複製的 fixture 存檔。`tests/test_adventure_assistant.py` 涵蓋真實捕捉紀錄、科技與武器門檻、差額補給、重複／過期確認、失敗回滾、容量與存檔往返。前端 `tests/adventure.test.js` 驗證操作與競態；`tests/adventure-browser.mjs` 以模擬 API 驅動真實 Vue 元件，驗證確認、取消、套用、過期更新、空狀態及窄螢幕，不會讀寫遊戲存檔。遊戲內平衡仍需試玩驗收。

## English

An independent opt-in Adventure assistant preserves Endgame kits. Curated starter suggestions use unlocked item recipes, capture history, owned world Pals and a user-adjustable level ceiling. Previewing or cancelling never writes; explicit confirmation creates pending additions, followed by the existing Save Changes workflow. Supplies top up bounded backpack stock, and ordinary Pals use zero IVs, no added passives and level-appropriate natural attacks. Recomputed confirmation tokens reject stale loads or changed suggestions. There is no persistent allowance/cooldown and no claim to infer unmodified natural progress. See the tests above for fixture-only and mocked-API browser validation; in-game balance remains unverified.
