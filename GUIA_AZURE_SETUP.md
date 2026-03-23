# GUÍA DE SETUP: Generación de Recursos en Azure

**Objetivo:** Configurar todos los recursos necesarios en Azure para desplegar la aplicación FastAPI con PostgreSQL.

**Tiempo estimado:** 15-20 minutos

---

## 📋 REQUISITOS PREVIOS

Antes de comenzar, verifica que tienes:

✅ **Azure CLI** instalado
```bash
# Verificar instalación
az --version

# Si no está instalado (macOS):
brew install azure-cli

# Si no está instalado (Windows/Linux):
# Descargar desde: https://docs.microsoft.com/en-us/cli/azure/install-azure-cli
```

✅ **Suscripción de Azure** activa y acceso a ella

✅ **Git** configurado con tu repositorio de Proyecto4

✅ **Docker Desktop** (para tests locales opcionales)

---

## 🔑 PASO 1: Autenticarse en Azure

```bash
# Login interactivo
az login

# Verificar que estás autenticado
az account show

# Salida esperada:
# {
#   "id": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
#   "name": "Tu Suscripción",
#   "user": {...}
# }
```

**Guardar el ID de suscripción** para usarlo más adelante:
```bash
SUBSCRIPTION_ID=$(az account show --query id -o tsv)
echo $SUBSCRIPTION_ID
```

---

## 📁 PASO 2: Crear Resource Group

Un Resource Group es un contenedor lógico para agrupar todos los recursos relacionados.

```bash
# Variables (personaliza según necesidad)
RESOURCE_GROUP="Proyecto5psiete"
LOCATION="norwayeast"  # O tu región preferida (westus, northeurope, etc.)

# Crear Resource Group
az group create \
  --name $RESOURCE_GROUP \
  --location $LOCATION

# Verificar creación
az group list --output table
```

**Salida esperada:**
```
Name             Location     Status
---------------  -----------  ---------
grupo_unir       northeurope  Succeeded
Proyecto5psiete  norwayeast   Succeeded
```

---

## 🐳 PASO 3: Crear Azure Container Registry (ACR)

Azure Container Registry es donde guardaremos la imagen Docker de la aplicación.

```bash
# Variables
ACR_NAME="proyecto5acr"
RESOURCE_GROUP="Proyecto5psiete"
SKU="Basic"  # Basic, Standard, Premium

# Crear ACR
az acr create \
  --resource-group $RESOURCE_GROUP \
  --name $ACR_NAME \
  --sku $SKU

# Verificar creación
az acr list \
  --resource-group $RESOURCE_GROUP \
  --output table
```

**Salida esperada:**
```
NAME          RESOURCE GROUP    LOCATION    SKU    LOGIN SERVER             CREATION DATE         ADMIN ENABLED
------------  ----------------  ----------  -----  -----------------------  --------------------  ---------------
proyecto5acr  Proyecto5psiete   norwayeast  Basic  proyecto5acr.azurecr.io  2026-03-23T21:08:25Z  False
```

---

## 📝 PASO 4: Obtener Credenciales de ACR

Estas credenciales se usarán para subir y descargar imágenes Docker.

```bash
# Obtener login server
ACR_LOGIN_SERVER=$(az acr show \
  --resource-group $RESOURCE_GROUP \
  --name $ACR_NAME \
  --query loginServer \
  -o tsv)
echo "ACR Login Server: $ACR_LOGIN_SERVER"
# Salida: proyecto5acr.azurecr.io

# Habilitar el admin
az acr update -n proyecto5acr --admin-enabled true

# Obtener credenciales (username y password)
az acr credential show \
  --resource-group $RESOURCE_GROUP \
  --name $ACR_NAME

# Salida esperada:
# {
#   "passwords": [
#     {
#       "name": "password",
#       "value": "FHxaWw8RwhVDx8wHNTwoG3KLrgde1iztjsGMoudCqh2QRMNJLSUVJQQJ99CCAChHRaEEqg7NAAACAZCR4rxI"
#     },
#     {
#       "name": "password2",
#       "value": "DBj3CZaxLfuHGBlTBjviNjGxbQDRBgCsGanZGC6pVpg3RxsGB1UJJQQJ99CCAChHRaEEqg7NAAACAZCR85VO"
#     }
#   ],
#   "username": "proyecto4acr"
# }
```

