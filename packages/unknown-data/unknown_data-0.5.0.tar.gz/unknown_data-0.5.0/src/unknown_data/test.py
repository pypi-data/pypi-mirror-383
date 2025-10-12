from typing import List, Optional, Dict, Tuple, Any
from .loader import DataLoader
from .loader.loader import Config_db
from .core import Category, BaseDataEncoder, ResultDataFrames
from .encoder import Encoder
from pandas import DataFrame
import pandas as pd
import logging


class TestHelper:
    """테스트 및 개발용 헬퍼 클래스"""
    
    def __init__(self, db_config: Config_db):
        self.db_config = db_config
        self.loader = DataLoader()
        self.logger = logging.getLogger(__name__)
        self.loader.set_database(self.db_config)
        
    def get_task_ids(self, limit: Optional[int] = None) -> List[str]:
        """
        데이터베이스에서 task ID 목록을 가져옵니다.
        
        Args:
            limit: 반환할 최대 task 수 (None이면 전체)
            
        Returns:
            최신 순으로 정렬된 task ID 목록
            
        Raises:
            ConnectionError: 데이터베이스 연결 실패
        """
        try:
            task_ids = self.loader.database_task_data_load()
            
            if limit is not None:
                task_ids = task_ids[:limit]
                
            return task_ids
            
        except Exception as e:
            self.logger.error(f"Failed to get task IDs: {e}")
            raise ConnectionError(f"데이터베이스에서 task ID를 가져올 수 없습니다: {e}")
    
    def load_data(self, task_id: str, category: Category) -> dict:
        """
        지정된 task와 category의 원본 데이터를 로드합니다.
        
        Args:
            task_id: 작업 ID
            category: 데이터 카테고리
            
        Returns:
            원본 JSON 데이터
            
        Raises:
            ValueError: 데이터를 찾을 수 없는 경우
        """
        try:
            return self.loader.database_data_load(task_id, category)
        except Exception as e:
            self.logger.error(f"Failed to load data for {task_id}/{category.value}: {e}")
            raise ValueError(f"데이터 로드 실패 [{task_id}/{category.value}]: {e}")
    
    def encode_data(self, data: dict, category: Category, 
                   fresh_encoder: bool = True) -> BaseDataEncoder:
        """
        데이터를 인코딩합니다.
        
        Args:
            data: 원본 데이터
            category: 데이터 카테고리  
            fresh_encoder: 새로운 encoder 인스턴스 사용 여부
            
        Returns:
            인코딩된 데이터를 포함한 encoder 인스턴스
        """
        encoder = Encoder() if fresh_encoder else getattr(self, '_encoder', Encoder())
        if not fresh_encoder:
            self._encoder = encoder
            
        return encoder.convert_data(data, category)
    
    def get_encoded_results(self, task_id: str, category: Category,
                          fresh_encoder: bool = True) -> ResultDataFrames:
        """
        데이터를 로드하고 인코딩하여 최종 결과를 반환합니다.
        
        Args:
            task_id: 작업 ID
            category: 데이터 카테고리
            fresh_encoder: 새로운 encoder 인스턴스 사용 여부
            
        Returns:
            최종 DataFrame 결과들 (ResultDataFrames 객체)
        """
        data = self.load_data(task_id, category)
        encoder = self.encode_data(data, category, fresh_encoder)
        return encoder.get_result_dfs()
    
    def get_encoded_dataframes(self, task_id: str, category: Category,
                             fresh_encoder: bool = True) -> Dict[str, DataFrame]:
        """
        데이터를 로드하고 인코딩하여 DataFrame 딕셔너리로 반환합니다.
        
        Args:
            task_id: 작업 ID
            category: 데이터 카테고리
            fresh_encoder: 새로운 encoder 인스턴스 사용 여부
            
        Returns:
            {파일명: DataFrame} 딕셔너리
        """
        data = self.load_data(task_id, category)
        encoder = self.encode_data(data, category, fresh_encoder)
        
        # encoder.datas에서 최종 DataFrame들로 변환
        final_dfs = {}
        for key, df_list in encoder.datas.items():
            if df_list:  # 빈 리스트가 아닌 경우
                final_dfs[key] = pd.concat(df_list, ignore_index=True)
        
        return final_dfs
    
    def get_chunk_summary(self, task_id: str, category: Category) -> Dict[str, int]:
        """
        인코딩된 데이터의 청크 정보를 요약합니다.
        
        Args:
            task_id: 작업 ID
            category: 데이터 카테고리
            
        Returns:
            {파일명: 청크수} 딕셔너리
        """
        data = self.load_data(task_id, category)
        encoder = self.encode_data(data, category)
        
        return {key: len(df_list) for key, df_list in encoder.datas.items()}
    
    def process_all_categories(self, task_id: str, 
                             include_summary: bool = True) -> Dict[str, Any]:
        """
        모든 카테고리의 데이터를 처리합니다.
        
        Args:
            task_id: 작업 ID
            include_summary: 요약 정보 포함 여부
            
        Returns:
            카테고리별 처리 결과
        """
        results = {}
        
        for category in Category:
            try:
                if include_summary:
                    chunk_summary = self.get_chunk_summary(task_id, category)
                    total_chunks = sum(chunk_summary.values())
                    results[category.value] = {
                        'status': 'success',
                        'files': len(chunk_summary),
                        'total_chunks': total_chunks,
                        'chunk_details': chunk_summary
                    }
                else:
                    results[category.value] = self.get_encoded_results(task_id, category)
                    
            except Exception as e:
                results[category.value] = {
                    'status': 'error',
                    'error': str(e)
                }
                
        return results
    
    def memory_usage_report(self, task_id: str, category: Category) -> str:
        """
        메모리 사용량 리포트를 생성합니다.
        
        Args:
            task_id: 작업 ID
            category: 데이터 카테고리
            
        Returns:
            메모리 사용량 리포트 문자열
        """
        data = self.load_data(task_id, category)
        encoder = self.encode_data(data, category)
        
        # 메모리 사용량 계산
        encoder.log_memory_usage()
        
        return f"Memory report logged for {task_id}/{category.value}"


# 하위 호환성을 위한 레거시 함수들
def get_task_ids(loader: DataLoader, db_config: Config_db) -> List[str]:
    """레거시 함수 - TestHelper 사용을 권장합니다."""
    helper = TestHelper(db_config)
    return helper.get_task_ids()

def load_and_encode_data(task_id: str, category: Category, 
                        loader: DataLoader, encoder: Encoder) -> BaseDataEncoder:
    """레거시 함수 - TestHelper.encode_data 사용을 권장합니다.""" 
    data = loader.database_data_load(task_id, category)
    return encoder.convert_data(data, category)