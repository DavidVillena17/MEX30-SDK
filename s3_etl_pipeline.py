import argparse
import csv
import io
import logging
from datetime import datetime

import boto3
from botocore.exceptions import ClientError

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

boto3.setup_default_session(profile_name='s3')

def get_s3_client(region: str):
    """Retorna un cliente S3 para la región especificada."""
    return boto3.client('s3', region_name=region)

def preparar_buckets(s3_client, region: str, bucket_raw: str, bucket_processed: str) -> bool:
    """Crea los buckets necesarios para el pipeline si no existen."""
    buckets = [bucket_raw, bucket_processed]
    todas_creadas = True
    
    for b in buckets:
        try:
            if region == 'us-east-1':
                s3_client.create_bucket(Bucket=b)
            else:
                s3_client.create_bucket(
                    Bucket=b, 
                    CreateBucketConfiguration={'LocationConstraint': region}
                )
            logger.info(f"Bucket listo: {b}")
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'BucketAlreadyOwnedByYou':
                logger.info(f"El bucket '{b}' ya te pertenece y está listo.")
            elif error_code == 'BucketAlreadyExists':
                logger.error(f"Error: El nombre '{b}' ya está en uso por otro usuario a nivel global.")
                todas_creadas = False
            else:
                logger.error(f"Error inesperado al crear '{b}': {e}")
                todas_creadas = False
                
    return todas_creadas

def procesar_metricas_ventas(contenido_csv: str) -> str:
    """Analiza datos del CSV en memoria y genera un reporte de texto."""
    f = io.StringIO(contenido_csv)
    lector = csv.DictReader(f)
    
    total_ingresos = 0
    total_articulos = 0
    categorias = []
    
    for fila in lector:
        try:
            cantidad = int(fila['cantidad'])
            precio = float(fila['precio_unitario'])
            
            total_ingresos += (cantidad * precio)
            total_articulos += cantidad
            categorias.append(fila['categoria'])
        except KeyError as e:
            logger.error(f"Falta columna esperada en el CSV: {e}")
        except ValueError as e:
            logger.error(f"Valor numérico inválido en el CSV: {e}")
            
    if not categorias:
        return "Error: No se pudo generar el reporte. Datos insuficientes."
        
    categoria_top = max(set(categorias), key=categorias.count)
    
    # Generar reporte formateado
    reporte = (
        f"--- RESUMEN DE VENTAS DIARIAS ---\n"
        f"Fecha de Procesamiento: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
        f"----------------------------------\n"
        f"Ingresos Totales: ${total_ingresos:,.2f}\n"
        f"Total de Artículos Vendidos: {total_articulos}\n"
        f"Categoría más Vendida: {categoria_top}\n"
        f"Promedio por Transacción: ${total_ingresos/max(1, len(categorias)):,.2f}\n"
    )
    return reporte

def ejecutar_pipeline(s3_client, archivo_local: str, bucket_raw: str, bucket_processed: str):
    logger.info("Iniciando Pipeline ETL...")
    
    # A. Ingesta (Upload)
    s3_key_raw = f"raw/{archivo_local.split('/')[-1]}"
    try:
        logger.info(f"Subiendo archivo origen '{archivo_local}' a la capa Raw...")
        s3_client.upload_file(archivo_local, bucket_raw, s3_key_raw)
    except FileNotFoundError:
        logger.error(f"Archivo local '{archivo_local}' no encontrado. Abortando pipeline.")
        return
    except Exception as e:
        logger.error(f"Error al subir a bucket raw: {e}")
        return
        
    # B. Transformación (Read & Process)
    try:
        logger.info("Descargando de capa Raw para procesar en memoria...")
        obj = s3_client.get_object(Bucket=bucket_raw, Key=s3_key_raw)
        cuerpo = obj['Body'].read().decode('utf-8')
        
        logger.info("Transformando datos y calculando métricas...")
        reporte_final = procesar_metricas_ventas(cuerpo)
    except Exception as e:
        logger.error(f"Error en fase de transformación: {e}")
        return
        
    # C. Carga (Output)
    try:
        nombre_reporte = f"reportes/resultado_{datetime.now().strftime('%H%M')}.txt"
        logger.info("Guardando reporte final en capa Processed...")
        s3_client.put_object(Bucket=bucket_processed, Key=nombre_reporte, Body=reporte_final)
        
        logger.info(f"Proceso ETL completado exitosamente.")
        logger.info(f"Reporte guardado como: s3://{bucket_processed}/{nombre_reporte}")
        print("\n--- Vista Previa del Reporte ---\n" + reporte_final)
    except Exception as e:
        logger.error(f"Error en fase de carga final: {e}")

def main():
    parser = argparse.ArgumentParser(description="Pipeline ETL (Extract, Transform, Load) en AWS S3.")
    parser.add_argument("--region", type=str, default="us-east-1", help="Región AWS.")
    parser.add_argument("--bucket-raw", type=str, required=True, help="Nombre del bucket S3 para datos crudos.")
    parser.add_argument("--bucket-processed", type=str, required=True, help="Nombre del bucket S3 para datos procesados.")
    parser.add_argument("--file", type=str, default="./mis_archivos/datos_ventas.csv", help="Ruta del archivo local (CSV) a ingestar.")
    args = parser.parse_args()
    
    s3_client = get_s3_client(args.region)
    if preparar_buckets(s3_client, args.region, args.bucket_raw, args.bucket_processed):
        ejecutar_pipeline(s3_client, args.file, args.bucket_raw, args.bucket_processed)
    else:
        logger.error("No se pudo iniciar el pipeline debido a problemas con la infraestructura (Buckets).")

if __name__ == "__main__":
    main()
