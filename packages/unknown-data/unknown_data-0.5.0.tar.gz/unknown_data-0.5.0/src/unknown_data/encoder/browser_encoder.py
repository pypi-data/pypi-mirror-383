import pandas as pd
from datetime import datetime, timezone
from ..core import BaseDataEncoder, ResultDataFrames, Category
# from ..utils import memory_tracker


class BrowserDataEncoder(BaseDataEncoder):
    # WebKit timestamp를 포함하는 테이블명과 해당 컬럼명 매핑
    WEBKIT_TIME_COLUMNS = {
        # 방문 기록 (Visit History)
        'urls': ['last_visit_time'],
        'visits': ['visit_time'],
        'visited_links': [],  # visited_links는 WebKit 타임스탬프가 없음
        
        # 다운로드 기록 (Download History)
        'downloads': ['start_time', 'end_time', 'last_access_time'],
        
        # 검색 기록 (Search History)
        'keywords': ['date_created', 'last_visited', 'last_modified'],
        
        # 기타 브라우저 데이터
        'cookies': ['creation_utc', 'last_access_utc', 'expires_utc', 'last_update_utc'],
        'logins': ['date_created', 'date_last_used', 'date_received', 'date_password_modified', 'date_last_filled'],
        'insecure_credentials': ['create_time'],
        
        # 방문 맥락 정보 (Visit Context)
        'context_annotations': [],  # duration_since_last_visit는 마이크로초이지만 이미 숫자 형태이므로 변환 불필요
        
        # 레거시 테이블명 (대소문자 구분)
        'History': ['last_visit_time', 'visit_time'],
        'Cookies': ['creation_utc', 'last_access_utc', 'expires_utc'],
    }
    
    # Unix timestamp (초 단위)를 포함하는 테이블명과 해당 컬럼명 매핑
    UNIX_TIME_COLUMNS = {
        'autofill': ['date_created', 'date_last_used'],
    }
    
    def __init__(self) -> None:
        super().__init__()
        self.category=Category.BROWSER
        self.binary_data_list: list = []
    
    @staticmethod
    def _webkit_to_datetime(webkit_timestamp):
        """
        WebKit 타임스탬프를 datetime으로 변환
        WebKit epoch: 1601-01-01 00:00:00 UTC
        Chrome/Edge 모두 지원
        
        Chrome: 마이크로초 단위 (13-17자리)
        Edge: 100나노초 단위 (18자리 이상)
        
        Note: 초 단위까지만 반환 (마이크로초 버림)
        """
        if pd.isna(webkit_timestamp) or webkit_timestamp == 0:
            return None
        try:
            timestamp_int = int(webkit_timestamp)
            
            # Edge는 100나노초 단위를 사용 (18자리 이상)
            # 18자리 이상이면 Edge 형식으로 간주
            if timestamp_int >= 100000000000000000:  # 10^17 (18자리)
                # Edge: 100나노초 단위 -> 마이크로초로 변환
                timestamp_int = timestamp_int // 10
            
            # WebKit timestamp는 1601-01-01부터의 마이크로초
            # Unix timestamp는 1970-01-01부터의 초
            # 차이: 11644473600초 (369년)
            unix_timestamp = int((timestamp_int / 1_000_000) - 11644473600)  # 정수로 변환 (초 단위)
            return datetime.fromtimestamp(unix_timestamp, tz=timezone.utc)
        except (ValueError, OSError, OverflowError, TypeError):
            return None
    
    @staticmethod
    def _unix_to_datetime(unix_timestamp):
        """
        Unix 타임스탬프 (초)를 datetime으로 변환
        """
        if pd.isna(unix_timestamp) or unix_timestamp == 0:
            return None
        try:
            timestamp_int = int(unix_timestamp)
            return datetime.fromtimestamp(timestamp_int, tz=timezone.utc)
        except (ValueError, OSError, OverflowError, TypeError):
            return None
    
    def _convert_webkit_columns(self, df: pd.DataFrame, table_name: str) -> pd.DataFrame:
        """
        데이터프레임의 WebKit/Unix 타임스탬프 컬럼을 datetime으로 변환 (원본 컬럼 대체)
        """
        # 빈 데이터프레임 처리
        if df.empty:
            return df
        
        # 테이블명에서 브라우저명 제거 (예: "chrome.urls" -> "urls")
        base_table_name = table_name.split('.')[-1] if '.' in table_name else table_name
        
        # WebKit 타임스탬프 변환 (원본 컬럼에 덮어쓰기)
        webkit_columns = self.WEBKIT_TIME_COLUMNS.get(base_table_name, [])
        for col in webkit_columns:
            if col in df.columns:
                df[col] = df[col].apply(self._webkit_to_datetime)
                self.logger.log(f"Converted WebKit {table_name}.{col} to datetime")
        
        # Unix 타임스탬프 변환 (원본 컬럼에 덮어쓰기)
        unix_columns = self.UNIX_TIME_COLUMNS.get(base_table_name, [])
        for col in unix_columns:
            if col in df.columns:
                df[col] = df[col].apply(self._unix_to_datetime)
                self.logger.log(f"Converted Unix {table_name}.{col} to datetime")
        
        return df

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
                
                # WebKit 타임스탬프 변환 적용
                df = self._convert_webkit_columns(df, key)
                
                filename = f"{browser}.{key}"

                self._update_datas(filename, df)
        binary_df = pd.DataFrame(self.binary_data_list)
        binary_df = self._optimize_df_types(binary_df)
        self._update_datas("binary", binary_df)
