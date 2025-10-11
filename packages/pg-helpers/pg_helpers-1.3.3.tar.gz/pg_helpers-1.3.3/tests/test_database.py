# tests/test_database.py
import unittest
from unittest.mock import patch, MagicMock, mock_open, call
import pandas as pd
import os
import tempfile
import pickle
from sqlalchemy.exc import SQLAlchemyError
import time
import logging

# Import your package modules
from pg_helpers.query_utils import listPrep, queryCleaner
from pg_helpers.config import get_db_config, validate_db_config, get_ssl_params
from pg_helpers.database import (
    createPostgresqlEngine, 
    createPostgresqlEngineWithCustomSSL,
    dataGrabber, 
    recursiveDataGrabber,
    check_ssl_connection,
    diagnose_connection_and_query,
    _execute_with_manual_construction,
    _execute_with_alternative_params
)


class TestQueryUtils(unittest.TestCase):
    """Test query utility functions"""
    
    def test_listPrep_integers(self):
        """Test listPrep with integer list"""
        result = listPrep([1, 2, 3, 4])
        self.assertEqual(result, "1,2,3,4")
    
    def test_listPrep_floats(self):
        """Test listPrep with float list"""
        result = listPrep([1.1, 2.2, 3.3])
        self.assertEqual(result, "1.1,2.2,3.3")
    
    def test_listPrep_strings(self):
        """Test listPrep with string list"""
        result = listPrep(['apple', 'banana', 'cherry'])
        self.assertEqual(result, "'apple','banana','cherry'")
    
    def test_listPrep_single_value(self):
        """Test listPrep with single value"""
        result = listPrep("single_value")
        self.assertEqual(result, "single_value")
    
    def test_listPrep_empty_list(self):
        """Test listPrep with empty list"""
        with self.assertRaises(IndexError):
            listPrep([])
    
    def test_queryCleaner_basic(self):
        """Test basic query cleaning functionality"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.sql') as f:
            f.write("SELECT * FROM table WHERE id IN ($IDS) AND date BETWEEN $START_DATE AND $END_DATE")
            temp_file = f.name
        
        try:
            result = queryCleaner(
                file=temp_file,
                list1=[1, 2, 3],
                varString1='$IDS',
                startDate='2023-01-01',
                endDate='2023-12-31'
            )
            
            expected = "SELECT * FROM table WHERE id IN (1,2,3) AND date BETWEEN '2023-01-01' AND '2023-12-31'"
            self.assertEqual(result, expected)
        
        finally:
            os.unlink(temp_file)
    
    def test_queryCleaner_no_substitutions(self):
        """Test query cleaner with no substitutions"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.sql') as f:
            original_query = "SELECT * FROM table"
            f.write(original_query)
            temp_file = f.name
        
        try:
            result = queryCleaner(file=temp_file)
            self.assertEqual(result, original_query)
        finally:
            os.unlink(temp_file)

    def test_queryCleaner_two_lists(self):
        """Test query cleaner with two lists"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.sql') as f:
            f.write("SELECT * FROM table WHERE id IN ($IDS1) AND category IN ($IDS2)")
            temp_file = f.name
        
        try:
            result = queryCleaner(
                file=temp_file,
                list1=[1, 2, 3],
                varString1='$IDS1',
                list2=['A', 'B', 'C'],
                varString2='$IDS2'
            )
            
            expected = "SELECT * FROM table WHERE id IN (1,2,3) AND category IN ('A','B','C')"
            self.assertEqual(result, expected)
        finally:
            os.unlink(temp_file)


class TestConfig(unittest.TestCase):
    """Test configuration functions"""
    
    @patch.dict(os.environ, {
        'DB_USER': 'testuser',
        'DB_PASSWORD': 'testpass',
        'DB_HOST': 'localhost',
        'DB_PORT': '5432',
        'DB_NAME': 'testdb',
        'DB_SSL_MODE': 'require'
    })
    def test_get_db_config_complete(self):
        """Test getting complete database configuration"""
        config = get_db_config()
        self.assertEqual(config['user'], 'testuser')
        self.assertEqual(config['password'], 'testpass')
        self.assertEqual(config['host'], 'localhost')
        self.assertEqual(config['port'], '5432')
        self.assertEqual(config['database'], 'testdb')
        self.assertEqual(config['ssl_mode'], 'require')
    
    @patch.dict(os.environ, {
        'DB_USER': 'testuser',
        'DB_PASSWORD': 'testpass',
        'DB_HOST': 'localhost',
        'DB_NAME': 'testdb'
    }, clear=True)
    def test_get_db_config_defaults(self):
        """Test default values assignment"""
        config = get_db_config()
        self.assertEqual(config['port'], '5432')
        self.assertEqual(config['ssl_mode'], 'require')
        self.assertIsNone(config['ssl_ca_cert'])
    
    @patch.dict(os.environ, {
        'DB_USER': 'testuser',
        'DB_HOST': 'localhost',
        'DB_NAME': 'testdb'
    }, clear=True)
    def test_validate_db_config_missing_password(self):
        """Test validation with missing required config"""
        with self.assertRaises(ValueError) as context:
            validate_db_config()
        
        self.assertIn("Missing required environment variables", str(context.exception))
        self.assertIn("password", str(context.exception))

    @patch.dict(os.environ, {
        'DB_USER': 'testuser',
        'DB_PASSWORD': 'testpass',
        'DB_HOST': 'localhost',
        'DB_NAME': 'testdb',
        'DB_SSL_CA_CERT': '/nonexistent/path/ca.crt'
    }, clear=True)
    def test_validate_db_config_missing_ssl_file(self):
        """Test validation with missing SSL certificate file"""
        with self.assertRaises(ValueError) as context:
            validate_db_config()
        
        self.assertIn("SSL CA certificate file not found", str(context.exception))

    @patch.dict(os.environ, {
        'DB_USER': 'testuser',
        'DB_PASSWORD': 'testpass',
        'DB_HOST': 'localhost',
        'DB_NAME': 'testdb',
        'DB_SSL_MODE': 'verify-full',
        'DB_SSL_CA_CERT': '/path/to/ca.crt'
    }, clear=True)
    def test_get_ssl_params_with_ca_cert(self):
        """Test SSL parameters with CA certificate"""
        with patch('os.path.exists', return_value=True):
            result = get_ssl_params()
            self.assertIn('sslmode=verify-full', result)
            self.assertIn('sslrootcert=/path/to/ca.crt', result)

    @patch.dict(os.environ, {
        'DB_USER': 'testuser',
        'DB_PASSWORD': 'testpass',
        'DB_HOST': 'localhost',
        'DB_NAME': 'testdb',
        'DB_SSL_MODE': 'require',
        'DB_SSL_CERT': '/path/to/client.crt',
        'DB_SSL_KEY': '/path/to/client.key'
    }, clear=True)
    def test_get_ssl_params_with_client_certs(self):
        """Test SSL parameters with client certificates"""
        with patch('os.path.exists', return_value=True):
            result = get_ssl_params()
            self.assertIn('sslmode=require', result)
            self.assertIn('sslcert=/path/to/client.crt', result)
            self.assertIn('sslkey=/path/to/client.key', result)

    def test_load_env_with_fallback_default(self):
        """Test load_env_with_fallback with default behavior (no env vars set)"""
        # Create a temporary .env file in current directory
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.env', dir='.') as f:
            f.write("DB_USER=default_user\n")
            f.write("DB_PASSWORD=default_pass\n")
            env_file = f.name
        
        try:
            # Rename to .env
            os.rename(env_file, '.env')
            
            # Clear any existing env vars that might interfere
            with patch.dict(os.environ, {}, clear=True):
                # Reload the module to trigger load_env_with_fallback
                import importlib
                import pg_helpers.config
                importlib.reload(pg_helpers.config)
                
                # Check that default .env was loaded
                self.assertEqual(os.getenv('DB_USER'), 'default_user')
                self.assertEqual(os.getenv('DB_PASSWORD'), 'default_pass')
        
        finally:
            if os.path.exists('.env'):
                os.unlink('.env')
    
    def test_load_env_with_fallback_credentials_dir_only(self):
        """Test load_env_with_fallback with only CREDENTIALS_DIR set"""
        # Create temporary credentials directory
        with tempfile.TemporaryDirectory() as tmpdir:
            env_file = os.path.join(tmpdir, '.env')
            with open(env_file, 'w') as f:
                f.write("DB_USER=dir_user\n")
                f.write("DB_PASSWORD=dir_pass\n")
            
            # Set only CREDENTIALS_DIR
            with patch.dict(os.environ, {'CREDENTIALS_DIR': tmpdir}, clear=True):
                import importlib
                import pg_helpers.config
                importlib.reload(pg_helpers.config)
                
                self.assertEqual(os.getenv('DB_USER'), 'dir_user')
                self.assertEqual(os.getenv('DB_PASSWORD'), 'dir_pass')
    
    def test_load_env_with_fallback_credentials_file_only(self):
        """Test load_env_with_fallback with only CREDENTIALS_FILE set"""
        # Create a custom named file in current directory
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.database', dir='.') as f:
            f.write("DB_USER=file_user\n")
            f.write("DB_PASSWORD=file_pass\n")
            custom_filename = os.path.basename(f.name)
        
        try:
            # Set only CREDENTIALS_FILE
            with patch.dict(os.environ, {'CREDENTIALS_FILE': custom_filename}, clear=True):
                import importlib
                import pg_helpers.config
                importlib.reload(pg_helpers.config)
                
                self.assertEqual(os.getenv('DB_USER'), 'file_user')
                self.assertEqual(os.getenv('DB_PASSWORD'), 'file_pass')
        
        finally:
            if os.path.exists(custom_filename):
                os.unlink(custom_filename)
    
    def test_load_env_with_fallback_both_set(self):
        """Test load_env_with_fallback with both CREDENTIALS_DIR and CREDENTIALS_FILE set"""
        # Create temporary credentials directory with custom named file
        with tempfile.TemporaryDirectory() as tmpdir:
            env_file = os.path.join(tmpdir, '.env.custom')
            with open(env_file, 'w') as f:
                f.write("DB_USER=both_user\n")
                f.write("DB_PASSWORD=both_pass\n")
            
            # Set both environment variables
            with patch.dict(os.environ, {
                'CREDENTIALS_DIR': tmpdir,
                'CREDENTIALS_FILE': '.env.custom'
            }, clear=True):
                import importlib
                import pg_helpers.config
                importlib.reload(pg_helpers.config)
                
                self.assertEqual(os.getenv('DB_USER'), 'both_user')
                self.assertEqual(os.getenv('DB_PASSWORD'), 'both_pass')
    
    def test_load_env_with_fallback_nonexistent_file(self):
        """Test load_env_with_fallback with nonexistent file (should not crash)"""
        with patch.dict(os.environ, {
            'CREDENTIALS_DIR': '/nonexistent/path',
            'CREDENTIALS_FILE': '.env.missing'
        }, clear=True):
            # This should not raise an exception, dotenv handles missing files gracefully
            import importlib
            import pg_helpers.config
            importlib.reload(pg_helpers.config)
            
            # No assertion needed, just verify it doesn't crash
    
    def test_load_env_with_fallback_path_construction(self):
        """Test that paths are constructed correctly"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Test with various file names including special cases
            test_cases = [
                '.env.database',
                '.env.production',
                '.env.pink_elephants',
                'credentials.env'
            ]
            
            for filename in test_cases:
                env_file = os.path.join(tmpdir, filename)
                with open(env_file, 'w') as f:
                    f.write(f"TEST_VAR={filename}\n")
                
                with patch.dict(os.environ, {
                    'CREDENTIALS_DIR': tmpdir,
                    'CREDENTIALS_FILE': filename
                }, clear=True):
                    import importlib
                    import pg_helpers.config
                    importlib.reload(pg_helpers.config)
                    
                    self.assertEqual(os.getenv('TEST_VAR'), filename)

