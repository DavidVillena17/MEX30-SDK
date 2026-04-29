import argparse
import logging
import boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

boto3.setup_default_session(profile_name='admin-profile')

def get_ec2_client(region: str):
    """
    Inicializa el cliente de EC2 en la región especificada.
    """
    try:
        return boto3.client('ec2', region_name=region)
    except Exception as e:
        logger.error(f"Error al conectar con AWS en la región {region}: {e}")
        return None

def fetch_ec2_instances(region: str) -> list:
    """
    Obtiene la lista de instancias EC2 y extrae:
    ID, Estado, Tipo e IP Pública.
    """
    ec2 = get_ec2_client(region)
    if not ec2:
        return []

    instances_data = []
    
    try:
        logger.info(f"Obteniendo la lista de instancias EC2 en {region}...")
        # Paginación automática con describe_instances
        response = ec2.describe_instances()
        
        for reservation in response.get('Reservations', []):
            for instance in reservation.get('Instances', []):
                instance_info = {
                    "Instance ID": instance.get('InstanceId'),
                    "Estado": instance.get('State', {}).get('Name'),
                    "Tipo": instance.get('InstanceType'),
                    "IP Pública": instance.get('PublicIpAddress', 'N/A')
                }
                instances_data.append(instance_info)
                
        return instances_data

    except (NoCredentialsError, PartialCredentialsError):
        logger.error("No se encontraron credenciales de AWS configuradas. Por favor corre 'aws configure'.")
    except Exception as e:
        logger.error(f"Ocurrió un error inesperado al consultar EC2: {e}")
        
    return []

def main():
    parser = argparse.ArgumentParser(description="Monitoreo y Auditoría de Instancias EC2 en AWS.")
    parser.add_argument(
        "--region", 
        type=str, 
        default="us-east-1", 
        help="Región de AWS a auditar (default: us-west-2)."
    )
    
    args = parser.parse_args()
    
    logger.info(f"--- Iniciando Auditoría de Instancias EC2 ({args.region}) ---")
    data = fetch_ec2_instances(args.region)
    
    if data:
        # Formatear la salida tipo tabla en la consola de manera nativa sin pandas
        print("\n{:<20} | {:<12} | {:<12} | {:<15}".format("Instance ID", "Estado", "Tipo", "IP Pública"))
        print("-" * 68)
        for i, row in enumerate(data):
            print("{:<20} | {:<12} | {:<12} | {:<15}".format(
                row.get("Instance ID", ""),
                row.get("Estado", ""),
                row.get("Tipo", ""),
                row.get("IP Pública", "")
            ))
        print("\n")
        logger.info(f"Auditoría finalizada. Se encontraron {len(data)} instancias en total.")
    else:
        logger.warning("No se encontraron instancias o hubo un error en la conexión.")

if __name__ == "__main__":
    main()
