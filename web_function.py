import logging
from typing import List, Union, Dict

import joblib

from application.postprocessing.info_dict_postproc import InfoDictProcessor
from application.general_utils.utils import if_refresh_data, if_sheets_exist
from config import GeneralConfig, PlotIndexConfigFactory
from crawler import GoodInfoSeleniumCrawler
from plot_utils import Ploter

logger = logging.getLogger(__name__)


def run_all(stock_id: int,
            select_item: str,
            int_item_list: List[str]) -> Union[None, Dict[str]]:
    # 匯入基本資料檔
    general_config = GeneralConfig(stock_id=stock_id, root="./")

    #
    info_dict_seq = ("資產負債表", "損益表", "現金流量表", "財務比率表")
    info_dict_path = (general_config.BS_DATA_PATH,
                      general_config.IS_DATA_PATH,
                      general_config.CF_DATA_PATH,
                      general_config.XX_DATA_PATH)
    #
    if if_refresh_data(dir_name=general_config.DIR) or not if_sheets_exist(dir_name=general_config.DIR):
        logger.info("因為現有資料太舊、資料夾不存在 或是 資料夾存在但報表資訊缺漏，所以重新抓取資料")
        goodinfo_crawler = GoodInfoSeleniumCrawler(general_config.stock_id)
        for sheet_name, path in zip(info_dict_seq, info_dict_path):
            goodinfo_crawler.load_sheet_info(sheet_name=sheet_name)  # 透過爬蟲讀取報表
            goodinfo_crawler.dump_sheet_info(sheet_name=sheet_name, path=path)  # 將報表以pkl檔存入disk
        goodinfo_crawler.browser.close()
    logger.info("讀取資料")
    bs_info = joblib.load(general_config.BS_DATA_PATH)
    is_info = joblib.load(general_config.IS_DATA_PATH)
    cf_info = joblib.load(general_config.CF_DATA_PATH)
    xx_info = joblib.load(general_config.XX_DATA_PATH)

    # 後處理
    logger.info("後處理")
    info_dict_processor = InfoDictProcessor()
    bs_info = info_dict_processor.postprocess(bs_info)
    is_info = info_dict_processor.postprocess(is_info)
    cf_info = info_dict_processor.postprocess(cf_info)
    xx_info = info_dict_processor.postprocess(xx_info)

    # 繪圖
    plot_index_factory = PlotIndexConfigFactory(index_json_path="index.json")
    ploter = Ploter(bs_info=bs_info, is_info=is_info, cf_info=cf_info, xx_info=xx_info, stock_id=stock_id)
    if_error = ploter.plot([plot_index_factory(select_item)], interested_item=int_item_list)
    return if_error