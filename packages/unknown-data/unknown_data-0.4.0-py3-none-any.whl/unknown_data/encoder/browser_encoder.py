import pandas as pd
from ..core import BaseDataEncoder, ResultDataFrames, Category
# from ..utils import memory_tracker


class BrowserDataEncoder(BaseDataEncoder):
    def __init__(self) -> None:
        super().__init__()
        self.category=Category.BROWSER
        self.binary_data_list: list = []

    def get_result_dfs(self) -> ResultDataFrames:
        result = super().get_result_dfs()
        for key, df_chunks in self.datas.items():
            if df_chunks:
                final_df = pd.concat(df_chunks, ignore_index=True)
                result.add(name=key, data=final_df)
        return result

    # 데이터처리를 총괄하며 외부에서 호출하는 함수
    # @memory_tracker
    def convert_data(self, data: dict) -> bool:
        super().convert_data(data)
        for first_depth in self.data.keys():
            match first_depth:
                case "collected_files":
                    # 수집한 데이터 명세 -> binary file은 제외
                    self._collected_files(first_depth)
                case "collection_time":
                    pass
                case "detailed_files":
                    files_data = self.data[first_depth]
                    self._detailed_files(files_data)
                case "discovered_profiles":
                    self._discovered_profiles(first_depth)
                case "statistics":
                    self._statistics_data(first_depth)
                case "temp_directory":
                    pass
                case _:
                    print(first_depth)

        # self.log_memory_usage()
        return True
    
    def _collected_files(self, first_depth):
        list_data = self.data[first_depth]
        self.success_file_list.extend([i["file_name"] for i in list_data if i["success"] and not i["file_type"] == "binary"])
        df = pd.DataFrame([i for i in list_data if i["success"] and not i["file_type"] == "binary"])
        df = self._optimize_df_types(df)
        filename = "browser_collected_files"
        self._update_datas(filename, df)

    def _discovered_profiles(self, first_depth):
        list_data = self.data.get(first_depth)
        df = pd.DataFrame(list_data)
        df = self._optimize_df_types(df)
        filename = "browser_discovered_profiles"
        self._update_datas(filename, df)
    
    def _statistics_data(self, first_depth):
        stat_data = self.data[first_depth]
        df = pd.DataFrame([stat_data])
        df = self._optimize_df_types(df)
        filename = "browser_statistics"
        self._update_datas(filename, df)
    
    def _detailed_files(self, files_data):
        for file in files_data:
            if not file.get("success"):
                self.logger.log(f"{file.get('file_name')} failed")
                continue

            file_path = file["file_path"]
            browser = file_path.split("/")[6]
            profile = file_path.split("/")[8]

            if file.get("file_type") == "binary":
                self.binary_data_list.append(file)
                continue
            
            table_names = file.get("table_names")
            if not table_names:
                self.logger.log(f"{file.get('file_name')} no data to process")
                continue
            
            sql_data = file["sqlite_data"]
            for key, val in sql_data.items():
                if not val or key == "meta":
                    continue
                df = pd.DataFrame(val, index=None)
                df = self._optimize_df_types(df)
                filename = f"{browser}.{key}"

                self._update_datas(filename, df)
        binary_df = pd.DataFrame(self.binary_data_list)
        binary_df = self._optimize_df_types(binary_df)
        self._update_datas("binary", binary_df)