class TestDatabase(unittest.TestCase):
    """Test database functions"""
    
    @patch('pg_helpers.database.get_ssl_params')
    @patch('pg_helpers.database.validate_db_config')
    @patch('pg_helpers.database.create_engine')
    def test_createPostgresqlEngine_success(self, mock_create_engine, mock_validate, mock_ssl):
        """Test successful engine creation"""
        mock_validate.return_value = {
            'user': 'testuser',
            'password': 'testpass',
            'host': 'localhost',
            'port': '5432',
            'database': 'testdb'
        }
        mock_ssl.return_value = 'sslmode=require'
        
        mock_engine = MagicMock()
        mock_create_engine.return_value = mock_engine
        
        with patch('builtins.print'):
            result = createPostgresqlEngine()
        
        mock_create_engine.assert_called_once()
        call_args = mock_create_engine.call_args[0][0]
        self.assertIn('postgresql://testuser:testpass@localhost:5432/testdb', call_args)
        self.assertEqual(result, mock_engine)
    
    @patch('pg_helpers.database.validate_db_config')
    def test_createPostgresqlEngine_config_error(self, mock_validate):
        """Test engine creation with config error"""
        mock_validate.side_effect = ValueError("Missing required environment variables: ['password']")
        
        with self.assertRaises(ValueError):
            createPostgresqlEngine()

    @patch('os.path.exists')
    @patch('pg_helpers.database.validate_db_config')
    @patch('pg_helpers.database.create_engine')
    def test_createPostgresqlEngineWithCustomSSL_success(self, mock_create_engine, mock_validate, mock_exists):
        """Test custom SSL engine creation"""
        mock_validate.return_value = {
            'user': 'testuser',
            'password': 'testpass',
            'host': 'localhost',
            'port': '5432',
            'database': 'testdb'
        }
        mock_exists.return_value = True
        mock_engine = MagicMock()
        mock_create_engine.return_value = mock_engine
        
        with patch('builtins.print'):
            result = createPostgresqlEngineWithCustomSSL(
                ssl_ca_cert='/path/to/ca.crt',
                ssl_mode='verify-full'
            )
        
        mock_create_engine.assert_called_once()
        call_args = mock_create_engine.call_args[0][0]
        self.assertIn('sslmode=verify-full', call_args)
        self.assertIn('sslrootcert=/path/to/ca.crt', call_args)
        self.assertEqual(result, mock_engine)

    @patch('os.path.exists')
    @patch('pg_helpers.database.validate_db_config')
    def test_createPostgresqlEngineWithCustomSSL_missing_cert(self, mock_validate, mock_exists):
        """Test custom SSL with missing certificate file"""
        mock_validate.return_value = {
            'user': 'testuser',
            'password': 'testpass',
            'host': 'localhost',
            'port': '5432',
            'database': 'testdb'
        }
        mock_exists.return_value = False
        
        with self.assertRaises(ValueError) as context:
            createPostgresqlEngineWithCustomSSL(ssl_ca_cert='/nonexistent/ca.crt')
        
        self.assertIn("SSL CA certificate file not found", str(context.exception))
    
    @patch('pg_helpers.database.play_notification_sound')
    @patch('pandas.read_sql')
    @patch('time.time')
    def test_dataGrabber_success(self, mock_time, mock_read_sql, mock_sound):
        """Test successful data grabbing"""
        mock_time.side_effect = [0, 5]
        mock_df = pd.DataFrame({'col1': [1, 2, 3], 'col2': ['a', 'b', 'c']})
        mock_read_sql.return_value = mock_df
        mock_engine = MagicMock()
        
        with patch('builtins.print') as mock_print:
            result = dataGrabber("SELECT * FROM test", mock_engine)
        
        pd.testing.assert_frame_equal(result, mock_df)
        mock_read_sql.assert_called_once_with("SELECT * FROM test", mock_engine)
        mock_sound.assert_called_once()
        mock_print.assert_called_with('Elapsed Time: 0:00:05')

    @patch('pg_helpers.database.play_notification_sound')
    @patch('pg_helpers.database._execute_with_manual_construction')
    @patch('pandas.read_sql')
    @patch('logging.getLogger')
    def test_dataGrabber_metadata_error_fallback(self, mock_logger, mock_read_sql, mock_manual, mock_sound):
        """Test data grabber with metadata error triggering fallback"""
        # Mock logger to avoid time.time() calls in logging
        mock_logger_instance = MagicMock()
        mock_logger.return_value = mock_logger_instance
        
        # First attempt fails with metadata error, second also fails
        mock_read_sql.side_effect = [
            Exception("immutabledict not a sequence"),
            Exception("connection error")
        ]
        
        # Manual construction succeeds
        mock_df = pd.DataFrame({'col1': [1, 2]})
        mock_manual.return_value = mock_df
        mock_engine = MagicMock()
        
        with patch('builtins.print'), \
             patch('time.time', side_effect=[0, 3]):
            result = dataGrabber("SELECT * FROM test", mock_engine, debug=True)
        
        pd.testing.assert_frame_equal(result, mock_df)
        mock_manual.assert_called_once()
        mock_sound.assert_called_once()

    @patch('pandas.read_sql')
    def test_dataGrabber_non_metadata_error(self, mock_read_sql):
        """Test data grabber with non-metadata error"""
        mock_read_sql.side_effect = Exception("syntax error at line 1")
        mock_engine = MagicMock()
        
        with self.assertRaises(Exception) as context:
            dataGrabber("INVALID SQL", mock_engine)
        
        self.assertIn("syntax error", str(context.exception))

    def test_dataGrabber_with_limit(self):
        """Test data grabber with limit parameter"""
        with patch('pandas.read_sql') as mock_read_sql, \
             patch('pg_helpers.database.play_notification_sound'), \
             patch('time.time', side_effect=[0, 1]):
            
            mock_df = pd.DataFrame({'col1': [1]})
            mock_read_sql.return_value = mock_df
            mock_engine = MagicMock()
            
            query = "SELECT * FROM test FOR READ ONLY"
            result = dataGrabber(query, mock_engine, limit='10')
            
            expected_query = "SELECT * FROM test LIMIT 10 FOR READ ONLY"
            mock_read_sql.assert_called_once_with(expected_query, mock_engine)

    def test_execute_with_manual_construction(self):
        """Test manual DataFrame construction fallback method"""
        mock_engine = MagicMock()
        mock_connection = MagicMock()
        mock_result = MagicMock()
        
        # Mock the connection and result
        mock_engine.connect.return_value.__enter__.return_value = mock_connection
        mock_connection.execute.return_value = mock_result
        
        # Mock result data
        mock_result.keys.return_value = ['id', 'name']
        mock_result.fetchall.return_value = [
            (1, 'Alice'),
            (2, 'Bob')
        ]
        
        logger = MagicMock()
        result = _execute_with_manual_construction("SELECT * FROM users", mock_engine, logger)
        
        expected_df = pd.DataFrame([
            {'id': 1, 'name': 'Alice'},
            {'id': 2, 'name': 'Bob'}
        ])
        pd.testing.assert_frame_equal(result, expected_df)

    @patch('pandas.read_sql')
    def test_execute_with_alternative_params(self, mock_read_sql):
        """Test alternative parameters fallback method"""
        mock_engine = MagicMock()
        mock_connection = MagicMock()
        mock_engine.connect.return_value.__enter__.return_value = mock_connection
        
        # First parameter set succeeds
        mock_df = pd.DataFrame({'col1': [1, 2]})
        mock_read_sql.return_value = mock_df
        
        logger = MagicMock()
        result = _execute_with_alternative_params("SELECT * FROM test", mock_engine, logger)
        
        pd.testing.assert_frame_equal(result, mock_df)
        mock_read_sql.assert_called_once()

    @patch('pg_helpers.database.createPostgresqlEngine')
    @patch('pg_helpers.database.dataGrabber')
    @patch('pickle.dump')
    @patch('os.makedirs')
    def test_recursiveDataGrabber_success_first_attempt(self, mock_makedirs, mock_pickle, mock_datagrabber, mock_engine):
        """Test recursive data grabber succeeding on first attempt"""
        # Setup mocks
        mock_engine_instance = MagicMock()
        mock_engine.return_value = mock_engine_instance
        
        # Mock successful connection test
        mock_connection = MagicMock()
        mock_engine_instance.connect.return_value.__enter__.return_value = mock_connection
        
        # Mock successful query execution
        mock_df = pd.DataFrame({'col1': [1, 2, 3]})
        mock_datagrabber.return_value = mock_df
        
        query_dict = {'test_query': 'SELECT * FROM test_table'}
        results_dict = {}
        
        with patch('builtins.print'):
            result = recursiveDataGrabber(query_dict, results_dict)
        
        # Verify results
        self.assertIn('test_query', result)
        pd.testing.assert_frame_equal(result['test_query'], mock_df)
        mock_datagrabber.assert_called_once()

    @patch('pg_helpers.database.createPostgresqlEngine')
    @patch('pg_helpers.database.dataGrabber')
    @patch('time.sleep')
    def test_recursiveDataGrabber_retry_logic(self, mock_sleep, mock_datagrabber, mock_engine):
        """Test recursive data grabber retry logic"""
        # Setup mocks
        mock_engine_instance = MagicMock()
        mock_engine.return_value = mock_engine_instance
        
        # Mock connection test
        mock_connection = MagicMock()
        mock_engine_instance.connect.return_value.__enter__.return_value = mock_connection
        
        # First attempt fails, second succeeds
        mock_datagrabber.side_effect = [
            Exception("Connection error"),
            pd.DataFrame({'col1': [1, 2, 3]})
        ]
        
        query_dict = {'test_query': 'SELECT * FROM test_table'}
        results_dict = {}
        
        with patch('builtins.print'), \
             patch('pickle.dump'), \
             patch('os.makedirs'):
            result = recursiveDataGrabber(query_dict, results_dict, max_attempts=3)
        
        # Verify retry happened
        self.assertEqual(mock_datagrabber.call_count, 2)
        mock_sleep.assert_called_once()

    @patch('pg_helpers.database.createPostgresqlEngine')
    def test_check_ssl_connection_no_engine(self, mock_create_engine):
        """Test SSL connection testing function without provided engine"""
        mock_engine = MagicMock()
        mock_connection = MagicMock()
        mock_result = MagicMock()
        
        mock_create_engine.return_value = mock_engine
        mock_engine.connect.return_value.__enter__.return_value = mock_connection
        mock_connection.execute.return_value = mock_result
        
        # Mock SSL query results
        mock_row = MagicMock()
        mock_row._asdict.return_value = {
            'ssl_active': True,
            'pg_version': 'PostgreSQL 13.0',
            'ssl_enabled_on_server': 'on'
        }
        mock_result.fetchone.return_value = mock_row
        
        with patch('builtins.print'):
            result = check_ssl_connection()
        
        self.assertIsInstance(result, dict)
        self.assertTrue(result.get('ssl_active'))
        mock_create_engine.assert_called_once()

    def test_check_ssl_connection_with_engine(self):
        """Test SSL connection testing function with provided engine"""
        mock_engine = MagicMock()
        mock_connection = MagicMock()
        mock_result = MagicMock()
        
        # Set up engine mocking
        mock_engine.connect.return_value.__enter__.return_value = mock_connection
        
        # Mock multiple execute calls for different SSL functions
        mock_result_1 = MagicMock()
        mock_result_2 = MagicMock()
        
        # First call: basic SSL info query
        mock_row_1 = MagicMock()
        mock_row_1._asdict.return_value = {
            'ssl_active': False,
            'pg_version': 'PostgreSQL 12.0',
            'ssl_enabled_on_server': 'off',
            'client_address': '127.0.0.1',
            'server_address': '127.0.0.1'
        }
        mock_result_1.fetchone.return_value = mock_row_1
        
        # Second call: ssl_cipher() call which should return None for no SSL
        mock_result_2.fetchone.return_value = [None]
        
        # Configure the connection.execute to return different results
        mock_connection.execute.side_effect = [mock_result_1, mock_result_2, mock_result_2, mock_result_2, mock_result_2, mock_result_2, mock_result_2]
        
        with patch('builtins.print'):
            result = check_ssl_connection(mock_engine)
        
        self.assertIsInstance(result, dict)
        # The function should detect ssl_active as False since ssl_cipher is None
        self.assertFalse(result.get('ssl_active'))

    @patch('pg_helpers.database.dataGrabber')
    def test_diagnose_connection_and_query(self, mock_datagrabber):
        """Test connection and query diagnostic function"""
        mock_engine = MagicMock()
        mock_engine.url.drivername = 'postgresql'
        mock_engine.url.database = 'testdb'
        
        mock_df = pd.DataFrame({'col1': [1, 2], 'col2': ['a', 'b']})
        mock_datagrabber.return_value = mock_df
        
        result = diagnose_connection_and_query(mock_engine, "SELECT * FROM test")
        
        self.assertIn('engine_info', result)
        self.assertIn('query_info', result)
        self.assertIn('test_results', result)
        self.assertTrue(result['test_results']['success'])


