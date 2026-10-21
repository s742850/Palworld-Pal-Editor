# Game data sources / 遊戲資料來源

`src/palworld_pal_editor/assets/data/fast_travel_points.json` contains factual
Palworld actor identifiers, not downloaded executable code. / 此檔案是遊戲物件 ID
資料，不包含下載的可執行程式。

- Palworld Save Pal catalog, pinned commit `0d99b04acba369ec88550d122794b9917bbf820e`:
  https://github.com/oMaN-Rod/palworld-save-pal/blob/0d99b04acba369ec88550d122794b9917bbf820e/data/json/fast_travel_points.json
- Additional observed 1.0 IDs are taken from this repository's existing bundled
  fixture `tests/saves/1.0/8C439FF04713B5F986F9CAB485575089`, specifically the
  player's `RecordData.FastTravelPointUnlockFlag` and the client's
  `Local_WarpPointUnlockFlag`. No private user saves are included.
- Schema research references / 格式研究參考：
  https://github.com/zlmitchell/palworld-save-toolkit/blob/master/SAVE-FORMAT.md
  and https://github.com/lshwan0420/palworld-save-tools.

The bundled catalog covers 182 observed 1.0 travel IDs and 8 local Warp IDs. It
does not claim automatic compatibility with future game maps. Unknown saved
flags are preserved. / 目前型錄涵蓋已觀察到的 1.0 傳送點；未知旗標保留原值，
不宣稱能自動支援未來版本。

## Endgame presets / 畢業套組

Role selection, online discussion links, all species/item IDs and the date of
research are recorded in `ENDGAME_KIT.md`. The presets contain only bundled
catalog entries. No remote executable, script or preset is fetched at runtime.
Online opinions are selection references, not a claim of universal optimality.

用途選擇、網路討論連結、物種與物品 ID 及查閱日期見 `ENDGAME_KIT.md`。
只使用內建型錄項目，執行時不下載外部修改器、腳本或名單；網路排名僅為
選擇參考，不當成所有配置最強的證明。