**⚠️ GUARDAR ESTOS VALORES:**
- `ACR_LOGIN_SERVER`: `proyecto5acr.azurecr.io`
- `ACR_USERNAME`: `proyecto5acr`
- `ACR_PASSWORD`: (primer password)

---

## 🗄️ PASO 5: Desplegar PostgreSQL en Azure Container Instances

PostgreSQL es la base de datos que usará la aplicación.

```bash
# Variables
DB_CONTAINER_NAME="postgres-bd-produccion"
DB_IMAGE="postgres:16-alpine"
DB_user="proyecto_user"
DB_PASSWORD="FHxaWw8RwhVDx8wHNTwoG3KLrgde1iztjsGMoudCqh2QRMNJLSUVJQQJ99CCAChHRaEEqg7NAAACAZCR4rxI"  # ⚠️ Cambiar a contraseña fuerte
DB_NAME="proyecto_db"
RESOURCE_GROUP="Proyecto5psiete"

# Crear contenedor PostgreSQL
az container create \
  --resource-group $RESOURCE_GROUP \
  --name $DB_CONTAINER_NAME \
  --image $DB_IMAGE \
  --cpu 1 \
  --memory 1 \
  --environment-variables \
    POSTGRES_USER=$DB_user \
    POSTGRES_PASSWORD=$DB_PASSWORD \
    POSTGRES_DB=$DB_NAME \
  --ports 5432 \
  --protocol TCP
  --os-type Linux

# Si falla, ejecutar az provider register --namespace Microsoft.ContainerInstance

# Verificar estado
az container show \
  --resource-group $RESOURCE_GROUP \
  --name $DB_CONTAINER_NAME \
  --query "instanceView.state" -o tsv
```

**Estado esperado:** `Running`

```bash
# Obtener IP de PostgreSQL (importante para la app)
DB_IP=$(az container show \
  --resource-group $RESOURCE_GROUP \
  --name $DB_CONTAINER_NAME \
  --query ipAddress.ip \
  -o tsv)
echo "PostgreSQL IP: $DB_IP"
```

---

## 🚀 PASO 6: Construir y Subir Imagen Docker a ACR

```bash
# Navegar a la raíz del proyecto
cd /Users/albertopeset/UNIR/Proyecto4

# Login en ACR
az acr login --name $ACR_NAME

# Build imagen Docker
docker build -t $ACR_LOGIN_SERVER/mi-backend:latest .

# Push a ACR
docker push $ACR_LOGIN_SERVER/mi-backend:latest

# Verificar que subió correctamente
az acr repository list \
  --name $ACR_NAME \
  --output table

# Listar tags de la imagen
az acr repository show-tags \
  --name $ACR_NAME \
  --repository mi-backend \
  --output table
```

**Salida esperada:**
- Imagen subida: `proyecto4acr.azurecr.io/mi-backend:latest`

---

## 🌐 PASO 7: Desplegar Aplicación FastAPI en Azure Container Instances

