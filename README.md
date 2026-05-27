# Extract-Bigquery-Dataset

Pipeline de extracción de datos desde Google BigQuery hacia Amazon S3, como primera etapa de un pipeline DataOps sobre el dataset público **NYC Citi Bike Trips**.

## ¿Qué hace?

1. Se conecta a BigQuery usando una Service Account con permisos de solo lectura
2. Ejecuta una query con muestreo aleatorio (`RAND() < 0.01`) y filtros de calidad
3. Guarda el resultado localmente como `.parquet`
4. Sube el archivo a S3 

El ETL posterior (`docs/PipelineETL_AwsGLue.py`) se ejecuta como Job en AWS Glue Python Shell sobre los datos en S3.

## Estructura

```
Extract-Bigquery-Dataset/
├── src/
│   └── extract.py              # Script principal de extracción
├── docs/
│   ├── PipelineETL_AwsGLue.py  # Job ETL para AWS Glue Python Shell
│   ├── EDA_Citibike_trips.ipynb
│   └── citibike_optimized_architecture.png
├── .env.example
├── .gitignore
├── requirements.txt
└── tu_clave_privada_bigquery.json  # NO incluido — ver .env.example
```

## Requisitos

- Python 3.10+
- Cuenta de Google Cloud con acceso a BigQuery (Service Account JSON)
- AWS CLI configurado con credenciales válidas (`~/.aws/credentials`)
- Bucket S3 destino creado

```bash
pip install -r requirements.txt
```

## Configuración

Copia `.env.example` a `.env` y completa los valores:

```env
GOOGLE_APPLICATION_CREDENTIALS=../tu_clave_privada_bigquery.json
```

Las credenciales de AWS se leen desde `~/.aws/credentials` (configuradas con `aws configure` o pegadas desde AWS Academy Learner Lab).

## Uso

```bash
python src/extract.py
```

Output esperado:

```
Iniciando proceso de extraccion.

[1] Variable de entorno cargada
[2] Cliente de BigQuery creado
[3] Ejecutando consulta en BigQuery
[4] Muestra obtenida en formato .parquet
 - Datos guardados en: .../data/raw/citibike_trips.parquet
[5] Conexion con Bucket S3 establecida
 - Datos guardados en Bucket S3: citibike-datalake-seb/landing/citibike_trips.parquet

Fin de proceso de extraccion.
```

## Dataset

| Campo | Detalle |
|---|---|
| Fuente | `bigquery-public-data.new_york_citibike.citibike_trips` |
| Muestra | ~1% aleatorio (~474.491 registros) |
| Filtros | `tripduration` entre 60s y 7200s, `birth_year` no nulo |
| Columnas | `tripduration`, `starttime`, `start_station_id`, `end_station_id`, `usertype`, `gender`, `birth_year` |
| Formato salida | Snappy Parquet |

## Seguridad

- La Service Account JSON y el archivo `.env` están excluidos del repositorio vía `.gitignore`
- Las credenciales AWS no se almacenan en el código
- El bucket S3 tiene cifrado SSE-S3 habilitado (AES-256)

