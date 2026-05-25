import sys
import awswrangler as wr
import pandas as pd

# Rutas S3
INPUT_PATH = "s3://citibike-datalake-seb/landing/citibike-data/"
OUTPUT_PATH = "s3://citibike-datalake-seb/curated/citibike_trips/citibike_curated.snappy.parquet"

# Leer Parquet desde S3
df = wr.s3.read_parquet(path=INPUT_PATH)
print(f" [!] Shape original: {df.shape}")

# Crear features
df["starttime"] = pd.to_datetime(df["starttime"], errors="coerce")
df["year"] = df["starttime"].dt.year
df["hour"] = df["starttime"].dt.hour
df["month"] = df["starttime"].dt.month
df["dayofweek"] = df["starttime"].dt.dayofweek

# - Recordar: En Pandas lunes = 0 y domingo = 6
df["is_weekend"] = df["dayofweek"].isin([5, 6]).astype(int)
df["age"] = df["year"] - df["birth_year"]

# Filtrar outliers
df = df[
    (df["tripduration"] > 60) &
    (df["tripduration"] < 3600) &
    (df["age"] <= 90)
].copy()

print(f" [!] Shape despues del filtro: {df.shape}")

# Evitar data leakage
df = df.drop(columns=["end_station_id"])

# Guardar en S3 Curated

wr.s3.to_parquet(
    df=df,
    path=OUTPUT_PATH,
    dataset=False,
    compression="snappy"
)

print(f" [!] Dataset curated guardado en: {OUTPUT_PATH}")
