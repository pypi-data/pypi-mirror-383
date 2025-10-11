### pg_helpers/database.py
"""Database connection and query execution utilities"""
import logging
import math
import os
import pandas as pd
import pickle
import time
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
import warnings

from .config import validate_db_config, get_ssl_params
from .notifications import play_notification_sound

def createPostgresqlEngine():
    """
    Create SQLAlchemy engine for PostgreSQL connection with SSL support
    
    Returns:
        sqlalchemy.Engine: Database engine
        
    Raises:
        ValueError: If required environment variables are missing
        Exception: If engine creation fails
    """
    try:
        config = validate_db_config()
        ssl_params = get_ssl_params()
        
        # Build connection string with SSL parameters
        connection_string = (
            f"postgresql://{config['user']}:{config['password']}@"
            f"{config['host']}:{config['port']}/{config['database']}?{ssl_params}"
        )
        
        # Optional: Log connection details (without password)
        safe_connection_string = connection_string.replace(config['password'], '****')
        print(f"Connecting to PostgreSQL with SSL: {safe_connection_string}")
        
        engine = create_engine(connection_string)
        return engine
        
    except Exception as e:
        print(f"Error creating PostgreSQL engine: {e}")
        raise

def createPostgresqlEngineWithCustomSSL(ssl_ca_cert=None, ssl_mode='require', ssl_cert=None, ssl_key=None):
    """
    Create SQLAlchemy engine with custom SSL configuration (programmatic override)
    
    Args:
        ssl_ca_cert (str, optional): Path to CA certificate file
        ssl_mode (str): SSL mode (disable, allow, prefer, require, verify-ca, verify-full)
        ssl_cert (str, optional): Path to client certificate file
        ssl_key (str, optional): Path to client key file
    
    Returns:
        sqlalchemy.Engine: Database engine
    """
    try:
        config = validate_db_config()
        ssl_params = [f"sslmode={ssl_mode}"]
        
        if ssl_ca_cert:
            if not os.path.exists(ssl_ca_cert):
                raise ValueError(f"SSL CA certificate file not found: {ssl_ca_cert}")
            ssl_params.append(f"sslrootcert={ssl_ca_cert}")
        
        if ssl_cert:
            if not os.path.exists(ssl_cert):
                raise ValueError(f"SSL client certificate file not found: {ssl_cert}")
            ssl_params.append(f"sslcert={ssl_cert}")
        
        if ssl_key:
            if not os.path.exists(ssl_key):
                raise ValueError(f"SSL client key file not found: {ssl_key}")
            ssl_params.append(f"sslkey={ssl_key}")
        
        ssl_param_string = '&'.join(ssl_params)
        
        connection_string = (
            f"postgresql://{config['user']}:{config['password']}@"
            f"{config['host']}:{config['port']}/{config['database']}?{ssl_param_string}"
        )
        
        # Log connection details (without password)
        safe_connection_string = connection_string.replace(config['password'], '****')
        print(f"Connecting to PostgreSQL with custom SSL: {safe_connection_string}")
        
        engine = create_engine(connection_string)
        return engine
        
    except Exception as e:
        print(f"Error creating PostgreSQL engine with custom SSL: {e}")
        raise

