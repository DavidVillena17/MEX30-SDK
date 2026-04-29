import argparse
import logging
import os

import boto3
from botocore.exceptions import ClientError

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

boto3.setup_default_session(profile_name='s3')

def get_s3_client(region: str):
    return boto3.client('s3', region_name=region)

def create_s3_bucket(s3_client, bucket_name: str, region: str) -> bool:
    """Asegura que el bucket exista en la región deseada."""
    try:
        if region == 'us-east-1':
            s3_client.create_bucket(Bucket=bucket_name)
        else:
            location = {'LocationConstraint': region}
            s3_client.create_bucket(Bucket=bucket_name, CreateBucketConfiguration=location)
        logger.info(f"Bucket '{bucket_name}' creado exitosamente.")
        return True
    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == 'BucketAlreadyOwnedByYou':
            logger.info(f"El bucket '{bucket_name}' ya te pertenece. Listo para sincronizar.")
            return True
        elif error_code == 'BucketAlreadyExists':
            logger.error(f"El nombre de bucket '{bucket_name}' ya está en uso por otro usuario.")
            return False
        else:
            logger.error(f"Error al crear el bucket: {e}")
            return False

def list_s3_files(s3_client, bucket: str) -> list:
    """Lista todos los objetos presentes en el bucket especificado."""
    try:
        # Usamos paginador por si hay más de 1000 objetos
        paginator = s3_client.get_paginator('list_objects_v2')
        pages = paginator.paginate(Bucket=bucket)
        
        archivos = []
        for page in pages:
            if 'Contents' in page:
                archivos.extend([obj['Key'] for obj in page['Contents']])
        return archivos
    except ClientError as e:
        logger.error(f"Error al listar archivos en S3: {e}")
        return []

def upload_missing_files(s3_client, directory: str, bucket: str):
    """Sube archivos locales a S3 si no existen allí."""
    s3_files = list_s3_files(s3_client, bucket)
    
    # Obtener listado ignorando carpetas localmente para simplificar la sinc (solo archivos en la raíz)
    local_files = [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]
    
    for file in local_files:
        if file not in s3_files:
            try:
                logger.info(f"Sincronizando -> Subiendo '{file}' a S3...")
                s3_client.upload_file(os.path.join(directory, file), bucket, file)
            except Exception as e:
                logger.error(f"Error al subir '{file}': {e}")
        else:
            logger.debug(f"'{file}' ya existe en S3. Omitiendo subida.")

def download_missing_files(s3_client, directory: str, bucket: str):
    """Descarga objetos de S3 si no existen en el directorio local."""
    s3_files = list_s3_files(s3_client, bucket)
    local_files = os.listdir(directory)
    
    for s3_file in s3_files:
        # Si s3_file tiene barras ("folder/archivo.txt"), podrías requerir lógica para directorios.
        # Aquí simplificamos para comparar el objeto base como asume el notebook
        base_s3_file = os.path.basename(s3_file)
        if base_s3_file not in local_files and base_s3_file != "":
            try:
                logger.info(f"Sincronizando <- Descargando '{s3_file}' desde S3...")
                # Soporte para rutas dentro del bucket (descarga todo en la raiz local)
                s3_client.download_file(bucket, s3_file, os.path.join(directory, base_s3_file))
            except Exception as e:
                logger.error(f"Error al descargar '{s3_file}': {e}")
        else:
            logger.debug(f"'{s3_file}' ya existe localmente. Omitiendo descarga.")

def main():
    parser = argparse.ArgumentParser(description="Herramienta de sincronización bidireccional S3 <> Local.")
    parser.add_argument("--bucket", type=str, required=True, help="Nombre del bucket objetivo en AWS S3.")
    parser.add_argument("--directory", type=str, required=True, help="Ruta del directorio local a sincronizar.")
    parser.add_argument("--region", type=str, default="us-east-1", help="Región AWS.")
    args = parser.parse_args()
    
    logger.info("--- Iniciando Sincronizador (Mirror) S3 ---")
    s3_client = get_s3_client(args.region)

    if not os.path.exists(args.directory):
        os.makedirs(args.directory)
        logger.info(f"Se creó el directorio local necesario: '{args.directory}'")

    if create_s3_bucket(s3_client, args.bucket, args.region):
        logger.info("Etapa 1: Verificando y sincronizando hacia la nube (Uploads pendientes)...")
        upload_missing_files(s3_client, args.directory, args.bucket)
        
        logger.info("Etapa 2: Verificando y sincronizando hacia local (Downloads pendientes)...")
        download_missing_files(s3_client, args.directory, args.bucket)
        
        logger.info("Estado actual en la nube de S3:")
        print(list_s3_files(s3_client, args.bucket))
    else:
        logger.error("Abortando sincronización por problemas con el Bucket.")
        
    logger.info("--- Sincronización Finalizada ---")

if __name__ == "__main__":
    main()
