### pg_helpers/config.py
"""Configuration and environment handling"""
import os
from pathlib import Path
from dotenv import load_dotenv

def load_env_with_fallback():
    """
    Load environment variables with flexible configuration.
    
    Behavior:
    - If CREDENTIALS_DIR and CREDENTIALS_FILE are both set: 
      load from {CREDENTIALS_DIR}/{CREDENTIALS_FILE}
    - If only CREDENTIALS_DIR is set: 
      load from {CREDENTIALS_DIR}/.env
    - If only CREDENTIALS_FILE is set: 
      load from ./{CREDENTIALS_FILE}
    - If neither is set (default): 
      load from ./.env
    
    Environment variables are checked BEFORE importing this module:
        import os
        os.environ['CREDENTIALS_DIR'] = r'C:\Documents\Project\Assets'
        os.environ['CREDENTIALS_FILE'] = '.env.pink_elephants'
        from pg_helpers import createPostgresqlEngine
    """
    credentials_dir = os.getenv('CREDENTIALS_DIR')
    credentials_file = os.getenv('CREDENTIALS_FILE')
    
    # Determine which path to use
    if credentials_dir and credentials_file:
        # Both specified: use full custom path
        env_path = Path(credentials_dir) / credentials_file
    elif credentials_dir:
        # Only directory specified: use default .env filename
        env_path = Path(credentials_dir) / '.env'
    elif credentials_file:
        # Only filename specified: use current directory
        env_path = Path(credentials_file)
    else:
        # Default: .env in current directory
        env_path = Path('.env')
    
    # Load the environment file
    load_dotenv(env_path)
    
    # Optional: Uncomment to see where env vars were loaded from
    # print(f"Loading environment from: {env_path}")

# Load environment variables when module is imported
load_env_with_fallback()

def get_db_config():
    """Get database configuration from environment variables"""
    return {
        'user': os.getenv('DB_USER'),
        'password': os.getenv('DB_PASSWORD'),
        'host': os.getenv('DB_HOST'),
        'port': os.getenv('DB_PORT', '5432'),
        'database': os.getenv('DB_NAME'),
        'ssl_mode': os.getenv('DB_SSL_MODE', 'require'),
        'ssl_ca_cert': os.getenv('DB_SSL_CA_CERT'),  # Optional CA certificate path
        'ssl_cert': os.getenv('DB_SSL_CERT'),        # Optional client certificate
        'ssl_key': os.getenv('DB_SSL_KEY')           # Optional client key
    }

def validate_db_config():
    """Validate that required environment variables are set"""
    config = get_db_config()
    required_keys = ['user', 'password', 'host', 'database']
    
    missing = [key for key in required_keys if not config[key]]
    if missing:
        raise ValueError(f"Missing required environment variables: {missing}")
    
    if config['ssl_ca_cert'] and not os.path.exists(config['ssl_ca_cert']):
        raise ValueError(f"SSL CA certificate file not found: {config['ssl_ca_cert']}")
    
    if config['ssl_cert'] and not os.path.exists(config['ssl_cert']):
        raise ValueError(f"SSL client certificate file not found: {config['ssl_cert']}")
    
    if config['ssl_key'] and not os.path.exists(config['ssl_key']):
        raise ValueError(f"SSL client key file not found: {config['ssl_key']}")
    
    return config

def get_ssl_params():
    """Get SSL parameters for connection string"""
    config = get_db_config()
    ssl_params = []
    
    ssl_params.append(f"sslmode={config['ssl_mode']}")
    
    if config['ssl_ca_cert']:
        ssl_params.append(f"sslrootcert={config['ssl_ca_cert']}")
    
    if config['ssl_cert']:
        ssl_params.append(f"sslcert={config['ssl_cert']}")
    
    if config['ssl_key']:
        ssl_params.append(f"sslkey={config['ssl_key']}")
    
    return '&'.join(ssl_params)
