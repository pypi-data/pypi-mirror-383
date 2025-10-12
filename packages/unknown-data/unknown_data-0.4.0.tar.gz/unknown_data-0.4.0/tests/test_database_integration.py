"""
데이터베이스 데이터 로더 테스트
"""
import pytest
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock

from src.unknown_data.loader.loader import DataLoader
from src.unknown_data.loader.base import Config_db
from src.unknown_data.loader.data import Artifact
from src.unknown_data.core import Category


class TestDatabaseDataLoader:
    """데이터베이스 데이터 로더 테스트 클래스"""
    
    def setup_method(self):
        """각 테스트 전에 실행되는 설정"""
        self.loader = DataLoader()
        self.mock_config = Config_db(
            dbms="postgresql",
            username="test_user",
            password="test_pass",
            ip="localhost",
            port=5432,
            database_name="test_db"
        )
        self.sample_json_data = {
            "browser_data": [
                {"url": "https://example.com", "visit_count": 10},
                {"url": "https://google.com", "visit_count": 5}
            ]
        }
    
    @patch('src.unknown_data.loader.loader.get_db')
    def test_set_database_success(self, mock_get_db):
        """데이터베이스 설정 성공 테스트"""
        # Mock 세션 설정
        mock_session = Mock()
        mock_get_db.return_value = mock_session
        
        # 테스트 실행
        self.loader.set_database(self.mock_config)
        
        # 검증
        assert self.loader.config == self.mock_config
        assert self.loader.db == mock_session
        mock_get_db.assert_called_once_with(self.mock_config)
    
    @patch('src.unknown_data.loader.loader.get_db')
    def test_set_database_with_existing_session(self, mock_get_db):
        """기존 세션이 있을 때 데이터베이스 설정 테스트"""
        # 기존 세션 Mock
        mock_old_session = Mock()
        mock_new_session = Mock()
        mock_get_db.return_value = mock_new_session
        
        # 기존 세션 설정
        self.loader.db = mock_old_session
        
        # 테스트 실행
        self.loader.set_database(self.mock_config)
        
        # 검증
        mock_old_session.close.assert_called_once()  # 기존 세션이 닫혔는지 확인
        assert self.loader.db == mock_new_session
    
    @patch('src.unknown_data.loader.loader.get_db')
    def test_set_database_failure(self, mock_get_db):
        """데이터베이스 설정 실패 테스트"""
        # Mock에서 예외 발생
        mock_get_db.side_effect = Exception("Connection failed")
        
        # 테스트 실행 및 검증
        with pytest.raises(ConnectionRefusedError) as exc_info:
            self.loader.set_database(self.mock_config)
        
        assert "데이터베이스 연결 실패" in str(exc_info.value)
    
    def test_ensure_db_connection_no_config(self):
        """설정이 없을 때 연결 확인 테스트"""
        # config가 None인 상태
        self.loader.config = None
        
        # 테스트 실행 및 검증
        with pytest.raises(ValueError) as exc_info:
            self.loader._ensure_db_connection()
        
        assert "데이터베이스 설정이 필요합니다" in str(exc_info.value)
    
    @patch('src.unknown_data.loader.loader.get_db')
    def test_ensure_db_connection_no_session(self, mock_get_db):
        """세션이 없을 때 연결 확인 테스트"""
        # Mock 설정
        mock_session = Mock()
        mock_session.is_active = True
        mock_get_db.return_value = mock_session
        
        self.loader.config = self.mock_config
        self.loader.db = None  # 세션 없음
        
        # 테스트 실행
        self.loader._ensure_db_connection()
        
        # 검증
        assert self.loader.db == mock_session
        mock_get_db.assert_called_once_with(self.mock_config)
    
    @patch('src.unknown_data.loader.loader.get_db')
    def test_ensure_db_connection_inactive_session(self, mock_get_db):
        """비활성 세션일 때 재연결 테스트"""
        # Mock 설정
        mock_old_session = Mock()
        mock_old_session.is_active = False
        mock_new_session = Mock()
        mock_new_session.is_active = True
        
        mock_get_db.return_value = mock_new_session
        
        self.loader.config = self.mock_config
        self.loader.db = mock_old_session
        
        # 테스트 실행
        self.loader._ensure_db_connection()
        
        # 검증
        mock_old_session.close.assert_called_once()
        assert self.loader.db == mock_new_session
    
    @patch('src.unknown_data.loader.loader.get_db')
    def test_ensure_db_connection_reconnection_failure(self, mock_get_db):
        """재연결 실패 테스트"""
        # Mock에서 재연결 시 예외 발생
        mock_get_db.side_effect = Exception("Reconnection failed")
        
        self.loader.config = self.mock_config
        self.loader.db = None
        
        # 테스트 실행 및 검증
        with pytest.raises(ConnectionError) as exc_info:
            self.loader._ensure_db_connection()
        
        assert "데이터베이스 재연결 실패" in str(exc_info.value)
    
    def test_close_db_session_success(self):
        """세션 닫기 성공 테스트"""
        # Mock 세션 설정
        mock_session = Mock()
        self.loader.db = mock_session
        
        # 테스트 실행
        self.loader._close_db_session()
        
        # 검증
        mock_session.close.assert_called_once()
        assert self.loader.db is None
    
    def test_close_db_session_no_session(self):
        """세션이 없을 때 닫기 테스트"""
        # 세션이 None인 상태
        self.loader.db = None
        
        # 테스트 실행 (예외 없이 실행되어야 함)
        self.loader._close_db_session()
        
        # 검증
        assert self.loader.db is None
    
    def test_close_db_session_with_exception(self):
        """세션 닫기 시 예외 발생 테스트"""
        # Mock 세션에서 예외 발생하도록 설정
        mock_session = Mock()
        mock_session.close.side_effect = Exception("Close failed")
        self.loader.db = mock_session
        
        # 테스트 실행 (예외가 발생해도 안전하게 처리되어야 함)
        self.loader._close_db_session()
        
        # 검증
        assert self.loader.db is None
    
    @patch('src.unknown_data.loader.loader.get_db')
    def test_database_data_load_success(self, mock_get_db):
        """데이터베이스에서 데이터 로드 성공 테스트"""
        # Mock 설정
        mock_session = Mock()
        mock_session.is_active = True
        mock_get_db.return_value = mock_session
        
        # Mock Artifact 객체
        mock_artifact = Mock()
        mock_artifact.json_data = self.sample_json_data
        
        # Mock 쿼리 체인
        mock_query = Mock()
        mock_filter = Mock()
        mock_filter.first.return_value = mock_artifact
        mock_query.filter.return_value = mock_filter
        mock_session.query.return_value = mock_query
        
        # 테스트 준비
        self.loader.config = self.mock_config
        self.loader.db = mock_session
        
        # 테스트 실행
        result = self.loader.database_data_load("test-task-123", Category.BROWSER)
        
        # 검증
        assert result == self.sample_json_data
        mock_session.query.assert_called_once_with(Artifact)
        mock_query.filter.assert_called_once()
        mock_filter.first.assert_called_once()
    
    @patch('src.unknown_data.loader.loader.get_db')
    def test_database_data_load_no_data_found(self, mock_get_db):
        """데이터베이스에서 데이터를 찾을 수 없는 경우 테스트"""
        # Mock 설정
        mock_session = Mock()
        mock_session.is_active = True
        mock_get_db.return_value = mock_session
        
        # Mock 쿼리 체인 - 데이터 없음
        mock_query = Mock()
        mock_filter = Mock()
        mock_filter.first.return_value = None  # 데이터 없음
        mock_query.filter.return_value = mock_filter
        mock_session.query.return_value = mock_query
        
        # 테스트 준비
        self.loader.config = self.mock_config
        self.loader.db = mock_session
        
        # 테스트 실행 및 검증
        with pytest.raises(ValueError) as exc_info:
            self.loader.database_data_load("test-task-123", Category.BROWSER)
        
        assert "해당하는 데이터를 찾을 수 없습니다" in str(exc_info.value)
        assert "test-task-123" in str(exc_info.value)
        assert "BROWSER_DATA" in str(exc_info.value)
    
    @patch('src.unknown_data.loader.loader.get_db')
    def test_database_data_load_no_json_data(self, mock_get_db):
        """데이터베이스에서 json_data가 없는 경우 테스트"""
        # Mock 설정
        mock_session = Mock()
        mock_session.is_active = True
        mock_get_db.return_value = mock_session
        
        # Mock Artifact 객체 - json_data가 None
        mock_artifact = Mock()
        mock_artifact.json_data = None
        
        # Mock 쿼리 체인
        mock_query = Mock()
        mock_filter = Mock()
        mock_filter.first.return_value = mock_artifact
        mock_query.filter.return_value = mock_filter
        mock_session.query.return_value = mock_query
        
        # 테스트 준비
        self.loader.config = self.mock_config
        self.loader.db = mock_session
        
        # 테스트 실행 및 검증
        with pytest.raises(ValueError) as exc_info:
            self.loader.database_data_load("test-task-123", Category.BROWSER)
        
        assert "json_data가 없습니다" in str(exc_info.value)
    
    def test_database_data_load_no_config(self):
        """설정 없이 데이터베이스 로드 시도 테스트"""
        # config가 None인 상태
        self.loader.config = None
        
        # 테스트 실행 및 검증
        with pytest.raises(ValueError) as exc_info:
            self.loader.database_data_load("test-task-123", Category.BROWSER)
        
        assert "데이터베이스 설정이 필요합니다" in str(exc_info.value)
    
    @patch('src.unknown_data.loader.loader.get_db')
    def test_database_data_load_no_session_after_ensure(self, mock_get_db):
        """연결 확인 후에도 세션이 없는 경우 테스트"""
        # Mock 설정 - ensure_db_connection은 성공하지만 세션이 여전히 None
        mock_get_db.return_value = Mock()
        
        self.loader.config = self.mock_config
        
        # _ensure_db_connection을 Mock으로 덮어써서 세션을 None으로 유지
        with patch.object(self.loader, '_ensure_db_connection'):
            self.loader.db = None  # 강제로 None 설정
            
            # 테스트 실행 및 검증
            with pytest.raises(ConnectionError) as exc_info:
                self.loader.database_data_load("test-task-123", Category.BROWSER)
            
            assert "데이터베이스 세션이 초기화되지 않았습니다" in str(exc_info.value)
    
    @patch('src.unknown_data.loader.loader.get_db')
    def test_database_data_load_connection_error_during_query(self, mock_get_db):
        """쿼리 실행 중 연결 오류 발생 테스트"""
        # Mock 설정
        mock_session = Mock()
        mock_session.is_active = True
        mock_session.query.side_effect = Exception("Database connection lost")
        
        mock_get_db.return_value = mock_session
        
        # 테스트 준비
        self.loader.config = self.mock_config
        self.loader.db = mock_session
        
        # Mock _close_db_session to verify it's called
        with patch.object(self.loader, '_close_db_session') as mock_close:
            # 테스트 실행 및 검증
            with pytest.raises(Exception) as exc_info:
                self.loader.database_data_load("test-task-123", Category.BROWSER)
            
            # 데이터베이스 관련 오류이므로 세션이 닫혀야 함
            mock_close.assert_called_once()
    
    @patch('src.unknown_data.loader.loader.get_db')
    def test_database_integration_with_all_categories(self, mock_get_db):
        """모든 카테고리로 데이터베이스 통합 테스트"""
        # Mock 설정
        mock_session = Mock()
        mock_session.is_active = True
        mock_get_db.return_value = mock_session
        
        self.loader.config = self.mock_config
        self.loader.db = mock_session
        
        # 각 카테고리별 테스트
        test_cases = [
            (Category.BROWSER, "BROWSER_DATA", {"browser_history": ["url1", "url2"]}),
            (Category.DELETED, "DELETED_DATA", {"deleted_files": ["file1.txt", "file2.doc"]}),
            (Category.USB, "USB_DATA", {"usb_devices": ["device1", "device2"]}),
            (Category.LNK, "LNK_DATA", {"lnk_files": ["shortcut1.lnk", "shortcut2.lnk"]}),
            (Category.MESSENGER, "MESSENGER_DATA", {"messages": ["msg1", "msg2"]}),
            (Category.PREFETCH, "PREFETCH_DATA", {"prefetch_files": ["app1.pf", "app2.pf"]})
        ]
        
        for category, expected_module_type, expected_data in test_cases:
            # Mock Artifact 객체
            mock_artifact = Mock()
            mock_artifact.json_data = expected_data
            
            # Mock 쿼리 체인
            mock_query = Mock()
            mock_filter = Mock()
            mock_filter.first.return_value = mock_artifact
            mock_query.filter.return_value = mock_filter
            mock_session.query.return_value = mock_query
            
            # 테스트 실행
            result = self.loader.database_data_load("test-task", category)
            
            # 검증
            assert result == expected_data
            mock_session.query.assert_called_with(Artifact)
    
    def test_config_db_dataclass(self):
        """Config_db 데이터클래스 테스트"""
        config = Config_db(
            dbms="postgresql",
            username="test_user", 
            password="test_pass",
            ip="127.0.0.1",
            port=5432,
            database_name="forensic_db"
        )
        
        assert config.dbms == "postgresql"
        assert config.username == "test_user"
        assert config.password == "test_pass"
        assert config.ip == "127.0.0.1"
        assert config.port == 5432
        assert config.database_name == "forensic_db"
    
    @patch('src.unknown_data.loader.loader.get_db')
    def test_database_data_load_different_task_ids(self, mock_get_db):
        """다른 task_id로 데이터 로드 테스트"""
        # Mock 설정
        mock_session = Mock()
        mock_session.is_active = True
        mock_get_db.return_value = mock_session
        
        self.loader.config = self.mock_config
        self.loader.db = mock_session
        
        # 다양한 task_id 테스트
        task_ids = [
            "550e8400-e29b-41d4-a716-446655440000",  # UUID 형태
            "task-2024-001",  # 사용자 정의 형태
            "12345"  # 숫자 형태
        ]
        
        for task_id in task_ids:
            # Mock Artifact 객체
            mock_artifact = Mock()
            mock_artifact.json_data = {"task_id": task_id, "data": "test"}
            
            # Mock 쿼리 체인
            mock_query = Mock()
            mock_filter = Mock()
            mock_filter.first.return_value = mock_artifact
            mock_query.filter.return_value = mock_filter
            mock_session.query.return_value = mock_query
            
            # 테스트 실행
            result = self.loader.database_data_load(task_id, Category.BROWSER)
            
            # 검증
            assert result["task_id"] == task_id
            assert result["data"] == "test"


