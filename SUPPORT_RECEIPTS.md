# 後續開發者收款 / Maintainer receipts

## 收款對象

新增的加密貨幣地址與中國信託銀行帳戶由使用者提供，用於後續開發者 **s742850** 的贊助。原作者為 **_connlost（GitHub：KrisCris）**，依本專案 README 與 pyproject.toml 核對。原作者既有的 Ko-fi、PayPal、AliPay、WeChat Pay 保留於獨立區塊；後續開發者收款資訊不會覆蓋原作者收款方式。

## 資料與去重

- `frontend/palworld-pal-editor-webui/src/support-receipts.json`：公開收款設定；網路支援只依使用者截圖建檔，不由相同地址推測其他幣別或網路。
- `frontend/palworld-pal-editor-webui/tests/fixtures/support-receipts-evidence.json`：41 張來源圖的 SHA-256、批次、圖片編號與實際 QR 解碼結果。第一批 34 張，第二批 7 張 USDC。原始手機截圖不打包。
- 第一批重複圖片：9 → 8、18 → 2、19 → 3、22 → 11、23 → 10。去重鍵為幣別＋網路＋地址，保留不同鏈及不同 BTC 地址格式。
- 去重後 USDT 18、USDC 7、BTC 4、ETH 6，合計 35 個加密貨幣選項；另有 1 個台幣銀行帳戶。Kraken 僅為提供的 USDT / Tron 選項，其餘加密貨幣選項來自 Binance 截圖。
- QR 圖片以解碼內容重新產生，保留安靜區並逐張再解碼核對；銀行 TWQR 保留來源的 percent-encoded payload，不擅自解碼後改寫。相同地址共用同一張 QR，但 UI 始終顯示所選幣別及網路。
- 地址、QR Code、幣別與網路圖示均在本機提供，不透過外部 QR 產生服務傳送收款資料。圖示來源與 MIT 授權位於 `public/support/icons/`；opBNB 使用 BNB 生態系圖示，Bitcoin 與 SegWit 共用 Bitcoin 圖示。

## 顯示與限制

幣別切換時清除舊網路與收款資訊；未選網路不顯示地址。切換時的資料由同一筆 route 驅動，避免地址與 QR 不一致。提供繁中、簡中、英文文字，其餘介面語言沿用現有英文 fallback。

最低入帳金額、比較符號與合約尾碼依使用者提供的截圖轉錄，資料整理日期為 2026-10-25。它們不是即時交易所資料。QR 僅含地址，沒有鏈別；付款者仍需在轉出平台選擇對應網路。BTC / Ethereum 標明 BBTC、BTC / BSC 標明 BTCB；USDC / Optimism 與 Polygon 保留原生 USDC 提醒。

本次只實作公開收款展示，不接入交易所私有 API、不代發交易、不查帳或宣稱已入帳。地址與截圖一致不代表帳戶當下可入金，也不代表交易所已同意第三方贊助用途。Kraken 與 Binance 的最新入金規則及第三方收款限制，需由帳戶持有人依適用地區與帳戶條款確認。

官方參考：

- Kraken 入金最低額：https://support.kraken.com/articles/360000292886-cryptocurrency-deposit-fees-and-minimums
- Kraken 條款：https://www.kraken.com/legal/global-terms
- Binance 入金說明：https://www.binance.com/en-IN/support/faq/detail/115003764971

## 驗證

- `node --test tests/*.test.js`：240 個前端測試通過，包含來源資料覆蓋、去重、地址一致性、圖檔存在、銀行帳號保留前導零與多語系署名。
- Vite 正式建置輸出至桌面 Flask 使用的 `src/palworld_pal_editor/webui`，PWA 檢查通過。
- Headless Edge 實際點選全部 35 個選項；檢查切換幣別清除舊地址、網路搜尋、地址／銀行帳號複製、390px 手機版無橫向溢出、原作者放大 QR 的收款對象標示與 Escape 關閉。
- 41 張來源 QR 全數解碼；產生的 QR 逐張解碼比對來源。實際 Flask test client 驗證 `/`、新版 JS bundle 與全部 36 個唯一收款圖檔為正確的圖片回應。
- 未進行真實轉帳、交易所登入／帳戶核准驗證或新安裝檔發布。
