import os
import json
import datetime as dt
import pandas as pd
from enum import Enum
from typing import Any, Optional, Generator
from collections import defaultdict
from dataclasses import dataclass, field
from pandas import DataFrame



class Category(Enum):
    BROWSER = 'browser'
    DELETED = 'deleted'
    LNK = 'lnk'
    MESSENGER = 'messenger'
    PREFETCH = 'prefetch'
    USB = 'usb'


class DataKeys:
    def __init__(self):
        self.browser_keys = set(('collected_files', 'collection_time', 'detailed_files', 'discovered_profiles', 'statistics', 'temp_directory'))
        self.deleted_keys = set(('data_sources', 'mft_deleted_files', 'recycle_bin_files', 'statistics'))
        self.lnk_keys = set(('lnk_files', 'search_directories'))
        self.messenger_keys = set(['messenger_data'])
        self.prefetch_keys = set(['prefetch_files'])
        self.usb_keys = set(['usb_devices'])
    
    def get_data_keys(self, category: Category) -> set:
        mapping = {
            Category.BROWSER: self.browser_keys,
            Category.DELETED: self.deleted_keys,
            Category.LNK: self.lnk_keys,
            Category.MESSENGER: self.messenger_keys,
            Category.PREFETCH: self.prefetch_keys,
            Category.USB: self.usb_keys
        }
        
        if category in mapping:
            return mapping[category]
        else:
            print(f"Category: {category}, Type: {type(category)}")
            raise TypeError


@dataclass
class ResultDataFrame:
    name:str
    data:DataFrame
    subname:str = field(default_factory=str)


@dataclass
class ResultDataFrames:
    data:list[ResultDataFrame] = field(default_factory=list)

    def add(self, name:str, data:DataFrame, subname=str()):
        if not name:
            raise NameError
        self.data.append(ResultDataFrame(name, data, subname if subname else ""))


class Logger:
    def __init__(self, name) -> None:
        self.name = name
    
    def log(self, message) -> None:
        time = dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        template = f"[{time}] {self.name} - {message}"
        print(template)


class BaseDataEncoder:
    CHUNK_SIZE = 10000

    def __init__(self):
        self.category: Category
        self.success_file_list = []
        self.datas: dict[str, list[DataFrame]] = defaultdict(list)
        self.blacklist: list = []
        self.whitelist: list = []
        self.logger = Logger("DataEncoder")


    def _validate_data_keys(self, keys: set) -> bool:
        _keys = DataKeys().get_data_keys(self.category)
        return keys.issubset(_keys)
        
    def _validate_data(self, data: dict) -> bool:
        if not data:
            self.logger.log("There is no data to process.")
            raise NotImplementedError
        
        if not self._validate_data_keys(set(data.keys())):
            self.logger.log("Data key is not correct.")
            raise NotImplementedError

        return True
    
    def get_result_dfs(self) -> ResultDataFrames:
        return ResultDataFrames()
        
    
    def convert_data(self, data: dict) -> bool:
        self.datas.clear()
        self.data = data
        self._validate_data(data)
        return True

    def _optimize_df_types(self, df: DataFrame) -> DataFrame:
        for col in df.columns:
            if df[col].dtype == 'object':
                try:
                    num_unique_values = df[col].nunique()
                    num_total_values = len(df[col])
                    if num_unique_values / num_total_values < 0.5:
                        df[col] = df[col].astype('category')
                except:
                    pass
            else:
                df[col] = pd.to_numeric(df[col], downcast='integer')
                df[col] = pd.to_numeric(df[col], downcast='float')
        return df

    def _dict_data_to_df(self, first_depth:str) -> DataFrame:
        dict_data = self.data.get(first_depth, {})
        df = pd.DataFrame([dict_data])
        return self._optimize_df_types(df)
    
    def _list_data_to_df(self, first_depth:str) -> Generator[DataFrame, None, None]:
        data = self.data.get(first_depth, [])
        
        for i in range(0, len(data), self.CHUNK_SIZE):
            chunk = data[i:i + self.CHUNK_SIZE]
            processed_chunk = [self._flatten_dict(item) for item in chunk]
            df = pd.DataFrame(processed_chunk)
            yield self._optimize_df_types(df)

    
    def _flatten_dict(self, obj: Any, parent_key: str = "", sep: str = "__") -> dict[str, Any]:
        flat: dict[str, Any] = {}
        if isinstance(obj, dict):
            for k, v in obj.items():
                if k == "execution_times":
                    continue
                if k == "last_run_times":
                    # 리스트를 8개의 고정된 슬롯으로 변환 (0-7)
                    for slot in range(8):
                        if slot < len(v) and v[slot] is not None:
                            # 데이터가 있는 경우
                            flat[f"{k}_{slot+1}"] = v[slot]
                        else:
                            # 데이터가 없는 경우 None으로 채움
                            flat[f"{k}_{slot+1}"] = None
                    continue
                new_key = f"{parent_key}{sep}{k}" if parent_key else k
                if isinstance(v, dict):
                    flat.update(self._flatten_dict(v, new_key, sep))
                elif isinstance(v, list):
                    flat[new_key] = json.dumps(v, ensure_ascii=False)
                else:
                    flat[new_key] = v
        else:
            flat[parent_key or "value"] = json.dumps(obj, ensure_ascii=False) if isinstance(obj, list) else obj
        return flat
    
    def _update_datas(self, filename: str, df: DataFrame):
        self.datas[filename].append(df)

    def log_memory_usage(self):
        self.logger.log("--- Memory Usage Report ---")
        total_usage = 0
        for name, df_chunks in self.datas.items():
            chunk_usage = sum(df.memory_usage(deep=True).sum() for df in df_chunks)
            chunk_usage_mb = chunk_usage / (1024 * 1024)
            total_usage += chunk_usage_mb
            self.logger.log(f"DataFrame '{name}': {chunk_usage_mb:.2f} MB")
        self.logger.log(f"Total DataFrame memory usage: {total_usage:.2f} MB")
        self.logger.log("---------------------------")


class DataSaver:
    def __init__(self, directory=None) -> None:
        self.logger = Logger("DataSaver")
        self.result_dir = "./data/result"
        if directory:
            self.set_result_dir(directory)
        else:
            self.logger.log("Data will be saved to Default directory")
            self._check_result_dir()
    
    def _check_result_dir(self) -> None:
        if not os.path.exists(self.result_dir):
            os.makedirs(self.result_dir, exist_ok=True)
    
    def set_result_dir(self, directory:str) -> None:
        self.result_dir = directory
        self._check_result_dir()

    def save_data_to_csv(self, filename:str, data:DataFrame, subname="") -> str:
        if not filename:
            raise NameError
        filename = subname+"."+filename if subname else filename
        file_path = os.path.join(self.result_dir, f"{filename}.csv")
        try:
            data.to_csv(file_path)
        except Exception as e:
            self.logger.log(f"Unknown Error: {e}")
            raise Exception
        
        return file_path
    
    def save_all(self, result:ResultDataFrames) -> None:
        for item in result.data:
            save = self.save_data_to_csv(item.name, item.data, item.subname)
            self.logger.log(save)
    