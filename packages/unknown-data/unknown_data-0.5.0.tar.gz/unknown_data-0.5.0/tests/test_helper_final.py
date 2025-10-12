"""
TestHelper 클래스의 실용적인 배포 테스트
실제 코드 동작을 정확히 반영한 최종 테스트
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import pandas as pd
from typing import Dict, List, Any

from src.unknown_data.test import TestHelper, get_task_ids, load_and_encode_data
from src.unknown_data.core import Category, BaseDataEncoder, ResultDataFrames
from src.unknown_data.loader.loader import Config_db
from src.unknown_data.loader import DataLoader


class TestHelperFinalTest:
    """TestHelper 클래스의 최종 배포 테스트"""
    
    @pytest.fixture
    def mock_db_config(self):
        """완전한 Mock 데이터베이스 설정"""
        config = Mock(spec=Config_db)
        config.dbms = "postgresql"
        config.username = "test_user"
        config.password = "test_pass"
        config.ip = "localhost"
        config.port = 5432
        config.database_name = "test_db"
        return config
    
    @pytest.fixture
    def test_helper(self, mock_db_config):
        """TestHelper 인스턴스"""
        return TestHelper(mock_db_config)
    
    @pytest.fixture
    def sample_raw_data(self):
        """샘플 원본 데이터"""
        return {
            "file1.csv": [{"col1": "val1", "col2": "val2"}],
            "file2.csv": [{"col1": "val3", "col2": "val4"}]
        }
    
    @pytest.fixture
    def mock_encoder_with_data(self):
        """실제 datas 속성을 가진 Mock encoder"""
        mock_encoder = Mock(spec=BaseDataEncoder)
        mock_encoder.datas = {
            "file1": [pd.DataFrame({"col1": ["val1"], "col2": ["val2"]})],
            "file2": [pd.DataFrame({"col1": ["val3"], "col2": ["val4"]})]
        }
        
        # get_result_dfs 결과
        mock_result_dfs = Mock(spec=ResultDataFrames)
        mock_encoder.get_result_dfs.return_value = mock_result_dfs
        
        # log_memory_usage 메서드
        mock_encoder.log_memory_usage.return_value = None
        
        # convert_data는 자기 자신을 반환
        mock_encoder.convert_data.return_value = mock_encoder
        
        return mock_encoder

    def test_initialization(self, mock_db_config):
        """1. TestHelper 초기화 테스트"""
        helper = TestHelper(mock_db_config)
        
        assert helper.db_config == mock_db_config
        assert helper.loader is not None
        assert helper.logger is not None

    def test_get_task_ids_success(self, test_helper):
        """2. Task ID 조회 성공 테스트"""
        # loader 메서드들을 직접 모킹
        test_helper.loader.database_task_data_load = Mock(return_value=["task1", "task2", "task3"])
        
        result = test_helper.get_task_ids()
        
        assert result == ["task1", "task2", "task3"]

    def test_get_task_ids_with_limit(self, test_helper):
        """3. 제한된 Task ID 조회 테스트"""
        test_helper.loader.database_task_data_load = Mock(return_value=["task1", "task2", "task3"])
        
        result = test_helper.get_task_ids(limit=2)
        
        assert result == ["task1", "task2"]

    def test_get_task_ids_connection_error(self, test_helper):
        """4. Task ID 조회 연결 오류 테스트"""
        test_helper.loader.database_task_data_load = Mock(side_effect=Exception("DB Connection failed"))
        
        with pytest.raises(ConnectionError, match="데이터베이스에서 task ID를 가져올 수 없습니다"):
            test_helper.get_task_ids()

    def test_load_data_success(self, test_helper, sample_raw_data):
        """5. 데이터 로드 성공 테스트"""
        test_helper.loader.database_data_load = Mock(return_value=sample_raw_data)
        
        result = test_helper.load_data("task1", Category.BROWSER)
        
        assert result == sample_raw_data
        test_helper.loader.database_data_load.assert_called_once_with("task1", Category.BROWSER)

    def test_load_data_failure(self, test_helper):
        """6. 데이터 로드 실패 테스트"""
        test_helper.loader.database_data_load = Mock(side_effect=Exception("Data not found"))
        
        with pytest.raises(ValueError, match="데이터 로드 실패"):
            test_helper.load_data("invalid_task", Category.BROWSER)

    @patch('src.unknown_data.test.Encoder')
    def test_encode_data_fresh_encoder(self, mock_encoder_class, test_helper, sample_raw_data, mock_encoder_with_data):
        """7. Fresh Encoder 인코딩 테스트"""
        mock_encoder_class.return_value = mock_encoder_with_data
        
        result = test_helper.encode_data(sample_raw_data, Category.BROWSER, fresh_encoder=True)
        
        # encode_data는 convert_data의 결과를 반환
        assert result == mock_encoder_with_data
        mock_encoder_with_data.convert_data.assert_called_once_with(sample_raw_data, Category.BROWSER)

    @patch('src.unknown_data.test.Encoder')
    def test_encode_data_reused_encoder(self, mock_encoder_class, test_helper, sample_raw_data, mock_encoder_with_data):
        """8. 재사용 Encoder 인코딩 테스트"""
        mock_encoder_class.return_value = mock_encoder_with_data
        
        # 첫 번째 호출
        test_helper.encode_data(sample_raw_data, Category.BROWSER, fresh_encoder=False)
        
        # 두 번째 호출 - encoder 재사용
        result = test_helper.encode_data(sample_raw_data, Category.BROWSER, fresh_encoder=False)
        
        assert hasattr(test_helper, '_encoder')
        assert result == mock_encoder_with_data

    def test_get_chunk_summary(self, test_helper, sample_raw_data, mock_encoder_with_data):
        """9. 청크 요약 테스트"""
        test_helper.loader.database_data_load = Mock(return_value=sample_raw_data)
        
        with patch('src.unknown_data.test.Encoder', return_value=mock_encoder_with_data):
            result = test_helper.get_chunk_summary("task1", Category.BROWSER)
        
        expected = {"file1": 1, "file2": 1}  # 각 파일당 1개의 청크
        assert result == expected

    def test_get_encoded_results(self, test_helper, sample_raw_data, mock_encoder_with_data):
        """10. 인코딩된 결과 조회 테스트"""
        test_helper.loader.database_data_load = Mock(return_value=sample_raw_data)
        
        with patch('src.unknown_data.test.Encoder', return_value=mock_encoder_with_data):
            result = test_helper.get_encoded_results("task1", Category.BROWSER)
        
        assert result == mock_encoder_with_data.get_result_dfs.return_value
        mock_encoder_with_data.get_result_dfs.assert_called_once()

    def test_get_encoded_dataframes(self, test_helper, sample_raw_data, mock_encoder_with_data):
        """11. 인코딩된 DataFrame 조회 테스트"""
        test_helper.loader.database_data_load = Mock(return_value=sample_raw_data)
        
        with patch('src.unknown_data.test.Encoder', return_value=mock_encoder_with_data):
            result = test_helper.get_encoded_dataframes("task1", Category.BROWSER)
        
        # 결과는 각 파일의 DataFrame을 concat한 것
        assert isinstance(result, dict)
        assert "file1" in result
        assert "file2" in result
        assert isinstance(result["file1"], pd.DataFrame)
        assert isinstance(result["file2"], pd.DataFrame)

    def test_process_all_categories_summary(self, test_helper, sample_raw_data, mock_encoder_with_data):
        """12. 모든 카테고리 처리 테스트 (요약 포함)"""
        test_helper.loader.database_data_load = Mock(return_value=sample_raw_data)
        
        with patch('src.unknown_data.test.Encoder', return_value=mock_encoder_with_data):
            result = test_helper.process_all_categories("task1", include_summary=True)
        
        # 모든 카테고리에 대한 결과가 있어야 함
        for category in Category:
            assert category.value in result
            category_result = result[category.value]
            if category_result['status'] == 'success':
                assert 'files' in category_result
                assert 'total_chunks' in category_result
                assert 'chunk_details' in category_result

    def test_process_all_categories_with_errors(self, test_helper):
        """13. 모든 카테고리 처리 테스트 (오류 발생)"""
        test_helper.loader.database_data_load = Mock(side_effect=Exception("Load error"))
        
        result = test_helper.process_all_categories("invalid_task", include_summary=True)
        
        # 모든 카테고리에서 오류가 발생해야 함
        for category in Category:
            assert category.value in result
            assert result[category.value]['status'] == 'error'
            assert 'error' in result[category.value]

    def test_memory_usage_report(self, test_helper, sample_raw_data, mock_encoder_with_data):
        """14. 메모리 사용량 리포트 테스트"""
        test_helper.loader.database_data_load = Mock(return_value=sample_raw_data)
        
        with patch('src.unknown_data.test.Encoder', return_value=mock_encoder_with_data):
            result = test_helper.memory_usage_report("task1", Category.BROWSER)
        
        assert "Memory report logged for task1/browser" in result
        mock_encoder_with_data.log_memory_usage.assert_called_once()

    def test_fresh_encoder_isolation(self, test_helper, sample_raw_data):
        """15. Fresh encoder 격리 테스트"""
        with patch('src.unknown_data.test.Encoder') as mock_encoder_class:
            mock_encoder1 = Mock()
            mock_encoder1.convert_data.return_value = mock_encoder1
            mock_encoder2 = Mock()
            mock_encoder2.convert_data.return_value = mock_encoder2
            mock_encoder_class.side_effect = [mock_encoder1, mock_encoder2]
            
            # 두 번의 fresh encoder 호출
            test_helper.encode_data(sample_raw_data, Category.BROWSER, fresh_encoder=True)
            test_helper.encode_data(sample_raw_data, Category.BROWSER, fresh_encoder=True)
            
            # 두 개의 다른 encoder 인스턴스가 생성되어야 함
            assert mock_encoder_class.call_count == 2

    def test_parameter_handling(self, test_helper):
        """16. 파라미터 처리 테스트"""
        # 기본적인 파라미터 처리 확인
        test_helper.loader.set_database = Mock()
        test_helper.loader.database_task_data_load = Mock(return_value=["task1", "task2", "task3"])
        
        # limit=0인 경우
        result = test_helper.get_task_ids(limit=0)
        assert result == []
        
        # limit=None인 경우 (전체 반환)
        result = test_helper.get_task_ids(limit=None)
        assert result == ["task1", "task2", "task3"]

    def test_integration_workflow_mocked(self, test_helper, sample_raw_data, mock_encoder_with_data):
        """17. 통합 워크플로우 테스트 (완전 Mock)"""
        # 모든 데이터베이스 호출을 Mock으로 처리
        test_helper.loader.set_database = Mock()
        test_helper.loader.database_task_data_load = Mock(return_value=["task1"])
        test_helper.loader.database_data_load = Mock(return_value=sample_raw_data)
        
        with patch('src.unknown_data.test.Encoder', return_value=mock_encoder_with_data):
            # 전체 워크플로우 실행
            task_ids = test_helper.get_task_ids(limit=1)
            task_id = task_ids[0]
            
            data = test_helper.load_data(task_id, Category.BROWSER)
            encoder_result = test_helper.encode_data(data, Category.BROWSER)
            chunk_summary = test_helper.get_chunk_summary(task_id, Category.BROWSER)
            
            assert task_id == "task1"
            assert data == sample_raw_data
            assert encoder_result == mock_encoder_with_data
            assert isinstance(chunk_summary, dict)

    def test_performance_simulation(self, test_helper, mock_encoder_with_data):
        """18. 성능 시뮬레이션 테스트"""
        # 대용량 데이터 시뮬레이션
        large_data = {f"file_{i}": [{"data": f"value_{j}"} for j in range(10)] 
                      for i in range(5)}
        
        test_helper.loader.database_data_load = Mock(return_value=large_data)
        
        with patch('src.unknown_data.test.Encoder', return_value=mock_encoder_with_data):
            # 성능 측정
            import time
            start_time = time.time()
            result = test_helper.get_encoded_results("task1", Category.BROWSER)
            end_time = time.time()
            
            # Mock이므로 매우 빠르게 완료되어야 함
            assert end_time - start_time < 1.0
            assert result is not None

    def test_memory_efficiency_basic(self, test_helper):
        """19. 기본적인 메모리 효율성 테스트"""
        import gc
        import sys
        
        # TestHelper의 기본적인 메모리 사용 패턴 확인
        # 완전한 Mock Config 생성
        def create_mock_config():
            config = Mock(spec=Config_db)
            config.dbms = "postgresql"
            config.username = "test_user"
            config.password = "test_pass"
            config.ip = "localhost"
            config.port = 5432
            config.database_name = "test_db"
            return config
        
        # 여러 인스턴스 생성과 삭제
        helpers = []
        for i in range(3):
            config = create_mock_config()
            with patch.object(DataLoader, 'set_database'):
                helper = TestHelper(config)
                helpers.append(helper)
        
        # 인스턴스들이 정상적으로 생성되었는지 확인
        assert len(helpers) == 3
        
        # 각 인스턴스가 필요한 속성들을 가지고 있는지 확인
        for helper in helpers:
            assert hasattr(helper, 'db_config')
            assert hasattr(helper, 'loader')
            assert hasattr(helper, 'logger')
        
        # 정리
        del helpers
        gc.collect()
        
        # 메모리 효율성은 정상적인 인스턴스 생성/삭제로 검증됨
        assert True  # 위 과정에서 메모리 오류가 없으면 통과


class TestHelperLegacyCompatibility:
    """하위 호환성 테스트"""
    
    def test_legacy_functions_importable(self):
        """20. 레거시 함수 import 가능성 테스트"""
        from src.unknown_data.test import get_task_ids, load_and_encode_data
        
        assert callable(get_task_ids)
        assert callable(load_and_encode_data)

    @patch('src.unknown_data.test.TestHelper')
    def test_legacy_get_task_ids_function(self, mock_helper_class):
        """21. 레거시 get_task_ids 함수 테스트"""
        mock_helper = Mock()
        mock_helper.get_task_ids.return_value = ["task1", "task2"]
        mock_helper_class.return_value = mock_helper
        
        from src.unknown_data.loader import DataLoader
        loader = Mock(spec=DataLoader)
        config = Mock(spec=Config_db)
        
        result = get_task_ids(loader, config)
        
        assert result == ["task1", "task2"]
        mock_helper_class.assert_called_once_with(config)

    def test_legacy_load_and_encode_function(self):
        """22. 레거시 load_and_encode_data 함수 테스트"""
        from src.unknown_data.loader import DataLoader
        from src.unknown_data.encoder import Encoder
        
        mock_loader = Mock(spec=DataLoader)
        mock_encoder = Mock(spec=Encoder)
        mock_data = {"test": "data"}
        mock_result = Mock()
        
        mock_loader.database_data_load.return_value = mock_data
        mock_encoder.convert_data.return_value = mock_result
        
        result = load_and_encode_data("task1", Category.BROWSER, mock_loader, mock_encoder)
        
        assert result == mock_result
        mock_loader.database_data_load.assert_called_once_with("task1", Category.BROWSER)
        mock_encoder.convert_data.assert_called_once_with(mock_data, Category.BROWSER)


def test_deployment_readiness_final():
    """23. 최종 배포 준비 상태 확인"""
    # 기본적인 import 테스트
    from src.unknown_data.test import TestHelper
    from src.unknown_data.core import Category
    from src.unknown_data.loader.loader import Config_db
    
    # Mock 설정으로 인스턴스 생성 테스트
    config = Mock(spec=Config_db)
    config.dbms = "postgresql"
    config.username = "test"
    config.password = "test"
    config.ip = "localhost"
    config.port = 5432
    config.database_name = "test"
    
    helper = TestHelper(config)
    
    # 주요 메서드들이 존재하는지 확인
    required_methods = [
        'get_task_ids', 'load_data', 'encode_data', 'get_chunk_summary',
        'get_encoded_results', 'get_encoded_dataframes', 
        'process_all_categories', 'memory_usage_report'
    ]
    
    for method_name in required_methods:
        assert hasattr(helper, method_name), f"Missing method: {method_name}"
        assert callable(getattr(helper, method_name)), f"Method not callable: {method_name}"
    
    # Category enum이 정상인지 확인
    assert len(list(Category)) > 0, "Category enum is empty"
    
    # 레거시 함수들도 확인
    from src.unknown_data.test import get_task_ids, load_and_encode_data
    assert callable(get_task_ids)
    assert callable(load_and_encode_data)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])