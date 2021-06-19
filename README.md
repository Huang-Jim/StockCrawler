# StockCrawler
從[台灣股市資訊網](https://goodinfo.tw/StockInfo/index.asp)爬資料，並依照需求作圖

# requirements
+ `plotly` -> 作圖使用
+ `pyyaml` -> logger使用
+ `bottle` -> 僅需載`bottle.py`即可，不須另外install，web service使用
+ `joblib` -> 儲存及讀取報表資訊
+ `beautifulsoup4` -> 爬蟲
+ `selenium` -> 爬蟲
+ [下載](https://chromedriver.chromium.org/downloads)chrome driver，並放到專案資料夾內，爬蟲時是透過`Selenium`操控

# How to use?
1. `run web.py`
2. 從瀏覽器連接 `http://localhost:9999/`
3. 輸入個股股市代碼
4. 選擇想要查看的個股資訊內容
5. 依照goodinfo上四種報表的欄位做更動
6. 點選`取得作圖`按鈕
7. 等待爬蟲程式獲取網頁資料(一檔股票一天只需等待爬蟲一次後即可產生圖表)
8. 生成的圖表會以html方式呈現並儲存在資料夾內
