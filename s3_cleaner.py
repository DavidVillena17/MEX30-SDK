import argparse
import logging
from datetime import datetime, timedelta, timezone

import boto3
from botocore.exceptions import ClientError

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

boto3.setup_default_session(profile_name='s3')

def cleanup_old_backups(bucket_name: str, retention_days: int) -> None:
    """
    Lista y elimina objetos en un bucket de S3 que tengan más de 'retention_days' de antigüedad.
    """
    s3_client = boto3.client('s3')
    ahora = datetime.now(timezone.utc)
    limite_fecha = ahora - timedelta(days=retention_days)
    
    logger.info(f"Buscando y limpiando archivos anteriores a: {limite_fecha.strftime('%Y-%m-%d %H:%M:%S UTC')}")
    logger.info(f"Bucket Objetivo: {bucket_name}")

    try:
        # Listar objetos en el bucket usando paginador para manejar >1000 objetos si los hay
        paginator = s3_client.get_paginator('list_objects_v2')
        pages = paginator.paginate(Bucket=bucket_name)

        objetos_eliminados = 0
        bucket_vacio_o_sin_coincidencias = True
        
        for page in pages:
            if 'Contents' in page:
                bucket_vacio_o_sin_coincidencias = False
                for obj in page['Contents']:
                    fecha_archivo = obj['LastModified']
                    nombre_archivo = obj['Key']
                    
                    # Verificar si el archivo es más antiguo que el límite permitido
                    if fecha_archivo < limite_fecha:
                        logger.info(f"Eliminando: {nombre_archivo} (Fecha modificado: {fecha_archivo.strftime('%Y-%m-%d')})")
                        s3_client.delete_object(Bucket=bucket_name, Key=nombre_archivo)
                        objetos_eliminados += 1

        if bucket_vacio_o_sin_coincidencias:
            logger.info("El bucket fue escaneado. Está vacío o no tiene objetos que superen el tiempo de retención.")

        logger.info(f"Limpieza completada exitosamente. Total de objetos eliminados: {objetos_eliminados}")

    except ClientError as e:
        logger.error(f"Error de permisos o al conectar con S3: {e}")
    except Exception as e:
        logger.error(f"Error inesperado durante la limpieza: {e}")

def main():
    parser = argparse.ArgumentParser(description="Auditoría y limpieza de almacenamiento inactivo en AWS S3.")
    parser.add_argument(
        "--bucket", 
        type=str, 
        required=True, 
        help="Nombre del bucket de destino en AWS S3 a limpiar."
    )
    parser.add_argument(
        "--days", 
        type=int, 
        default=30, 
        help="Número de días de retención. Archivos más antiguos serán eliminados (default: 30)."
    )
    args = parser.parse_args()
    
    logger.info("Iniciando auditoría de limpieza en S3...")
    cleanup_old_backups(args.bucket, args.days)

if __name__ == "__main__":
    main()
