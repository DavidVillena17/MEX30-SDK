import boto3
import argparse
from datetime import datetime, timezone
from botocore.exceptions import ClientError

boto3.setup_default_session(profile_name='admin-profile')

def check_iam_keys(max_days=90):
    """Detecta llaves de acceso de IAM más viejas que el límite definido."""
    print(f"\n[!] Auditando llaves de acceso de IAM (Límite: {max_days} días)...")
    iam = boto3.client('iam')
    users = iam.list_users()['Users']
    
    now = datetime.now(timezone.utc)
    found_old_keys = False

    for user in users:
        username = user['UserName']
        access_keys = iam.list_access_keys(UserName=username)['AccessKeyMetadata']
        
        for key in access_keys:
            key_id = key['AccessKeyId']
            created_date = key['CreateDate']
            age_days = (now - created_date).days
            
            if age_days > max_days:
                print(f"  - ADVERTENCIA: Usuario '{username}' tiene llave {key_id} con {age_days} días de antigüedad.")
                found_old_keys = True
    
    if not found_old_keys:
        print("  [+] No se encontraron llaves de acceso obsoletas.")

def check_mfa():
    """Detecta usuarios de IAM que NO tienen MFA activado."""
    print("\n[!] Auditando Segundo Factor de Autenticación (MFA)...")
    iam = boto3.client('iam')
    users = iam.list_users()['Users']
    
    found_no_mfa = False
    for user in users:
        username = user['UserName']
        mfa_devices = iam.list_mfa_devices(UserName=username)['MFADevices']
        
        if not mfa_devices:
            print(f"  - PELIGRO: Usuario '{username}' NO tiene MFA activado.")
            found_no_mfa = True
            
    if not found_no_mfa:
        print("  [+] Todos los usuarios tienen MFA activado.")

def check_security_groups():
    """Busca Security Groups con puerto 22 (SSH) abierto a 0.0.0.0/0."""
    print("\n[!] Auditando Security Groups (Puerto 22 - SSH)...")
    ec2 = boto3.client('ec2')
    sgs = ec2.describe_security_groups()['SecurityGroups']
    
    found_open_ssh = False
    for sg in sgs:
        sg_id = sg['GroupId']
        sg_name = sg['GroupName']
        
        for permission in sg.get('IpPermissions', []):
            if permission.get('FromPort') == 22 or permission.get('IpProtocol') == '-1':
                for ip_range in permission.get('IpRanges', []):
                    if ip_range.get('CidrIp') == '0.0.0.0/0':
                        print(f"  - ALERTA: SG '{sg_name}' ({sg_id}) permite SSH desde CUALQUIER IP (0.0.0.0/0).")
                        found_open_ssh = True
                        
    if not found_open_ssh:
        print("  [+] No se encontraron Security Groups con SSH expuesto.")

def main():
    # Configuración de ARGPARSE
    parser = argparse.ArgumentParser(description="Herramienta de Auditoría de Seguridad AWS (MEX30-SDK)")
    
    # Añadimos argumentos que el usuario puede usar en la terminal
    parser.add_argument("--iam-keys", action="store_true", help="Auditar antigüedad de llaves de acceso IAM")
    parser.add_argument("--mfa", action="store_true", help="Auditar usuarios sin MFA activado")
    parser.add_argument("--network", action="store_true", help="Auditar Security Groups con SSH expuesto")
    parser.add_argument("--days", type=int, default=90, help="Días límite para llaves IAM (por defecto: 90)")
    parser.add_argument("--all", action="store_true", help="Ejecutar todas las auditorías")

    args = parser.parse_args()

    # Lógica basada en los argumentos recibidos
    if args.all or args.iam_keys:
        check_iam_keys(args.days)
    
    if args.all or args.mfa:
        check_mfa()
        
    if args.all or args.network:
        check_security_groups()
    
    # Si no se pasó ningún argumento, mostrar la ayuda
    if not (args.all or args.iam_keys or args.mfa or args.network):
        parser.print_help()

if __name__ == "__main__":
    main()
