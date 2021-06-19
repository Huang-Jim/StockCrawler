from datetime import datetime
import logging
from typing import List, Dict
from time import sleep
import random

import bs4
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import joblib
from selenium import webdriver
from selenium.webdriver.support.ui import Select
import requests

from application.structures.sheet_struct import InfoDict

logger = logging.getLogger(__name__)

statement_chi_eng = {"資產負債表": "BS",
                     "損益表": "IS",
                     "現金流量表": "CF",
                     "財務比率表": "XX"}

consolidated_time_sacles = {"資產負債表": {"合併資產負債表-年度": "BS_M_YEAR", "合併資產負債表-季度": "BS_M_QUAR"},
                            "損益表": {"合併損益表-年度": "IS_M_YEAR", "合併損益表-單季": "IS_M_QUAR", "合併損益表-累季": "IS_M_QUAR_ACC"},
                            "現金流量表": {"合併現金流量表-年度": "CF_M_YEAR", "合併現金流量表-單季": "CF_M_QUAR",
                                      "合併現金流量表-累季": "CF_M_QUAR_ACC"},
                            "財務比率表": {"合併財務比率表-年度": "XX_M_YEAR", "合併財務比率表-單季": "XX_M_QUAR",
                                      "合併財務比率表-累季": "XX_M_QUAR_ACC"},
                            }


class TableHandler:
    """
    處理四張報表的table data
    """

    def __init__(self):
        """ 建立四張表的init dict
        每張表的結構皆為兩層dict
            第一層key是時間尺度, e.g. 季, 年或是累計季
            第一層val是在當前時間尺度下的報表資訊
            第二層key是報表項目，e.g. 負債、現金流量等等
            第二層val是報表項目對應的數據
        """
        self.bs_info = InfoDict(sheet_name="資產負債表")  # 資產負債表
        self.is_info = InfoDict(sheet_name="損益表")  # 損益表
        self.cf_info = InfoDict(sheet_name="現金流量表")  # 現金流量表
        self.xx_info = InfoDict(sheet_name="財務比率表")  # 財務比率表

    @staticmethod
    def _read_tr(rows: List[bs4.element.Tag]) -> dict:
        """ 從 list of tr elements讀取資料，並轉換成以"項目"為key、"數值"為value的dict
        Parameters
        ----------
        rows : List[bs4.element.Tag]
            a list, 內容是從table找出來的tr

        Returns
        -------
        dict
            以"項目"為key、"數值"為value的dict
        """
        info_dict = {}
        for row in rows:
            key = ""
            for ele in row.contents:
                if key not in info_dict.keys():
                    try:
                        if ele.nobr:  # 現金比率表裡面有公式藏在text
                            key = ele.nobr.text
                        else:
                            key = ele.text
                    except:
                        break
                    info_dict[key] = []
                else:
                    info_dict[key].append(ele.text)
        return info_dict

    def load_table_info(self,
                        soup: BeautifulSoup,
                        sheet_name: str,
                        time_scale: str,
                        find_table_element: str = "b1 p4_4 r0_10 row_mouse_over") -> None:
        """ 從報表讀取資料，存入私有變數
        Parameters
        ----------
        soup : BeautifulSoup
            透過bs4 parse的財務報表資訊
        sheet_name : str
            one of ["資產負債表", "損益表", "現金流量表", "財務比率表"]
        time_scale : str
            依照sheet_name而有不同的時間尺度:
            資產負債表: one of ["BS_M_YEAR"(年度), "BS_M_QUAR"(季度)]
            損益表: one of ["IS_M_YEAR"(年度), "IS_M_QUAR"(單季), "IS_M_QUAR_ACC"(累季)]
            現金流量表: one of ["CF_M_YEAR"(年度), "CF_M_QUAR"(單季), "CF_M_QUAR_ACC"(累季)]
            財務比率表: one of ["XX_M_YEAR"(年度), "XX_M_QUAR"(單季), "XX_M_QUAR_ACC"(累季)]
        find_table_element : str, optional
            觀察goodinfo原始碼找到含有欲抽取資訊的table class，注意這一項會隨著網站前端變更而導致爬不到東西
            ver. 1: <table class="solid_1_padding_4_4_tbl">
            ver. 2: <table class="b1 p4_4 r0_10 row_mouse_over">

        Returns
        -------
        None
            存入私有變數，key為time, value為self._read_tr抽出的info_dict
        """
        table = soup.find("table", {"class": find_table_element})
        try:
            rows = table.findAll("tr")
        except:
            raise AttributeError("請檢查soup.contents，若是因爬蟲太頻繁而被鎖的話，請稍後再嘗試；"
                                 "若不是的話，請檢查find_table_element是否需要變更，請前往goodinfo報表處檢查table class是否變更")
        if sheet_name == "損益表":
            self.is_info.content[time_scale] = self._read_tr(rows)
        elif sheet_name == "資產負債表":
            self.bs_info.content[time_scale] = self._read_tr(rows)
        elif sheet_name == "現金流量表":
            self.cf_info.content[time_scale] = self._read_tr(rows)
        elif sheet_name == "財務比率表":
            self.xx_info.content[time_scale] = self._read_tr(rows)
        else:
            raise ValueError('請輸入one of ["資產負債表", "損益表", "現金流量表", "財務比率表"]')


