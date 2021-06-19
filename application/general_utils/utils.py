from datetime import datetime
import os


def is_float(value: str) -> bool:
    """
    檢驗一個str是否能被轉換成float
    Parameters
    ----------
    value : 字串

    Returns
    -------
    若value能被轉成float則return True，反之return False
    """
    try:
        float(value)
        return True
    except ValueError:
        return False


def if_refresh_data(dir_name: str,
                    root: str = "./",
                    ) -> bool:
    """
    以現有檔名比對日期，若太舊或是不存在就更新資料
    Parameters
    ----------
    dir_name : 資料夾名稱
    root : 放置資料夾的根目錄，預設為目前的路徑
    """
    basename = os.path.basename(dir_name)
    dir_date = int("".join(basename.split("_")))
    current_date = int("".join(datetime.now().strftime("%m_%d").split("_")))
    # 如果太舊、資料夾不存在或是資料夾存在但是是空的
    if dir_date < current_date or not os.path.isdir(os.path.join(root, dir_name)) or not os.listdir(dir_name):
        return True
    else:
        return False


def if_sheets_exist(dir_name: str,
                    root: str = "./",
                    ) -> bool:
    """
    比對資料夾內是否四種表都存在，僅以資料夾內的file數量是否為四來決定
    Parameters
    ----------
    dir_name : 資料夾名稱
    root : 放置資料夾的根目錄，預設為目前的路徑
    """
    if len(os.listdir(dir_name)) == 4:
        return True
    return False


def create_dir(dir_name: str,
               root: str = "./") -> None:
    """
    如果不存在dir_name時創建資料夾
    Parameters
    ----------
    dir_name : 資料夾名稱
    root : 放置資料夾的根目錄，預設為目前的路徑

    Returns
    -------

    """
    if not os.path.isdir(os.path.join(root, dir_name)):
        os.mkdir(os.path.join(root, dir_name))
