import os
import boto3
from dotenv import load_dotenv
from pathlib import Path
from google.cloud import bigquery
from google.auth.exceptions import DefaultCredentialsError

FILE_NAME = "citibike_trips.parquet" 
BASE_DIR = Path(__file__).resolve().parent 
OUTPUT_PATH = BASE_DIR / "../data/raw" / FILE_NAME 

QUERY = """
SELECT
  tripduration,
  starttime,
  start_station_id,
  end_station_id,
  usertype,
  gender,
  birth_year
FROM
  `bigquery-public-data.new_york_citibike.citibike_trips`
WHERE
  tripduration IS NOT NULL
  AND birth_year IS NOT NULL
  AND tripduration > 60
  AND tripduration < 7200
  AND RAND() < 0.01
"""

def load_environment():
    env_path = BASE_DIR.parent / ".env"
    load_dotenv(dotenv_path=env_path)
    print(f"[1] Variable de entorno cargada")

def get_bigquery_client():
    try:
        cred_path = Path(os.getenv("GOOGLE_APPLICATION_CREDENTIALS")).resolve()
        if not cred_path:
            raise ValueError("[x] La variable GOOGLE_APPLICATION_CREDENTIALS no esta definida en .env")
        if not Path(cred_path).exists():
            raise FileNotFoundError(f"[x] No se encontro el archivo: {cred_path}")
        print("[2] Cliente de BigQuery creado")
        return bigquery.Client()

    except DefaultCredentialsError as e:
        print(f"[x] Error de credenciales: {e}")
        return None
    
    except Exception as e:
        print(f"[x] Error creando cliente: {e}")

def run_query(client):
    try:
        print("[3] Ejecutando consulta en BigQuery")
        return client.query(QUERY).to_dataframe()

    except Exception as e:
        print(f"[x] Error ejecutando query: {e}")
        return None

def save_parquet(df):
    try:
        OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
        df.to_parquet(OUTPUT_PATH)
        print("[4] Muestra obtenida en formato .parquet")
        print(f" - Datos guardados en: {str(OUTPUT_PATH)[0:45]}{str(OUTPUT_PATH)[48:]}")
    except Exception as e:
        print(f"[x] Error guardando archivo: {e}")

def save_parquet_s3(df):
    try:
        s3 = boto3.client('s3')
        params = ['../data/raw/citibike_trips.parquet', 'citibike-datalake-seb', 'landing/citibike_trips.parquet']
        s3.upload_file(params[0], params[1], params[2])
        print("[5] Conexion con Bucket S3 establecida")
        print(f" - Datos guardados en Bucket S3: {params[1]}/{params[2]}")
    except FileNotFoundError:
        print("[x] Error: Archivo no encontrado.")

def main():
    """
    Flujo principal del extract:
    1. Carga variables de entorno.
    2. Crea cliente BigQuery.
    3. Ejecuta Query.
    4. Guarda resultados (local/S3).
    """
    print("Iniciando proceso de extraccion.\n")
    load_environment()
    
    client = get_bigquery_client()
    if not client:
        return 
    
    df = run_query(client)
    if df is None:
        return 
    
    save_parquet(df)
    save_parquet_s3(df)
    print("\nFin de proceso de extraccion.")

if __name__ == "__main__":
    main()