class GoodInfoSeleniumCrawler:
    """
    此類別透過selenium套件抓取goodinfo上的報表資訊，需要使用者安裝瀏覽器driver
    """
    def __init__(self, stock_id: int):
        self.stock_id = stock_id
        self.th = TableHandler()
        self.browser = webdriver.Chrome('./chromedriver')

        url = "https://goodinfo.tw/StockInfo/StockDetail.asp?STOCK_ID={}".format(stock_id)
        self.browser.get(url)
        self.browser.implicitly_wait(5)

    def _go_to_button(self, sheet_name: str = "資產負債表") -> None:
        """ 前往某表的按鈕
        Parameters
        ----------
        sheet_name : str, optional
            one of ["資產負債表", "損益表", "現金流量表", "財務比率表"].
            The default is "資產負債表".
        """
        # 按下前往表的按鈕，表目前都在<a><\a>元素之間
        go_button = self.browser.find_element_by_xpath("//a[text()='{0}']".format(sheet_name))
        go_button.click()
        sleep(3)  # 等三秒讓網頁載入資訊

    def _select_time_list(self, time_scale: str) -> None:
        """ 在某表之下選擇時間尺度
        Parameters
        ----------
        time_scale : str
            依照sheet_name而有不同的時間尺度:
            資產負債表: one of ["BS_M_YEAR"(年度), "BS_M_QUAR"(季度)]
            損益表: one of ["IS_M_YEAR"(年度), "IS_M_QUAR"(單季), "IS_M_QUAR_ACC"(累季)]
            現金流量表: one of ["CF_M_YEAR"(年度), "CF_M_QUAR"(單季), "CF_M_QUAR_ACC"(累季)]
            財務比率表: one of ["XX_M_YEAR"(年度), "XX_M_QUAR"(單季), "XX_M_QUAR_ACC"(累季)]
        """
        # 找出合併報表下拉選單
        time_select = Select(self.browser.find_element_by_id("RPT_CAT"))
        time_select.select_by_value(time_scale)
        sleep(3)  # 等三秒讓網頁載入資訊

    def load_sheet_info(self, sheet_name: str = "資產負債表") -> None:
        """ 自動操控chrome driver:
                goodinfo首頁 -> 按按鈕前往報表 -> 下拉式選單選擇時間尺度
        Parameters
        ----------
        sheet_name : str
            one of ["資產負債表", "損益表", "現金流量表", "財務比率表"].
            The default is "資產負債表".
        """
        sheet_time = consolidated_time_sacles[sheet_name]
        logger.info("前往報表: {}".format(sheet_name))
        self._go_to_button(sheet_name)
        for consolidated_sheet_name_and_time_scale, time_scale_eng in sheet_time.items():
            logger.info("選取時間尺度: {}".format(consolidated_sheet_name_and_time_scale))
            self._select_time_list(time_scale_eng)
            soup = BeautifulSoup(self.browser.page_source, "html.parser")
            soup.encoding = 'utf-8'
            logger.info("抓取資料: {}".format(consolidated_sheet_name_and_time_scale))
            self.th.load_table_info(soup, sheet_name=sheet_name, time_scale=time_scale_eng)

    def dump_sheet_info(self, sheet_name: str, path: str) -> None:
        """
        Parameters
        ----------
        sheet_name : 報表中文名稱
        path : 儲存報表pkl檔案的資料夾位置
        """
        if sheet_name == "損益表":
            joblib.dump(self.th.is_info, path)
        elif sheet_name == "資產負債表":
            joblib.dump(self.th.bs_info, path)
        elif sheet_name == "現金流量表":
            joblib.dump(self.th.cf_info, path)
        elif sheet_name == "財務比率表":
            joblib.dump(self.th.xx_info, path)
        else:
            raise ValueError('請輸入one of ["資產負債表", "損益表", "現金流量表", "財務比率表"]')