def check_ssl_connection(engine=None):
    """
    Verify SSL connection and display SSL information
    
    Args:
        engine: SQLAlchemy engine (optional, will create one if not provided)
    
    Returns:
        dict: SSL connection information
    """
    if engine is None:
        engine = createPostgresqlEngine()
    
    try:
        with engine.connect() as conn:
            # Query PostgreSQL for SSL information
            ssl_info = {}
            
            # Basic connection information
            try:
                basic_info_query = """
                SELECT
                    coalesce(s.ssl, false) AS ssl_active,
                    version() AS pg_version,
                    (SELECT setting FROM pg_settings WHERE name = 'ssl') AS ssl_enabled_on_server,
                    inet_client_addr() as client_address,
                    inet_server_addr() AS server_address
                FROM
                    pg_stat_ssl s
                JOIN
                    pg_stat_activity a ON s.pid = a.pid
                WHERE
                    a.pid = pg_backend_pid();
                """
                result = conn.execute(text(basic_info_query))
                row = result.fetchone()
                
                # Handle different SQLAlchemy result formats
                if hasattr(row, '_asdict'):
                    # Named tuple style
                    ssl_info.update(row._asdict())
                elif hasattr(row, 'keys'):
                    # Mapping style
                    ssl_info.update(dict(row))
                else:
                    # Manual mapping using column names
                    columns = list(result.keys())
                    ssl_info.update({col: val for col, val in zip(columns, row)})
                    
            except Exception as e:
                ssl_info['basic_info_error'] = str(e)
            
            # SSL-specific details (these functions may not exist in all PostgreSQL versions)
            ssl_functions = [
                ('ssl_cipher', 'ssl_cipher()'),
                ('ssl_version', 'ssl_version()'),
                ('ssl_client_cert_present', 'ssl_client_cert_present()'),
                ('ssl_client_serial', 'ssl_client_serial()'),
                ('ssl_client_dn', 'ssl_client_dn()'),
                ('ssl_issuer_dn', 'ssl_issuer_dn()')
            ]
            
            for field_name, function_call in ssl_functions:
                try:
                    result = conn.execute(text(f"SELECT {function_call} as {field_name}"))
                    value = result.fetchone()[0]
                    ssl_info[field_name] = value
                    if field_name == 'ssl_cipher' and value:
                        ssl_info['ssl_active'] = True
                except Exception:
                    # Function doesn't exist or SSL not active
                    ssl_info[field_name] = None
            
            # Determine if SSL is active based on available information
            if 'ssl_active' not in ssl_info:
                # If we couldn't get ssl_cipher, try to infer SSL status
                ssl_info['ssl_active'] = ssl_info.get('ssl_cipher') is not None
            
            print("SSL Connection Test Results:")
            print("-" * 40)
            for key, value in ssl_info.items():
                print(f"{key}: {value}")
            print("-" * 40)
            
            return ssl_info
            
    except Exception as e:
        print(f"SSL connection test failed: {e}")
        raise

# Rest of your existing functions remain the same...
def dataGrabber(query, engine, limit='None', debug=False):
    """
    Execute query using SQLAlchemy engine and return pandas DataFrame with robust error handling.
    
    Args:
        query (str): SQL query to execute
        engine: SQLAlchemy engine object
        limit (str): Limit clause for query, defaults to 'None'
        debug (bool): Enable detailed debugging output
    
    Returns:
        pandas.DataFrame: Query results
        
    Raises:
        Exception: If all fallback methods fail
    """
    # Configure logging for detailed error diagnosis
    if debug:
        logging.basicConfig(level=logging.DEBUG)
        logger = logging.getLogger(__name__)
    else:
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.WARNING)
    
    # Handle limit for PostgreSQL
    if limit != 'None':
        limitString = f'LIMIT {limit}'
        query = query.replace('FOR READ ONLY', limitString + ' FOR READ ONLY')
    
    start = time.time()
    
    # Method 1: Standard pandas.read_sql() approach
    try:
        logger.debug("Attempting Method 1: Standard pandas.read_sql()")
        data = pd.read_sql(query, engine)
        logger.debug("Method 1 successful")
        
    except Exception as e:
        error_msg = str(e).lower()
        logger.warning(f"Method 1 failed: {e}")
        
        # Check if this is the specific immutabledict error
        is_metadata_error = any(keyword in error_msg for keyword in [
            'immutabledict', 'not a sequence', 'metadata', 'result'
        ])
        
        if is_metadata_error:
            logger.info("Detected metadata interpretation error, trying fallback methods...")
            
            # Method 2: Use connection directly with pandas
            try:
                logger.debug("Attempting Method 2: Direct connection with pandas")
                with engine.connect() as conn:
                    data = pd.read_sql(query, conn)
                logger.debug("Method 2 successful")
                
            except Exception as e2:
                logger.warning(f"Method 2 failed: {e2}")
                
                # Method 3: Use raw SQLAlchemy execution with manual DataFrame construction
                try:
                    logger.debug("Attempting Method 3: Manual DataFrame construction")
                    data = _execute_with_manual_construction(query, engine, logger)
                    logger.debug("Method 3 successful")
                    
                except Exception as e3:
                    logger.warning(f"Method 3 failed: {e3}")
                    
                    # Method 4: Try with different pandas parameters
                    try:
                        logger.debug("Attempting Method 4: Alternative pandas parameters")
                        data = _execute_with_alternative_params(query, engine, logger)
                        logger.debug("Method 4 successful")
                        
                    except Exception as e4:
                        logger.error(f"All methods failed. Final error: {e4}")
                        _print_comprehensive_error_report(query, engine, [e, e2, e3, e4], logger)
                        raise Exception(f"All fallback methods failed. Original error: {e}")
        else:
            # Non-metadata error, re-raise immediately with better context
            logger.error(f"Non-metadata error encountered: {e}")
            raise Exception(f"Query execution failed (non-metadata error): {e}")
    
    # Calculate and display timing
    end = time.time()
    elapsed = end - start
    
    m, s = divmod(elapsed, 60)
    h, m = divmod(m, 60)
    
    totTime = 'Elapsed Time: '
    eTime = "%d:%02d:%02d" % (h, m, s)
    totTime += eTime
    print(totTime)
    
    # Play notification sound
    play_notification_sound()
    
    # Final data validation
    if data is None or data.empty:
        logger.warning("Query returned empty result set")
    else:
        logger.debug(f"Successfully returned DataFrame with shape: {data.shape}")
    
    return data

