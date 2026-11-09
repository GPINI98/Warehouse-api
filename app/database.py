import os
import oracledb
from dotenv import load_dotenv

load_dotenv() #crea la variabile dal file .env

def connessione_database():
# os.getenv recupera una variabile d'ambiente
    connessione = oracledb.connect(
        user=os.getenv("ORACLE_USER"),
        password=os.getenv("ORACLE_PASSWORD"),
        dsn=os.getenv("ORACLE_DSN"),
        config_dir=os.getenv("ORACLE_CONFIG_DIR"),
        wallet_location=os.getenv("ORACLE_CONFIG_DIR"),
        wallet_password=os.getenv("ORACLE_WALLET_PASSWORD")
    )

    return connessione