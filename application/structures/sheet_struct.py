from typing import List, Iterator, Tuple


statement_chi_eng = {"資產負債表": "BS",
                     "損益表": "IS",
                     "現金流量表": "CF",
                     "財務比率表": "XX"}

consolidated_time_sacles = {"資產負債表": {"合併資產負債表-年度": "BS_M_YEAR", "合併資產負債表-季度": "BS_M_QUAR"},
                            "損益表": {"合併損益表-年度": "IS_M_YEAR", "合併損益表-單季": "IS_M_QUAR", "合併損益表-累季": "IS_M_QUAR_ACC"},
                            "現金流量表": {"合併現金流量表-年度": "CF_M_YEAR", "合併現金流量表-單季": "CF_M_QUAR", "合併現金流量表-累季": "CF_M_QUAR_ACC"},
                            "財務比率表": {"合併財務比率表-年度": "XX_M_YEAR", "合併財務比率表-單季": "XX_M_QUAR", "合併財務比率表-累季": "XX_M_QUAR_ACC"},
                            }


class InfoDict:
    """
    四種財報的資料結構
    """

    def __init__(self, sheet_name: str):
        """ 建立報表的init dict
        eng_name : 報表英文名稱
        content : 每張表的結構皆為兩層dict
                    第一層key是時間尺度, e.g. 季, 年或是累計季
                    第一層val是在當前時間尺度下的報表資訊
                    第二層key是報表項目，e.g. 負債、現金流量等等
                    第二層val是報表項目對應的數據
        """
        self.eng_name = statement_chi_eng[sheet_name]
        self.sheet_name = sheet_name
        self.time_sacles = consolidated_time_sacles[sheet_name]
        self.content = {t: None for t in self.time_sacles}

    def row_generator(self) -> Iterator[Tuple[str, str, List[str]]]:
        """

        Returns
        -------
        在報表中iter 每一個row的資料
        """
        for t_scale in self.time_sacles.values():
            for item, data in self.content[t_scale].items():
                yield t_scale, item, data