def recursiveDataGrabber(query_dict, results_dict, n=1, max_attempts=50):
    """
    Recursively execute queries with exponential backoff retry logic
    
    Args:
        query_dict (dict): Dictionary of query names and SQL strings
        results_dict (dict): Dictionary to store results
        n (int): Current attempt number
        max_attempts (int): Maximum number of retry attempts
        
    Returns:
        dict: Results dictionary with DataFrames or None for failed queries
    """
    def ordinal(i):
        return str(i) + {1:"st", 2:"nd", 3:"rd"}.get(i%10*(i%100 not in [11,12,13]), "th")
    
    if n <= max_attempts:
        if n > 1:
            print(f"{ordinal(n)} attempt")
            # Exponential backoff: Wait before retrying
            wait_time = min(2**(n-1), 600)  # Max wait time of 10 minutes
            print(f"Waiting for {wait_time:.2f} seconds before retry...")
            time.sleep(wait_time)
        
        engine = None
        try:
            # Create PostgreSQL engine
            engine = createPostgresqlEngine()
            
            # Test the connection
            with engine.connect() as conn:
                print("PostgreSQL database connection successful!")
            
            for k, v in query_dict.items():
                try:
                    results_dict[k] = dataGrabber(v, engine)
                    print(f"Query '{k}' completed successfully")
                except Exception as e:
                    print(f"Query '{k}' failed: {e}")
                    results_dict[k] = None
            
            # Save results
            dumpname = f'../Data/postgresql_results_attempt_{n}.pkl'
            os.makedirs(os.path.dirname(dumpname), exist_ok=True)
            
            with open(dumpname, 'wb') as f:
                pickle.dump(results_dict, f)
            
        except Exception as e:
            print(f"Database connection error at attempt {n}: {e}")
            for k in query_dict.keys():
                if k not in results_dict or not isinstance(results_dict[k], pd.DataFrame):
                    results_dict[k] = None
        
        finally:
            if engine:
                try:
                    engine.dispose()
                    print('PostgreSQL database connection closed.')
                except Exception as e:
                    print(f"Error closing engine: {e}")
        
        # Determine which queries need retry
        redo_dict = {k: v for k, v in query_dict.items() 
                    if not isinstance(results_dict.get(k), pd.DataFrame) or results_dict.get(k) is None}
        
        if redo_dict:
            failed_query_names = ", ".join(redo_dict.keys())
            print(f"{len(redo_dict)} {'query' if len(redo_dict) == 1 else 'queries'} remain: {failed_query_names}")
            return recursiveDataGrabber(redo_dict, results_dict, n+1, max_attempts)
        else:
            print("All queries completed successfully!")
            return results_dict
    
    else:
        print(f"Maximum retry attempts ({max_attempts}) reached.")
        failed_queries = [k for k, v in query_dict.items() 
                         if not isinstance(results_dict.get(k), pd.DataFrame) or results_dict.get(k) is None]
        if failed_queries:
            print(f"Failed queries: {', '.join(failed_queries)}")
        return results_dict

def _execute_with_manual_construction(query, engine, logger):
    """
    Fallback method: Execute query manually and construct DataFrame.
    
    This method bypasses pandas.read_sql() entirely and manually constructs
    the DataFrame from SQLAlchemy results.
    """
    logger.debug("Starting manual DataFrame construction")
    
    with engine.connect() as conn:
        # Execute query and fetch results
        result = conn.execute(text(query))
        
        # Get column names - handle different SQLAlchemy versions
        try:
            columns = list(result.keys())
        except AttributeError:
            # Older SQLAlchemy versions
            columns = list(result._metadata.keys)
        
        logger.debug(f"Columns detected: {columns}")
        
        # Fetch all rows
        rows = result.fetchall()
        logger.debug(f"Fetched {len(rows)} rows")
        
        # Convert to list of dictionaries for DataFrame construction
        data_dicts = []
        for row in rows:
            # Handle different row types
            if hasattr(row, '_asdict'):
                # Named tuple style
                row_dict = row._asdict()
            elif hasattr(row, 'keys'):
                # Mapping style
                row_dict = dict(row)
            else:
                # Fallback: create dict manually
                row_dict = {col: val for col, val in zip(columns, row)}
            
            data_dicts.append(row_dict)
        
        # Create DataFrame
        df = pd.DataFrame(data_dicts)
        logger.debug(f"Created DataFrame with shape: {df.shape}")
        
        return df


