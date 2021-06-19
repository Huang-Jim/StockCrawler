from typing import List, Tuple, Dict, Sequence, Union

import numpy as np
from plotly.offline import plot
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from application.structures.sheet_struct import InfoDict
from application.structures.plot_struct import PlotIndexConfig


class Ploter:
    """
    繪製報表相關圖表
    """

    def __init__(self,
                 bs_info: InfoDict,
                 is_info: InfoDict,
                 cf_info: InfoDict,
                 xx_info: InfoDict,
                 stock_id: int) -> None:
        """ 初始化四張報表
        Parameters
        ----------
        bs_info : 資產負債表
        is_info : 損益表
        cf_info : 現金流量表
        xx_info : 財務比率表
        stock_id : 個股股市代碼

        Returns
        -------
        """
        # raise NotImplementedError
        self.bs_info = bs_info
        self.is_info = is_info
        self.cf_info = cf_info
        self.xx_info = xx_info
        self.stock_id = stock_id
        self._sheetname_2_info = {"資產負債表": self.bs_info,
                                  "損益表": self.is_info,
                                  "現金流量表": self.cf_info,
                                  "財務比率表": self.xx_info}

    @staticmethod
    def _add_bar(time_axis: List,
                 data_present_index: np.ndarray,
                 interested_item_data_dict: Dict[str, np.ndarray]
                 ) -> Tuple[List[go.Bar], List[Dict[str, Union[float, str, bool]]]]:
        # 計算每個成分在每個時間點上的加總，最後要加註在bar plot上
        totals = np.zeros(len(data_present_index))
        for k, v in interested_item_data_dict.items():
            totals += v
        total_labels = [{"x": x, "y": total + 0.5, "text": '%.2f' % total, "showarrow": False} for x, total
                        in zip(time_axis, totals)]
        # 生成bar物件
        traces = [go.Bar(name=k, x=time_axis, y=v) for k, v in interested_item_data_dict.items()]
        return traces, total_labels

    @staticmethod
    def _add_line(time_axis: List,
                  interested_item_data_dict: Dict[str, np.ndarray]
                  ) -> List:
        # 生成line物件
        traces = [go.Scatter(name=k, x=time_axis, y=v, mode='lines+markers') for k, v in
                  interested_item_data_dict.items()]
        return traces

    def get_trace(self,
                  interested_item=None,
                  time_scale: str = "BS_M_QUAR",
                  sheet_name: str = "資產負債表",
                  data_present_type: str = "絕對值",
                  mode: str = "bar") -> Tuple:
        if interested_item is None:
            interested_item = ["流動資產合計", "流動負債合計"]
        sheetname_2_timeaxis = {"資產負債表": ["資產", "負債", "股東權益"],
                                "損益表": ["本業獲利", "業外損益", "淨損益"],
                                "現金流量表": ["營業活動", "投資活動", "融資活動", "現金流量總計"],
                                "財務比率表": ["獲利能力", "獲利年成長率", "各項資產佔總資產比重", "資產季成長率", "資產年成長率"]}

        info_dict = self._sheetname_2_info[sheet_name].content[time_scale]
        time_axis = info_dict[sheetname_2_timeaxis[sheet_name][0]]  # 取出時間軸
        if sheet_name != "財務比率表":
            if data_present_type == "絕對值":
                data_present_index = np.arange(0, 2 * len(time_axis), 2)  # 絕對數值在偶數欄位
            else:
                data_present_index = np.arange(1, 2 * len(time_axis) - 1, 2)  # 百分比數值在奇數欄位
        else:  # 財務比率表只有percent，沒有絕對值
            data_present_index = np.arange(0, len(time_axis))

        # 從某一個想要觀察的指標的組成成分中取出資料
        interested_item_data_dict = {item: np.array(info_dict[item], dtype=np.float32)[data_present_index] for item
                                     in interested_item}

        bar_traces, line_traces, total_labels = [], [], []
        if mode == "bar":
            bar_traces, total_labels = self._add_bar(time_axis, data_present_index, interested_item_data_dict)
        if mode == "line":
            line_traces = self._add_line(time_axis, interested_item_data_dict)
        traces = bar_traces + line_traces
        return traces, total_labels

    def _check_interested_item(self,
                               sheet_name: str,
                               time_scale: str,
                               interested_item: List[str]) -> None:
        available_int_item = list(self._sheetname_2_info[sheet_name].content[time_scale].keys())
        forbiden_list = [ii for ii in interested_item if ii not in available_int_item]
        if forbiden_list:
            raise ValueError('欄位{}有誤，請確認輸入的欄位是否出現在"{}"科目內 \n'.format(forbiden_list, sheet_name))

    def plot(self,
             plot_index: Sequence[PlotIndexConfig],
             interested_item: List[str] = None,
             ):
        if len(plot_index) == 1:  # 只有一張圖
            plot_index = plot_index[0]
            try:
                self._check_interested_item(plot_index.sheet_name, plot_index.time_scale, interested_item)
            except ValueError as ve:
                return {'error': str(ve)}
            if not interested_item:
                interested_item = plot_index.interested_item
            fig = go.Figure()
            traces, total_labels = self.get_trace(
                interested_item=interested_item,
                time_scale=plot_index.time_scale,
                sheet_name=plot_index.sheet_name,
                data_present_type=plot_index.data_present_type,
                mode=plot_index.fig_args["mode"])
            for trace in traces:
                fig.add_trace(trace)
            fig.update_layout(annotations=total_labels,
                              barmode="stack",
                              title=plot_index.fig_args["title"],
                              xaxis_title=plot_index.fig_args["x_axis_name"],
                              yaxis_title=plot_index.fig_args["y_axis_name"],
                              )
            plot(fig, filename="{}".format(plot_index.fig_args["file_name"].format(self.stock_id)))

        elif len(plot_index) == 2:  # 要畫的兩張圖在不同的表
            fig = make_subplots(specs=[[{"secondary_y": True}]])
            total_trace, title, file_name = [], [], []
            for n_plot, ki in enumerate(plot_index):
                fig_args = ki.fig_args
                traces, total_labels = self.get_trace(
                    interested_item=ki.interested_item,
                    time_scale=ki.time_scale,
                    sheet_name=ki.sheet_name,
                    data_present_type=ki.data_present_type,
                    mode=fig_args["mode"])
                total_trace += traces
                title.append(fig_args["title"])
                file_name.append(fig_args["file_name"].format(self.stock_id))

            # 使兩張圖的X軸的長度一樣，且單位要一致
            trace_1_x = total_trace[0]["x"]
            trace_2_x = total_trace[1]["x"]
            trace_x_common = trace_1_x if len(trace_1_x) < len(trace_2_x) else trace_2_x
            # 把比較長的x ticks換成trace_x_common
            for n_plot, trace in enumerate(total_trace):
                trace["x"] = trace_x_common
                fig.add_trace(trace, secondary_y=bool(n_plot))
            fig.update_layout(
                title=" + ".join(title),
                xaxis_title=fig_args["x_axis_name"],
            )
            plot(fig, filename="{}".format("_".join(file_name)))

        else:
            raise ValueError("目前僅支援最多將兩種資料繪製在同一張圖的功能")
