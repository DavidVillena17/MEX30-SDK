# Proyectos de AWS Boto3 (MEX30-SDK)

## Introducción

**Propósito y Aspectos Generales**
El propósito de este repositorio es recopilar una serie de proyectos prácticos orientados a la administración y automatización de recursos en Amazon Web Services (AWS) utilizando programación en Python.
A medida que la infraestructura en la nube crece, resulta difícil e ineficiente administrarla únicamente y de forma manual desde la consola gráfica. 

**Justificación**
La automatización de tareas con scripts de Python permite reducir el margen de error, aumentar la velocidad de ejecución y ahorrar tiempo. Estos proyectos, desarrollados de forma interactiva en Jupyter Notebooks (`.ipynb`), demuestran mediante casos de uso reales cómo interactuar de forma programática con servicios clave de AWS, especialmente con S3 (almacenamiento) y EC2 (cómputo).

**Guía de instalación de AWS CLI para Linux**
AWS Command Line Interface (CLI) es una herramienta unificada que permite administrar los diferentes servicios de AWS interactuando con ellos mediante comandos en la terminal desde cualquier lugar.

Para instalar AWS CLI v2 en entornos Linux (se requiere curl y unzip), se pueden seguir estos pasos en la terminal:

1. Descargar el archivo de instalación oficial:
   ```bash
   curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
   ```
2. Descomprimir el archivo descargado:
   ```bash
   unzip awscliv2.zip
   ```
3. Ejecutar el script de instalación correspondiente:
   ```bash
   sudo ./aws/install
   ```
4. Verificar que la instalación fue exitosa revisando la versión instalada:
   ```bash
   aws --version
   ```

> **Nota:** Para que todos los proyectos y scripts almacenados en este directorio interactúen debidamente con tu cuenta de AWS, es sumamente importante destacar que las credenciales fueron configuradas a través del comando `aws configure`. Esta herramienta te solicitará y guardará de forma segura el *AWS Access Key ID*, el *Secret Access Key* y la región por defecto, garantizando autorización al momento de realizar peticiones.

**Tecnologías Utilizadas**
- **Python:** Lenguaje de programación principal empleado por sus capacidades en scripting.
- **Jupyter Notebooks:** Entorno de desarrollo interactivo utilizado en todos los proyectos para documentar, estructurar y ejecutar el código fuente en celdas individuales para su fácil lectura.
- **Boto3:** Es el SDK (Software Development Kit) de Amazon Web Services, oficial para Python. Permite crear, configurar y gestionar servicios de AWS y realizar acciones que varían desde subir un archivo a encender servidores, de forma sencilla gracias a su uso integrado en el código.

---

## Desarrollo

A continuación, se detalla el enfoque de cada uno de los proyectos incluidos, listando en cada caso las funcionalidades que desarrollan internamente estos scripts:

### 1. Proyecto de Respaldo en S3 (`s3_backup_project.ipynb`)
Permite automatizar y asegurar el respaldo de archivos locales esenciales enviándolos a un almacenamiento en la nube de Amazon S3 de forma íntegra.
* **Crear el bucket:** Instrucciones para identificar la existencia de un bucket; de no existir, se emite la orden a AWS para crear un nuevo bucket en una región específica y preparar el alojamiento.
* **Subir archivos y respaldarlos:** Toma elementos del disco duro local y usa mecanismos del sdk para transportarlos a los buckets alojados de manera segura.
* **Listar archivos cargados:** Realiza una revisión del repositorio digital en S3 para mostrar en pantalla que todos los metadatos y archivos han sido cargados al 100%.

### 2. Proyecto de Sincronización a S3 (`s3_sync_project.ipynb`)
Desarrolla el concepto de un "mirror" o espejo, en donde un directorio en modo local y el entorno dentro de un Bucket S3 se mantienen en constante sincronización inteligente.
* **Comparar estados:** Recupera la lista de objetos en S3 para compararlos con los archivos locales, evitando transferencias duplicadas.
* **Actualizar y sincronizar contenido:** Automatiza la subida de archivos nuevos al bucket y la descarga de objetos que residen en la nube pero no en el host local.

