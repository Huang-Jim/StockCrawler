from datetime import datetime
import json
import os

from application.general_utils.utils import create_dir
from application.structures.plot_struct import PlotIndexConfig


class GeneralConfig:
    def __init__(self, stock_id: int, root: str = "./"):
        self.stock_id = stock_id
        self.DIR = "{}_{}".format(stock_id, datetime.now().strftime("%m_%d"))  # 必以個股代碼_月份_日期作為資料夾名稱
        self.DIR = os.path.join(root, self.DIR)
        create_dir(dir_name=self.DIR)
        self.BS_DATA_PATH = os.path.join(self.DIR, "bs_dict.pkl")
        self.IS_DATA_PATH = os.path.join(self.DIR, "is_dict.pkl")
        self.CF_DATA_PATH = os.path.join(self.DIR, "cf_dict.pkl")
        self.XX_DATA_PATH = os.path.join(self.DIR, "xx_dict.pkl")


class PlotIndexConfigFactory:
    """
    讀取index.json檔案，並將每個指標轉成PlotIndexConfig物件存放在index_dict中
    外部則透過index取用指定的PlotIndexConfig物件
    """
    def __init__(self, index_json_path: str = "./index.json"):
        self.index_dict = {}
        with open(index_json_path, 'r', encoding='utf-8') as f:
            indexes = json.load(f)
        for ind in indexes.keys():
            self.index_dict[ind] = PlotIndexConfig(indexes[ind])

    def __call__(self, index):
        return self.index_dict[index]
