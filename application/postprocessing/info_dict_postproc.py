from typing import Union, List
from copy import deepcopy

import numpy as np

from application.structures.sheet_struct import InfoDict
from application.general_utils import utils


class InfoDictProcessor:
    """
    將InfoDict做系列後處理
    """

    def __init__(self):
        pass

    @staticmethod
    def _replace_hiven(x: str) -> str:
        """
        將報表中的"-"替換成0，此"-"表示公司未提供的項目
        Parameters
        ----------
        x : 報表中的一格內容

        Returns
        -------
        x : 報表中的一格內容
        """
        if x == "-":  # 有一些是負數就不能取代掉，否則會變成正數
            return x.replace("-", "0")
        else:
            return x

    @staticmethod
    def _replace_comma(x: str) -> str:
        """
        把報表中數字裡面的","符號去除
        Parameters
        ----------
        x : 報表中的一格內容

        Returns
        -------
        x : 報表中的一格內容
        """
        return x.replace(",", "")

    @staticmethod
    def _str_2_float(x: str) -> Union[str, float]:
        """
        將x轉成float，若不行轉成float則保留為str
        Parameters
        ----------
        x : 報表中的一格內容

        Returns
        -------
        x : 報表中的一格內容
        """
        if utils.is_float(x):
            return float(x)
        else:
            return x

    def postprocess(self, info_dict: InfoDict) -> InfoDict:
        new_info_dict = deepcopy(info_dict)
        for t_scale, item, data in info_dict.row_generator():
            new_item = item.replace("\xa0", "")
            new_info_dict.content[t_scale][new_item] = [self._str_2_float(self._replace_hiven(self._replace_comma(x)))
                                                        for x in data]
        return new_info_dict


class CFProcessor:
    """
    處理各種有關現金流量表的指標之後製
    """

    def __init__(self, cf_info_dict: InfoDict):
        if cf_info_dict.sheet_name != "現金流量表":
            raise ValueError("此類別只接受現金流量表之處理")
        self.info_dict = cf_info_dict

    def calculate_fcf(self, time_scale: str = "CF_M_YEAR") -> List[float]:
        """
        計算Free cash flow(自由現金流量表)，公式=營業現金流+投資現金流
        Returns
        -------

        """
        cash_flows_from_operations = np.array(self.info_dict.content[time_scale]['營業活動之淨現金流入(出)'])
        cash_flows_from_investing = np.array(self.info_dict.content[time_scale]['投資活動之淨現金流入(出)'])
        free_cash_flow = cash_flows_from_operations + cash_flows_from_investing
        raise NotImplementedError
        # return free_cash_flow.tolist()