### 3. Proyecto ETL Pipeline con S3 (`s3_etl_pipeline_project.ipynb`)
Emula de forma precisa un pequeño (pipeline) para las tres etapas de manejo de datos principales (Extracción, Transformación y Carga) haciendo un uso total de S3 para resguardos del flujo de datos en procesamiento.
* **Extraer:** Obtener y descargar sets de variables crudas desde el cloud directamente a las memorias volátiles controlando eficientemente el código y su procesamiento en entorno Python.
* **Transformar:** Modificar estructuralmente la representación original (limpiando, filtrando e inter-cruzando información).
* **Cargar:** Subir al S3 el objeto pulido listo para la distribución de datos de consulta.

### 4. Proyecto de Auditoría en EC2 (`ec2_describe_project.ipynb`)
Un proyecto volcado enteramente al monitoreo general de cómputo en AWS (EC2), orientado al ahorro general y la consulta administrativa.
* **Conexión con recursos de EC2:** Generar peticiones y filtros hacia el SDK para que nos reporte el estado de los recursos de cómputo generados en una cuenta en particular de Amazon.
* **Listar y describir instancias:** Imprimir información de alto nivel como el estado (running/stopped), id, claves y métricas básicas de diferentes instancias bajo nuestra jurisdicción.

### 5. Proyecto de Limpieza en S3 (`s3_cleaner_project.ipynb`)
Script enfocado en la eliminación de objetos masiva y la auditoría constante para librar espacio inactivo, identificando archivos obsoletos en nuestros buckets S3, apoyando al mantenimiento y prevención de costos innecesarios en la nube.
* **Análisis y enumeración de objetos en bucket:** Lista el almacenamiento disponible para ubicar elementos viejos analizando de forma temporal sus etiquetas de último acceso/modificación.
* **Eliminar archivos en lote:** Elimina de forma eficiente (uno a uno o todos en bloque) los datos y elementos hallados.
* **Borrar bucket S3 vacíos:** Permite desmontar la infraestructura quitando buckets enteros si están vacíos o no se ocupan más.

> **Importante sobre este script (Pipeline de Limpieza)**  
> Cabe destacar que, aunque este script es excelente para la **automatización personalizada** utilizando código Python en tareas de limpieza de objetos, **AWS ofrece S3 Lifecycle Policies** de forma totalmente nativa.
> 
> * ¿Cuándo usar este script?: Es sumamente útil cuando se necesita una lógica compleja para disparar eliminaciones (por ejemplo, borrar solo si se determina que un backup en otro lado fue exitoso, o si se desea enviar un conjunto de métricas y un reporte por correo antes de ejecutar una eliminación masiva basándose en un registro en la base de datos).
> * ¿Cuándo utilizar S3 Lifecycle Policies?: Estas políticas nativas de AWS son mucho mejores, de gran escalabilidad y preferibles si el objetivo son los ahorros de costos automáticos a gran escala, donde AWS se encargará detrás de la plataforma de limpiar automáticamente tus archivos pasados ciertos días definidos por regla, o reasignarlos a capas más económicas de forma permanente.

---

## Resultados y Conclusión

**Resultados**
A lo largo de estos proyectos realizados desde notebooks de Python, se logró confirmar de primera mano cómo aprovechar las herramientas de desarrollo para comunicarse directamente con AWS. Desde operaciones simples y habituales en S3, tales como respaldos, limpieza selectiva y transferencias ETL, hasta la descripción e inventariado visual de componentes y máquinas virtuales en EC2 sin utilizar clics de ratón ni interfaces basadas en portales y navegadores web (Consola de AWS).

**Conclusión**
La integración de las funcionalidades de AWS en rutinas mediante Python, empoderadas por el uso del marco de Boto3, incrementa enormemente los beneficios logísticos hacia flujos de trabajo repetitivos en nuestra cuenta de AWS. El poder escalar programáticamente estas necesidades de manejo y el hecho de aplicar la mentalidad de 'Infraestructura como código' da como resultado soluciones inmediatas, confiables y con posibilidades ilimitadas para adaptarlas mediante las herramientas interconectadas a casos de uso que demanda la era digital de forma moderna y eficiente.