```bash
# Variables
APP_CONTAINER_NAME="fastapi-app-produccion"
APP_IMAGE="$ACR_LOGIN_SERVER/mi-backend:latest"
ACR_USERNAME="proyecto4acr"
ACR_PASSWORD="<tu-password-de-ACR>"  # Del Paso 4
RESOURCE_GROUP="Proyecto4RG"

# Variables de base de datos (desde Paso 5)
DB_IP="<IP-de-PostgreSQL>"
DB_USER="proyecto_user"
DB_PASSWORD="ProyectoPass123!Segura"
DB_NAME="proyecto_db"

# Crear contenedor de la aplicación
az container create \
  --resource-group $RESOURCE_GROUP \
  --name $APP_CONTAINER_NAME \
  --image $APP_IMAGE \
  --cpu 1 \
  --memory 1 \
  --registry-login-server $ACR_LOGIN_SERVER \
  --registry-username $ACR_USERNAME \
  --registry-password $ACR_PASSWORD \
  --environment-variables \
    POSTGRES_HOST=$DB_IP \
    POSTGRES_PORT="5432" \
    POSTGRES_USER=$DB_USER \
    POSTGRES_PASSWORD=$DB_PASSWORD \
    POSTGRES_DB=$DB_NAME \
  --ports 8000 \
  --protocol TCP \
  --restart-policy OnFailure

# Verificar estado
az container show \
  --resource-group $RESOURCE_GROUP \
  --name $APP_CONTAINER_NAME \
  --query "instanceView.state" -o tsv

# Esperar 30 segundos a que inicie la app
echo "Esperando a que la aplicación inicie..."
sleep 30
```

---

## 🌍 PASO 8: Obtener IP Pública y Validar

```bash
# Obtener IP pública de la aplicación
APP_IP=$(az container show \
  --resource-group $RESOURCE_GROUP \
  --name $APP_CONTAINER_NAME \
  --query ipAddress.ip \
  -o tsv)

echo "✅ Aplicación desplegada en: http://$APP_IP:8000"

# Obtener FQDN (dominio completo)
APP_FQDN=$(az container show \
  --resource-group $RESOURCE_GROUP \
  --name $APP_CONTAINER_NAME \
  --query ipAddress.fqdn \
  -o tsv)

echo "🔗 FQDN: $APP_FQDN"
```

---

## ✅ PASO 9: Verificar que Funciona

```bash
# Health Check
curl http://$APP_IP:8000/health

# Salida esperada:
# {"status":"ok","service":"fastapi-app-produccion","version":"1.0.0"}

# Ver logs de la aplicación
az container logs \
  --resource-group $RESOURCE_GROUP \
  --name $APP_CONTAINER_NAME \
  --follow

# Ver logs de PostgreSQL
az container logs \
  --resource-group $RESOURCE_GROUP \
  --name $DB_CONTAINER_NAME \
  --follow

# Listar todos los contenedores
az container list \
  --resource-group $RESOURCE_GROUP \
  --output table
```

---

## 🔐 PASO 10: Configurar GitHub Secrets

Para que los workflows de GitHub Actions funcionen automáticamente, necesitan acceso a las credenciales de Azure.

### 10.1 Crear Service Principal

```bash
# Crear un Service Principal con rol de Contributor
az ad sp create-for-rbac \
  --name "GithubActionsDeployer" \
  --role contributor \
  --scopes /subscriptions/$SUBSCRIPTION_ID \
  --json-auth

# Salida esperada (GUARDAR TODO):
# {
#   "clientId": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
#   "clientSecret": "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx~xxx",
#   "subscriptionId": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
#   "tenantId": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
# }
```

### 10.2 Añadir Secrets en GitHub

1. Ir a tu repositorio en GitHub
2. **Settings** → **Secrets and variables** → **Actions**
3. Crear los siguientes secrets:

| Secret Name | Valor |
|---|---|
| `AZURE_SUBSCRIPTION_ID` | (del Paso 1) |
| `AZURE_RESOURCE_GROUP` | `Proyecto4RG` |
| `AZURE_REGISTRY_LOGIN_SERVER` | `proyecto4acr.azurecr.io` |
| `AZURE_REGISTRY_USERNAME` | `proyecto4acr` |
| `AZURE_REGISTRY_PASSWORD` | (del Paso 4) |
| `AZURE_REGISTRY_NAME` | `proyecto4acr` |
| `AZURE_CREDENTIALS` | JSON completo del Service Principal (Paso 10.1) |
| `POSTGRES_USER` | `proyecto_user` |
| `POSTGRES_PASSWORD` | `ProyectoPass123!Segura` |
| `POSTGRES_DB` | `proyecto_db` |

