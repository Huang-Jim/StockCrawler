class PlotIndexConfig:
    """
    將json定義的一個指標所需的內容物件化，並透過PlotIndexConfigFactory調用
    """
    def __init__(self, index_info: dict):
        try:
            self.index = index_info.pop("index")
            self.sheet_name = index_info.pop("sheet_name")
            self.time_scale = index_info.pop("time_scale")
            self.interested_item = index_info.pop("interested_item")
            self.data_present_type = index_info.pop("data_present_type")
            self.fig_args = index_info.pop("fig_args")
        except KeyError:
            raise KeyError("index.json中有缺失鍵值")
        if index_info:
            raise TypeError("無法判定的key: {}".format(index_info))
