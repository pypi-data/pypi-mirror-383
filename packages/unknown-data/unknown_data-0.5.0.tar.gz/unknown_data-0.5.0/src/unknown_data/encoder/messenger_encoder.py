import pandas as pd
from ..core import BaseDataEncoder, ResultDataFrames, Category
# from ..utils import memory_tracker


class MessengerEncoder(BaseDataEncoder):
    def __init__(self):
        super().__init__()
        self.category=Category.MESSENGER

    def get_result_dfs(self) -> ResultDataFrames:
        result = super().get_result_dfs()
        for key, df_chunks in self.datas.items():
            if df_chunks:
                final_df = pd.concat(df_chunks, ignore_index=True)
                result.add(key, final_df)
        return result

        
    # @memory_tracker
    def convert_data(self, data: dict) -> bool:
        try:
            super().convert_data(data)
            messenger_data = data.get("messenger_data")

            if not messenger_data:
                self.logger.log("No data to Process")
                raise FileNotFoundError

            for messenger_name in messenger_data.keys():
                datas = messenger_data[messenger_name]
                for key, val in datas.items():
                    match key:
                        case "files":
                            if isinstance(val, list):
                                for i in range(0, len(val), self.CHUNK_SIZE):
                                    chunk = val[i:i + self.CHUNK_SIZE]
                                    processed_chunk = [self._flatten_dict(item) if isinstance(item, dict) else item for item in chunk]
                                    df = pd.DataFrame(processed_chunk)
                                    df = self._optimize_df_types(df)
                                    self._update_datas(f"{messenger_name}.{key}", df)
                            else:
                                df = pd.DataFrame([val] if val else [])
                                df = self._optimize_df_types(df)
                                self._update_datas(f"{messenger_name}.{key}", df)
                        case _:
                            pass
            
            # self.log_memory_usage()
            return True
        except Exception as e:
            self.logger.log(e)
            return False
    