---

## 🧪 PASO 11: Test del Pipeline CI/CD

```bash
# Hacer un push a main para activar los workflows
git add .
git commit -m "test: trigger CI/CD pipeline"
git push origin main

# Ir a GitHub Actions y verificar que:
# 1. ✅ ci.yml ejecuta tests
# 2. ✅ build-push.yml construye y sube imagen
# 3. ✅ deploy.yml despliega en ACI
```

---

## 📊 Resumen de Recursos Creados

```bash
# Ver todos los recursos creados
az resource list \
  --resource-group Proyecto4RG \
  --output table

# Ver estado de contenedores
az container list \
  --resource-group Proyecto4RG \
  --output table
```

**Recursos esperados:**
- ✅ Azure Container Registry (ACR)
- ✅ 2 Container Instances (PostgreSQL + FastAPI)
- ✅ Resource Group

---

## ❌ Troubleshooting

### ❌ "ERROR: Subscription not found"
```bash
# Verificar que estás autenticado
az logout
az login
az account show
```

### ❌ "ERROR: Image not found in registry"
```bash
# Verificar que la imagen se subió correctamente
az acr repository list --name proyecto4acr
```

### ❌ "Container is in Failed state"
```bash
# Ver logs de error
az container logs \
  --resource-group Proyecto4RG \
  --name fastapi-app-produccion
```

### ❌ "Connection refused between app and database"
```bash
# Verificar que PostgreSQL está corriendo
az container show \
  --resource-group Proyecto4RG \
  --name postgres-bd-produccion \
  --query "instanceView.state"

# Verificar variables de entorno de la app
az container show \
  --resource-group Proyecto4RG \
  --name fastapi-app-produccion \
  --query containers[0].environmentVariables
```

---

## 🧹 Limpiar Recursos (Opcional)

```bash
# Eliminar todo el Resource Group
az group delete \
  --name Proyecto4RG \
  --yes

# O eliminar recursos individuales:
az container delete \
  --resource-group Proyecto4RG \
  --name fastapi-app-produccion \
  --yes

az container delete \
  --resource-group Proyecto4RG \
  --name postgres-bd-produccion \
  --yes

az acr delete \
  --resource-group Proyecto4RG \
  --name proyecto4acr \
  --yes
```

---

## 📚 Comandos Útiles de Referencia

```bash
# Ver todas las ubicaciones disponibles
az account list-locations --output table

# Ver cuota de uso actual
az account get-access-token

# Monitorear contenedor en tiempo real
watch -n 5 'az container show \
  --resource-group Proyecto4RG \
  --name fastapi-app-produccion \
  --query "instanceView.state"'

# Conectar a PostgreSQL desde local (si necesitas)
psql -h $DB_IP -U proyecto_user -d proyecto_db
```

---

## ✅ Checklist Final

- [ ] Azure CLI instalado y autenticado
- [ ] Resource Group creado
- [ ] ACR creado y credenciales obtenidas
- [ ] PostgreSQL desplegado en ACI
- [ ] Imagen Docker subida a ACR
- [ ] Aplicación FastAPI desplegada en ACI
- [ ] Health check responde correctamente
- [ ] Service Principal creado
- [ ] GitHub Secrets configurados
- [ ] Workflow CI/CD ejecutado exitosamente
- [ ] Aplicación accesible desde IP pública

---

**¡Listo!** 🎉 Tu infraestructura en Azure está completamente configurada y lista para despliegue automatizado.

Para más detalles técnicos, ver [FASE5_GITHUB_ACTIONS.md](FASE5_GITHUB_ACTIONS.md) y [ENTREGABLE_5_RESUMEN.md](ENTREGABLE_5_RESUMEN.md).