class AJAXHeaders:
    """
    透過直接發送request的方式抓取goodinfo資訊時所需的header，需與GoodInfoAJAXCrawler配合使用
    """
    def __init__(self, stock_id: int, sheet_name: str = "資產負債表"):
        ajax_headers = {
            "資產負債表": "https://goodinfo.tw/StockInfo/StockFinDetail.asp?RPT_CAT=BS_M_QUAR&STOCK_ID={}".format(stock_id),
            "損益表": "https://goodinfo.tw/StockInfo/StockFinDetail.asp?RPT_CAT=BS_M_QUAR&STOCK_ID={}".format(stock_id),
            "現金流量表": "https://goodinfo.tw/StockInfo/StockFinDetail.asp?RPT_CAT=CF_M_QUAR_ACC&STOCK_ID={}".format(
                stock_id),
            "財務比率表": "https://goodinfo.tw/StockInfo/StockFinDetail.asp?RPT_CAT=XX_M_QUAR_ACC&STOCK_ID={}".format(
                stock_id),
        }
        self._user_agent = UserAgent()
        self._content_type = 'application/x-www-form-urlencoded'
        self._X_Requested_With = 'XMLHttpRequest'
        self._origin = 'https://goodinfo.tw'
        self._referer = ajax_headers[sheet_name]
        self._accept_language = 'zh-TW,zh;q=0.9'
        self._accept_encoding = 'gzip,deflate,br'
        self._sec_ch_ua = '"Not;A Brand";v = "99", "Google Chrome";v = "91", "Chromium";v = "91"'
        self._sec_ch_ua_mobile = '?0'
        self._sec_fetch_dest = 'empty'
        self._sec_fetch_mode = 'cors'
        self._sec_fetch_site = 'same - origin'

    def get_headers(self) -> Dict[str, str]:
        """
        header的getter
        Returns
        -------
        包含header資訊的dict
        """
        headers = {'user-agent': self._user_agent.random,
                   'content-type': self._content_type,
                   "X-Requested-With": self._X_Requested_With,
                   'referer': self._referer,
                   'accept-language': self._accept_language,
                   'accept-encoding': self._accept_encoding,
                   'origin': self._origin,
                   'sec-ch-ua': self._sec_ch_ua,
                   'sec-ch-ua-mobile': self._sec_ch_ua_mobile,
                   'sec-fetch-dest': self._sec_fetch_dest,
                   'sec-fetch-mode': self._sec_fetch_mode,
                   'sec-fetch-site': self._sec_fetch_site,
                   }
        return headers

    headers = property(fget=get_headers)


class GoodInfoAJAXCrawler:
    """
    透過直接發送request的方式抓取goodinfo資訊，需要與AJAXHeaders配合使用
    """
    def __init__(self, stock_id: int):
        self.stock_id = stock_id
        self.th = TableHandler()
        self.url = 'https://goodinfo.tw/StockInfo/StockFinDetail.asp'

    def load_sheet_info(self, sheet_name: str = "資產負債表") -> None:
        """ 讀取報表資訊
        Parameters
        ----------
        sheet_name : str
            one of ["資產負債表", "損益表", "現金流量表", "財務比率表"].
            The default is "資產負債表".
        """
        sheet_time = consolidated_time_sacles[sheet_name]
        logger.info("前往報表: {}".format(sheet_name))
        for consolidated_sheet_name_and_time_scale, time_scale_eng in sheet_time.items():
            headers = AJAXHeaders(stock_id=self.stock_id, sheet_name=sheet_name).headers  # 每次隨機更換user-agent
            print(headers)
            params = {
                'STEP': 'DATA',
                'STOCK_ID': str(self.stock_id),
                'RPT_CAT': time_scale_eng,
                'QRY_TIME': str(datetime.now().year),
            }
            logger.info("選取時間尺度: {}".format(consolidated_sheet_name_and_time_scale))
            sleep(random.randint(3, 15))  # 每次隨機更換request間隔
            response = requests.post(self.url, headers=headers, params=params)
            soup = BeautifulSoup(response.content, "html.parser")
            soup.encoding = 'utf-8'
            logger.info("抓取資料: {}".format(consolidated_sheet_name_and_time_scale))
            self.th.load_table_info(soup, sheet_name=sheet_name, time_scale=time_scale_eng)

    def dump_sheet_info(self, sheet_name: str, path: str) -> None:
        """
        Parameters
        ----------
        sheet_name : 報表中文名稱
        path : 儲存報表pkl檔案的資料夾位置
        """
        if sheet_name == "損益表":
            joblib.dump(self.th.is_info, path)
        elif sheet_name == "資產負債表":
            joblib.dump(self.th.bs_info, path)
        elif sheet_name == "現金流量表":
            joblib.dump(self.th.cf_info, path)
        elif sheet_name == "財務比率表":
            joblib.dump(self.th.xx_info, path)
        else:
            raise ValueError('請輸入one of ["資產負債表", "損益表", "現金流量表", "財務比率表"]')