def _execute_with_alternative_params(query, engine, logger):
    """
    Fallback method: Try pandas.read_sql() with different parameters.
    
    This method experiments with different pandas parameters that might
    resolve metadata interpretation issues.
    """
    logger.debug("Trying alternative pandas parameters")
    
    # Try different parameter combinations
    param_combinations = [
        {'coerce_float': False},
        {'parse_dates': None},
        {'params': None, 'coerce_float': False, 'parse_dates': None},
        {'chunksize': None}
    ]
    
    for i, params in enumerate(param_combinations):
        try:
            logger.debug(f"Trying parameter set {i+1}: {params}")
            with engine.connect() as conn:
                data = pd.read_sql(query, conn, **params)
            logger.debug(f"Parameter set {i+1} successful")
            return data
        except Exception as e:
            logger.debug(f"Parameter set {i+1} failed: {e}")
            continue
    
    raise Exception("All alternative parameter combinations failed")


def _print_comprehensive_error_report(query, engine, errors, logger):
    """
    Print a comprehensive error report for debugging purposes.
    """
    logger.error("=" * 60)
    logger.error("COMPREHENSIVE ERROR REPORT")
    logger.error("=" * 60)
    
    logger.error(f"Query: {query[:200]}{'...' if len(query) > 200 else ''}")
    logger.error(f"Engine: {engine}")
    logger.error(f"Engine URL: {engine.url}")
    
    logger.error("\nERROR SEQUENCE:")
    for i, error in enumerate(errors, 1):
        logger.error(f"Method {i}: {error}")
    
    logger.error("\nDEBUG SUGGESTIONS:")
    logger.error("1. Check if query works in DBeaver/pgAdmin")
    logger.error("2. Try simplifying the query (remove complex JOINs, subqueries)")
    logger.error("3. Check for special characters or data types in result set")
    logger.error("4. Verify SQLAlchemy and pandas versions compatibility")
    logger.error("5. Test with a LIMIT clause to reduce result set size")
    
    logger.error("=" * 60)


def diagnose_connection_and_query(engine, query, limit=10):
    """
    Diagnostic function to help troubleshoot SQLAlchemy/pandas issues.
    
    Args:
        engine: SQLAlchemy engine
        query: SQL query to diagnose
        limit: Number of rows to test with (default 10)
    
    Returns:
        dict: Diagnostic information
    """
    diagnostics = {
        'engine_info': {},
        'query_info': {},
        'test_results': {},
        'recommendations': []
    }
    
    # Engine diagnostics
    try:
        diagnostics['engine_info'] = {
            'url': str(engine.url),
            'driver': engine.url.drivername,
            'database': engine.url.database,
            'sqlalchemy_version': None  # Would need to import sqlalchemy.__version__
        }
    except Exception as e:
        diagnostics['engine_info']['error'] = str(e)
    
    # Query diagnostics
    diagnostics['query_info'] = {
        'length': len(query),
        'contains_limit': 'LIMIT' in query.upper(),
        'contains_for_read_only': 'FOR READ ONLY' in query.upper()
    }
    
    # Test with limited results
    test_query = f"SELECT * FROM ({query}) subq LIMIT {limit}"
    try:
        test_data = dataGrabber(test_query, engine, debug=True)
        diagnostics['test_results'] = {
            'success': True,
            'shape': test_data.shape,
            'columns': list(test_data.columns),
            'dtypes': test_data.dtypes.to_dict()
        }
    except Exception as e:
        diagnostics['test_results'] = {
            'success': False,
            'error': str(e)
        }
    
    # Generate recommendations
    if not diagnostics['test_results'].get('success', False):
        diagnostics['recommendations'].extend([
            "Test query fails even with LIMIT - issue may be with query structure",
            "Try running query directly in database client",
            "Check for unsupported data types in result set"
        ])
    
    return diagnostics
