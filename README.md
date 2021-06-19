# StockCrawler
1. 從[台灣股市資訊網](https://goodinfo.tw/StockInfo/index.asp)爬資料，並以簡易操作來取得個股資訊，以`plotly`呈現結果，請參考[範例](https://github.com/Huang-Jim/StockCrawler/blob/main/README.md#操作範例)
2. 請使用者依照使用情境來操作:
  + 以html做簡易的使用者介面，不想更動程式碼的使用者可以完全透過網頁操作即可取得作圖
  + 欲針對報表資訊做更改的使用者可以讀取報表的pkl檔案做後續分析
  + 欲更動程式碼的使用者則可透過`web_function.py`的`run_all`function研究即可

# Notices
1. 本專案為作者練習爬蟲、作圖以及簡易web為目的，不會頻繁針對此專案做更新，未來可能會補充的內容在[ToDoList](https://github.com/Huang-Jim/StockCrawler/blob/main/README.md#to-do-list)
3. 作者與goodinfo內部人員完全無關連，請使用者做有良心的爬蟲人，請勿在短時間內發送大量封包造成goodinfo的負擔，並點擊廣告回饋goodinfo的工程師們
4. goodinfo網頁有時會做更改，只要前端的element做變動，便可能會使爬蟲失效，請斟酌使用
5. 目前作圖皆以合併報表呈現，而非個體報表
6. goodinfo提供之報表為簡易報表，因此作圖結果不提供任何專業投資資訊，請自負投資風險

# requirements
+ `plotly` -> 作圖使用
+ `pyyaml` -> logger使用
+ `bottle` -> 僅需載`bottle.py`即可，不須另外install，web service使用
+ `joblib` -> 儲存及讀取報表資訊
+ `beautifulsoup4` -> 爬蟲
+ `selenium` -> 爬蟲
+ [下載](https://chromedriver.chromium.org/downloads)chrome driver，並放到專案資料夾內，爬蟲時是透過`Selenium`操控

# How to use?
1. `python web.py`
2. 從瀏覽器連接 `http://localhost:9999/`
3. 輸入個股股市代碼
4. 選擇想要查看的個股資訊內容
5. 依照goodinfo上四種報表的欄位做更動
6. 點選`取得作圖`按鈕
7. 等待爬蟲程式獲取網頁資料(一檔股票一天只需等待爬蟲一次後即可產生圖表)
8. 生成的圖表會以html方式呈現並儲存在資料夾內

# 操作範例
1. `python web.py`
2. 從瀏覽器連接 `http://localhost:9999/`，畫面如下，預設代碼為2330，使用者可根據需求輸入個股代碼
![操作者介面](https://github.com/Huang-Jim/StockCrawler/blob/main/fid_source/init_screen.png)
3. 從`個股資訊`選單中選出欲呈現之圖表，下方會跳出目前預設的欄位，但因每間公司的報表科目不盡相同，請至goodinfo或是台灣公開資訊觀測站查閱正確的科目名稱，在此我們先以預設的欄位，並點擊`取得專注本業作圖`按鈕
![操作者介面](https://github.com/Huang-Jim/StockCrawler/blob/main/fid_source/example_%E5%B0%88%E6%B3%A8%E6%9C%AC%E6%A5%AD_1.png)
4. 目前程式預設會以"日"為單位做更新，假設偵測到目前資料夾中尚未有個股報表資訊，或是已有的資訊太舊，則會重新透過爬蟲抓取資料，此步驟會透過selenium操控chrome driver作抓取，請勿在抓取完成前關閉跳出的chrome視窗(有些電腦不會跳出視窗)或是程式，如下圖chrome上方顯示目前由測試軟體操控中
![操作者介面](https://github.com/Huang-Jim/StockCrawler/blob/main/fid_source/example_selenium.png)
5. 如下圖，假設目前的欄位科目不存在報表科目中，使用者介面會跳出文字警示，由於2330並無"應收票據"以及"預付款項–流動資產"，則點選兩項科目旁的`移除欄位`按鈕，再重新取得作圖即可
![操作者介面](https://github.com/Huang-Jim/StockCrawler/blob/main/fid_source/example_%E5%B0%88%E6%B3%A8%E6%9C%AC%E6%A5%AD_3.png)
6. 成功後系統會跳出以`plotly`繪製的html圖表，使用者可依需求做調整並儲存
![操作者介面](https://github.com/Huang-Jim/StockCrawler/blob/main/fid_source/example_%E5%B0%88%E6%B3%A8%E6%9C%AC%E6%A5%AD_4.png)

# To Do List
- [ ] 多圖組合成一張圖
- [ ] 設計介面可讓使用者從0開始依照自己想要的科目製表
- [ ] 增加更多預設的作圖資訊
