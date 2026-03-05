# Fase 4: Despliegue Manual en Azure

Este documento guía el despliegue de la Base de Datos y la Aplicación en Azure Container Instances (ACI).

---

## Paso 4.1: Desplegar MySQL en Azure Container Instances

### 1. Definir variables
```bash
RESOURCE_GROUP="Proyecto4RG"
LOCATION="eastus"
MYSQL_CONTAINER_NAME="mysql-bd-produccion"
MYSQL_USER="proyecto_user"
MYSQL_PASSWORD="TuPassword123!Segura"  # CAMBIAR A CONTRASEÑA FUERTE
MYSQL_ROOT_PASSWORD="RootPassword123!Segura"  # CAMBIAR
MYSQL_DATABASE="proyecto_db"
```

### 2. Crear el contenedor MySQL
```bash
az container create \
  --resource-group $RESOURCE_GROUP \
  --name $MYSQL_CONTAINER_NAME \
  --image mysql:8.0 \
  --cpu 1 \
  --memory 1 \
  --environment-variables \
    MYSQL_ROOT_PASSWORD=$MYSQL_ROOT_PASSWORD \
    MYSQL_USER=$MYSQL_USER \
    MYSQL_PASSWORD=$MYSQL_PASSWORD \
    MYSQL_DATABASE=$MYSQL_DATABASE \
  --ports 3306 \
  --protocol TCP \
  --restart-policy OnFailure
```

### 3. Obtener IP privada/pública de MySQL
```bash
MYSQL_IP=$(az container show \
  --resource-group $RESOURCE_GROUP \
  --name $MYSQL_CONTAINER_NAME \
  --query ipAddress.ip -o tsv)

echo "MySQL IP: $MYSQL_IP"
echo "Esta IP será necesaria para la configuración de la aplicación"
```

### 4. Verificar que MySQL esté listo (esperar ~30 segundos)
```bash
az container logs \
  --resource-group $RESOURCE_GROUP \
  --name $MYSQL_CONTAINER_NAME | tail -20
```

---

## Paso 4.2: Build y Push de la Imagen a ACR

### 1. Definir variables
```bash
ACR_NAME="proyecto4acr"
ACR_LOGIN_SERVER="${ACR_NAME}.azurecr.io"
IMAGE_NAME="mi-backend"
IMAGE_VERSION="v1"
```

### 2. Autenticarse en ACR
```bash
az acr login --name $ACR_NAME
```

### 3. Build de la imagen
```bash
docker build -t ${ACR_LOGIN_SERVER}/${IMAGE_NAME}:${IMAGE_VERSION} .
```

### 4. Push a ACR
```bash
docker push ${ACR_LOGIN_SERVER}/${IMAGE_NAME}:${IMAGE_VERSION}
```

### 5. Verificar que la imagen está en ACR
```bash
az acr repository list --name $ACR_NAME
az acr repository show-tags --name $ACR_NAME --repository $IMAGE_NAME
```

---

## Paso 4.3: Desplegar la Aplicación en Azure Container Instances

### 1. Definir variables
```bash
RESOURCE_GROUP="Proyecto4RG"
LOCATION="eastus"
APP_CONTAINER_NAME="fastapi-app-produccion"
ACR_NAME="proyecto4acr"
ACR_LOGIN_SERVER="${ACR_NAME}.azurecr.io"
IMAGE_NAME="mi-backend"
IMAGE_VERSION="v1"
ACR_USERNAME="<username de ACR>"  # Obtenido en Fase 3
ACR_PASSWORD="<password de ACR>"   # Obtenido en Fase 3

# Variables de configuración
MYSQL_IP="<IP obtenida en paso 4.1>"
MYSQL_USER="proyecto_user"
MYSQL_PASSWORD="TuPassword123!Segura"  # Misma que BD
MYSQL_DATABASE="proyecto_db"
```

### 2. Crear el contenedor de la app
```bash
az container create \
  --resource-group $RESOURCE_GROUP \
  --name $APP_CONTAINER_NAME \
  --image ${ACR_LOGIN_SERVER}/${IMAGE_NAME}:${IMAGE_VERSION} \
  --cpu 1 \
  --memory 1 \
  --environment-variables \
    MYSQL_HOST=$MYSQL_IP \
    MYSQL_PORT="3306" \
    MYSQL_USER=$MYSQL_USER \
    MYSQL_PASSWORD=$MYSQL_PASSWORD \
    MYSQL_DATABASE=$MYSQL_DATABASE \
    APP_ENV="production" \
  --registry-login-server $ACR_LOGIN_SERVER \
  --registry-username $ACR_USERNAME \
  --registry-password $ACR_PASSWORD \
  --ports 8000 \
  --protocol TCP \
  --restart-policy OnFailure
```

### 3. Obtener IP pública de la aplicación
```bash
APP_IP=$(az container show \
  --resource-group $RESOURCE_GROUP \
  --name $APP_CONTAINER_NAME \
  --query ipAddress.ip -o tsv)

echo "Aplicación disponible en: http://${APP_IP}:8000"
echo "Documentación en: http://${APP_IP}:8000/docs"
```

### 4. Monitorear logs
```bash
az container logs \
  --resource-group $RESOURCE_GROUP \
  --name $APP_CONTAINER_NAME \
  --follow
```

---

## Paso 4.4: Validación y Pruebas

### 1. Verificar documentación de la API
```bash
curl http://${APP_IP}:8000/
```

Debería devolver:
```json
{
  "message": "API de gestión de tareas",
  "endpoints": {...}
}
```

### 2. Acceder a la documentación interactiva
Visitar: `http://${APP_IP}:8000/docs` en el navegador

---

## Troubleshooting

### La aplicación no inicia
```bash
az container logs --resource-group $RESOURCE_GROUP --name $APP_CONTAINER_NAME
```

### MySQL no es accesible desde la app
- Verificar que la IP de MySQL sea correcta
- Verificar que las credenciales (usuario/contraseña) sean idénticas

### Eliminar contenedores (si es necesario reintentar)
```bash
az container delete --resource-group $RESOURCE_GROUP --name $MYSQL_CONTAINER_NAME --yes
az container delete --resource-group $RESOURCE_GROUP --name $APP_CONTAINER_NAME --yes
```

