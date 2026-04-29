# Proyectos de AWS Boto3 (MEX30-SDK)


## Introducción

**Propósito y Aspectos Generales**
El propósito de este repositorio es recopilar una serie de proyectos prácticos orientados a la administración y automatización de recursos en Amazon Web Services (AWS) utilizando programación en Python. A medida que la infraestructura en la nube crece, resulta ineficiente administrarla únicamente de forma manual desde la consola; por ello, este SDK permite escalar operaciones de forma profesional.

**Justificación**
La automatización de tareas con scripts de Python permite reducir el margen de error, aumentar la velocidad de ejecución y optimizar costos operativos. Estos proyectos demuestran, mediante casos de uso reales, cómo interactuar de forma programática con servicios clave de AWS, especialmente con S3 (almacenamiento), EC2 (cómputo) e IAM (identidad y acceso).

**Guía de instalación de AWS CLI para Linux**
AWS Command Line Interface (CLI) es una herramienta unificada que permite administrar los diferentes servicios de AWS desde la terminal.

Para instalar AWS CLI v2 en entornos Linux, ejecuta los siguientes comandos:

1. Descargar el instalador oficial:
   ```bash
   curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
   ```
2. Descomprimir el archivo:
   ```bash
   unzip awscliv2.zip
   ```
3. Ejecutar el script de instalación:
   ```bash
   sudo ./aws/install
   ```
4. Verificar la instalación:
   ```bash
   aws --version
   ```

> **Nota:** Es fundamental configurar tus credenciales mediante el comando `aws configure`. Esto solicitará tu *Access Key ID*, *Secret Access Key* y región por defecto para autorizar las peticiones del SDK.

**Tecnologías Utilizadas**
- **Python:** Lenguaje de programación principal empleado por su versatilidad en scripting y automatización.
- **Boto3:** El SDK oficial de AWS para Python. Permite la gestión completa de servicios de AWS directamente desde el código.
- **Scripts Autónomos (.py):** Todos los proyectos han sido migrados a scripts ejecutables desde la terminal para facilitar su integración en pipelines de automatización.

---

## Desarrollo

A continuación, se detalla el enfoque de cada uno de los proyectos incluidos:

### 1. Proyecto de Respaldo en S3 (`s3_backup.py`)
Permite automatizar el respaldo de archivos locales hacia la nube de Amazon S3.
* **Gestión de Buckets:** Valida la existencia del bucket y lo crea si es necesario.
* **Carga de Archivos:** Sube elementos locales de forma íntegra utilizando el SDK.
* **Verificación:** Lista los objetos cargados para confirmar la integridad del respaldo.

### 2. Proyecto de Sincronización a S3 (`s3_sync.py`)
Implementa una sincronización inteligente tipo "mirror" entre un directorio local y un bucket S3.
* **Comparación de Estados:** Evita transferencias duplicadas comparando archivos locales con objetos en la nube.
* **Sincronización Bidireccional:** Automatiza tanto la subida de archivos nuevos como la descarga de objetos faltantes en el host local.

### 3. Proyecto ETL Pipeline con S3 (`s3_etl_pipeline.py`)
Emula un pipeline de procesamiento de datos (Extraer, Transformar y Cargar) utilizando S3 como repositorio central.
* **Extracción:** Ingesta de datos crudos (Raw) desde local hacia S3.
* **Transformación:** Procesamiento en memoria para limpiar y calcular métricas de negocio.
* **Carga:** Almacenamiento del reporte final procesado en una capa de salida en S3.

### 4. Proyecto de Auditoría en EC2 (`ec2_describe.py`)
Herramienta de monitoreo para recursos de cómputo (EC2), orientada a la visibilidad administrativa.
* **Filtros de Inventario:** Consulta el estado de las instancias (Running/Stopped) y sus métricas básicas.
* **Descripción de Recursos:** Imprime detalles técnicos como IDs, tipos de instancia y llaves de acceso.

### 5. Proyecto de Limpieza en S3 (`s3_cleaner.py`)
Enfocado en la optimización de costos mediante la eliminación masiva de objetos obsoletos.
* **Análisis de Retención:** Identifica archivos antiguos basándose en su fecha de última modificación.
* **Limpieza de Infraestructura:** Permite eliminar objetos en lote y desmontar buckets vacíos que ya no se utilizan.

### 6. Proyecto de Auditoría de Seguridad (`aws_security_audit.py`)

Script especializado en fortalecer la postura de seguridad de la cuenta de AWS.
* **Auditoría de IAM:** Detecta llaves de acceso antiguas que necesitan rotación y usuarios sin MFA activado.
* **Seguridad de Red:** Identifica Security Groups con el puerto 22 (SSH) expuesto al mundo (0.0.0.0/0).

---

## Resultados y Conclusión

**Resultados**
A través de estos scripts, se ha logrado automatizar tareas críticas de administración en AWS sin depender de la consola web. Desde operaciones de almacenamiento masivo y procesos ETL, hasta la monitorización de seguridad y auditoría de recursos de cómputo, el uso de Boto3 garantiza precisión y escalabilidad.

**Conclusión**
La transición de tareas manuales a scripts programáticos incrementa la confiabilidad de la infraestructura. El enfoque de "Infraestructura como Código" adoptado en este repositorio permite adaptar las soluciones de AWS a necesidades digitales modernas, logrando flujos de trabajo eficientes, seguros y automatizados.