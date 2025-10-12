import pandas as pd
from ..core import BaseDataEncoder, ResultDataFrames, Category
# from ..utils import memory_tracker


class PrefetchEncoder(BaseDataEncoder):
    def __init__(self):
        super().__init__()
        self.category=Category.PREFETCH

    def get_result_dfs(self) -> ResultDataFrames:
        result = super().get_result_dfs()
        for key, df_chunks in self.datas.items():
            if df_chunks:
                final_df = pd.concat(df_chunks, ignore_index=True)
                result.add(key, final_df)
        return result
        
    # @memory_tracker
    def convert_data(self, data: dict) -> bool:
        super().convert_data(data)
        for first_depth in list(data.keys()):  # dictionary iteration 문제 해결
            match first_depth:
                case "collection_info":
                    df = self._dict_data_to_df(first_depth)
                    self._update_datas("collection_info", df)
                case "prefetch_files":
                    for df_chunk in self._list_data_to_df(first_depth):
                        self._update_datas("prefetch_files", df_chunk)
                case _:
                    self.logger.log(first_depth)
                    pass
        
        # self.log_memory_usage()
        return True
    