class TestIntegration(unittest.TestCase):
    """Integration tests that test multiple components together"""
    
    def test_query_workflow(self):
        """Test a typical query workflow"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.sql') as f:
            f.write("SELECT * FROM users WHERE id IN ($USER_IDS) AND created_date >= $START_DATE")
            temp_file = f.name
        
        try:
            user_ids = [100, 200, 300]
            cleaned_query = queryCleaner(
                file=temp_file,
                list1=user_ids,
                varString1='$USER_IDS',
                startDate='2023-01-01',
                endDate='2023-12-31'
            )
            
            expected = "SELECT * FROM users WHERE id IN (100,200,300) AND created_date >= '2023-01-01'"
            self.assertEqual(cleaned_query, expected)
            
        finally:
            os.unlink(temp_file)

    @patch.dict(os.environ, {
        'DB_USER': 'testuser',
        'DB_PASSWORD': 'testpass',
        'DB_HOST': 'localhost',
        'DB_NAME': 'testdb',
        'DB_SSL_MODE': 'require'
    }, clear=True)
    def test_config_to_engine_workflow(self):
        """Test workflow from config validation to engine creation"""
        with patch('pg_helpers.database.create_engine') as mock_create_engine:
            mock_engine = MagicMock()
            mock_create_engine.return_value = mock_engine
            
            with patch('builtins.print'):
                # Test that config flows through to engine creation
                config = validate_db_config()
                self.assertEqual(config['user'], 'testuser')
                
                engine = createPostgresqlEngine()
                self.assertEqual(engine, mock_engine)
                
                # Verify connection string was built correctly
                call_args = mock_create_engine.call_args[0][0]
                self.assertIn('postgresql://testuser:testpass@localhost', call_args)
                self.assertIn('sslmode=require', call_args)


class TestNotifications(unittest.TestCase):
    """Test notification functions"""
    
    @patch('sys.platform', 'darwin')
    @patch('os.system')
    def test_play_notification_sound_macos(self, mock_system):
        """Test notification sound on macOS"""
        from pg_helpers.notifications import play_notification_sound
        
        play_notification_sound()
        mock_system.assert_called_once_with('afplay /System/Library/Sounds/Sosumi.aiff')

    @patch('sys.platform', 'win32')
    @patch('os.system')
    def test_play_notification_sound_windows(self, mock_system):
        """Test notification sound on Windows"""
        from pg_helpers.notifications import play_notification_sound
        
        with patch('builtins.__import__') as mock_import:
            # Mock winsound module
            mock_winsound = MagicMock()
            mock_import.return_value = mock_winsound
            
            play_notification_sound()
            # Should attempt to import and use winsound

    @patch('sys.platform', 'linux')
    @patch('os.system')
    def test_play_notification_sound_linux(self, mock_system):
        """Test notification sound on Linux (should not call system)"""
        from pg_helpers.notifications import play_notification_sound
        
        play_notification_sound()
        mock_system.assert_not_called()


if __name__ == '__main__':
    # Configure test runner
    unittest.main(
        verbosity=2,
        buffer=True,  # Capture stdout/stderr during tests
        failfast=False,  # Continue running tests even if one fails
        warnings='ignore'  # Suppress warnings during tests
    )