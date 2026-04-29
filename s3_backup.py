import argparse
import logging
import os
import zipfile
from datetime import datetime

import boto3
from botocore.exceptions import ClientError

boto3.setup_default_session(profile_name='s3')

# Configurar el logger para una salida más profesional que simplemente 'print'
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def compress_folder(folder_path: str, output_zip_name: str) -> bool:
    """
    Comprime todo el contenido de una carpeta en un archivo .zip.
    
    Args:
        folder_path (str): Ruta de la carpeta a comprimir.
        output_zip_name (str): Nombre del archivo .zip saliente.
        
    Returns:
        bool: True si la compresión fue exitosa, False en caso contrario.
    """
    try:
        with zipfile.ZipFile(output_zip_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(folder_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, folder_path)
                    zipf.write(file_path, arcname)
        logger.info(f"Carpeta comprimida exitosamente: {output_zip_name}")
        return True
    except Exception as e:
        logger.error(f"Error al comprimir la carpeta '{folder_path}': {e}")
        return False

def upload_backup_to_s3(zip_filename: str, bucket_name: str, s3_key: str, s3_client=None) -> bool:
    """
    Sube un archivo de backup a un bucket de S3.
    """
    if s3_client is None:
        s3_client = boto3.client('s3')
        
    try:
        logger.info(f"Subiendo backup '{zip_filename}' a S3...")
        s3_client.upload_file(zip_filename, bucket_name, s3_key)
        logger.info(f"Backup completado exitosamente: s3://{bucket_name}/{s3_key}")
        return True
    except ClientError as e:
        logger.error(f"Error de permisos o conexión con AWS: {e}")
        return False
    except Exception as e:
        logger.error(f"Error inesperado al subir a S3: {e}")
        return False

def run_zipped_backup(source_dir: str, bucket_name: str) -> None:
    """
    Comprime una carpeta local y la sube a S3 con una estructura basada en la fecha.
    """
    if not os.path.exists(source_dir):
        logger.error(f"La carpeta o ruta '{source_dir}' no existe. Verifica e intenta nuevamente.")
        return

    # 1. Generar nombres basados en tiempo
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
    zip_filename = f"backup_{timestamp}.zip"
    s3_key = f"backups/archives/{timestamp}/{zip_filename}"
    
    # 2. Comprimir la carpeta en un zip temporal local
    if compress_folder(source_dir, zip_filename):
        # 3. Subir el zip a S3
        upload_success = upload_backup_to_s3(zip_filename, bucket_name, s3_key)
        
        # 4. Limpieza: Eliminar el zip local después de subirlo (haya sido exitoso o no)
        try:
            if os.path.exists(zip_filename):
                os.remove(zip_filename)
                logger.info("Archivo temporal local eliminado de manera segura.")
        except OSError as e:
            logger.warning(f"No se pudo eliminar el archivo temporal '{zip_filename}': {e}")
            
        if not upload_success:
            logger.error("El proceso finalizó, pero el archivo NO pudo subirse a S3.")
    else:
        logger.warning("El proceso se detuvo porque falló la compresión local.")

if __name__ == "__main__":
    # Configurar el analizador de argumentos de línea de comandos (CLI)
    parser = argparse.ArgumentParser(description="Automatización de respaldos (Backups) hacia AWS S3.")
    parser.add_argument(
        "--source", 
        type=str, 
        required=True, 
        help="Ruta de la carpeta local que se desea respaldar (default: ./mis_archivos/)."
    )
    parser.add_argument(
        "--bucket", 
        type=str, 
        required=True, 
        help="Nombre del bucket de destino en AWS S3."
    )
    
    # Parsear los argumentos pasados en la terminal
    args = parser.parse_args()
    
    logger.info("Iniciando el proceso de backup...")
    # Ejecutar el flujo de trabajo principal usando los argumentos recibidos
    run_zipped_backup(args.source, args.bucket)