class TestDatabaseLoaderEdgeCases:
    """데이터베이스 로더 엣지 케이스 테스트"""
    
    def setup_method(self):
        """각 테스트 전에 실행되는 설정"""
        self.loader = DataLoader()
    
    def test_multiple_set_database_calls(self):
        """여러 번 set_database 호출 테스트"""
        config1 = Config_db("postgresql", "user1", "pass1", "host1", 5432, "db1")
        config2 = Config_db("postgresql", "user2", "pass2", "host2", 5433, "db2")
        
        with patch('src.unknown_data.loader.loader.get_db') as mock_get_db:
            mock_session1 = Mock()
            mock_session2 = Mock()
            
            # 첫 번째 호출에서는 session1, 두 번째 호출에서는 session2 반환
            mock_get_db.side_effect = [mock_session1, mock_session2]
            
            # 첫 번째 설정
            self.loader.set_database(config1)
            assert self.loader.config == config1
            assert self.loader.db == mock_session1
            
            # 두 번째 설정 - 기존 세션이 닫히고 새 세션이 생성되어야 함
            self.loader.set_database(config2)
            assert self.loader.config == config2
            assert self.loader.db == mock_session2
            mock_session1.close.assert_called_once()
    
    @patch('src.unknown_data.loader.loader.get_db')
    def test_session_state_persistence(self, mock_get_db):
        """세션 상태 지속성 테스트"""
        mock_session = Mock()
        mock_session.is_active = True
        mock_get_db.return_value = mock_session
        
        config = Config_db("postgresql", "user", "pass", "host", 5432, "db")
        
        # 데이터베이스 설정
        self.loader.set_database(config)
        original_session = self.loader.db
        
        # 여러 번 연결 확인 호출
        self.loader._ensure_db_connection()
        self.loader._ensure_db_connection()
        self.loader._ensure_db_connection()
        
        # 같은 세션이 유지되어야 함
        assert self.loader.db is original_session
        # get_db는 초기 설정 시 한 번만 호출되어야 함
        mock_get_db.assert_called_once()
    
    def test_loader_initialization_state(self):
        """DataLoader 초기화 상태 테스트"""
        loader = DataLoader()
        
        # 초기 상태 검증
        assert loader.data_dir == "./data/agent_result"
        assert loader.file_path == ""
        assert loader.config is None
        assert loader.db is None
        assert loader._s3_client is None


class TestArtifactModel:
    """Artifact 모델 관련 테스트"""
    
    def test_artifact_model_exists(self):
        """Artifact 모델이 존재하는지 테스트"""
        # Artifact 클래스가 import 가능한지 확인
        assert Artifact is not None
        assert hasattr(Artifact, '__tablename__')
        assert Artifact.__tablename__ == "forensic_data_files"
    
    def test_artifact_model_fields(self):
        """Artifact 모델 필드 테스트"""
        # 필요한 필드들이 있는지 확인
        expected_fields = [
            'id', 'pc_id', 'task', 'module_type', 'collection_time',
            'file_size', 'checksum', 'json_data', 'created_at', 'update_at',
            'processed', 'error_message', 'extracted_info'
        ]
        
        for field in expected_fields:
            assert hasattr(Artifact, field), f"Artifact model should have {field} field"
