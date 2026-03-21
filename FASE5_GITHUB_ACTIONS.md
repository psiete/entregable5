# Fase 5: Automatización CI/CD - Configuración

Este documento guía la configuración de los workflows de GitHub Actions para CI/CD automatizado.

---

## Paso 5.1: Configurar Secrets en GitHub

Los workflows necesitan acceso a credenciales de Azure. Deben configurarse como GitHub Secrets.

### 1. Obtener credenciales necesarias

**AZURE_SUBSCRIPTION_ID:**
```bash
az account show --query id -o tsv
```

**AZURE_RESOURCE_GROUP:**
```bash
echo "Proyecto4RG"  # O el nombre de tu resource group
```

**AZURE_REGISTRY_LOGIN_SERVER:**
```bash
az acr show --resource-group Proyecto4RG --name proyecto4acr --query loginServer -o tsv
```

**AZURE_REGISTRY_USERNAME y AZURE_REGISTRY_PASSWORD:**
```bash
az acr credential show --resource-group Proyecto4RG --name proyecto4acr
```

**MYSQL_USER, MYSQL_PASSWORD, MYSQL_DATABASE:**
```bash
# Usar los valores definidos en el paso 4.1 de FASE4_DESPLIEGUE_MANUAL.md
MYSQL_USER="proyecto_user"
MYSQL_PASSWORD="TuPassword123!Segura"
MYSQL_DATABASE="proyecto_db"
```

**AZURE_CREDENTIALS (para Azure Login):**
```bash
# Crear un Service Principal
az ad sp create-for-rbac \
  --name "GithubActionsDeployer" \
  --role contributor \
  --scopes /subscriptions/$(az account show --query id -o tsv) \
  --json-auth
```

El comando anterior generará un JSON como:
```json
{
  "clientId": "...",
  "clientSecret": "...",
  "subscriptionId": "...",
  "tenantId": "..."
}
```

Copiar este JSON completo.

### 2. Añadir Secrets en GitHub

1. Ir a tu repositorio en GitHub
2. Settings → Secrets and variables → Actions
3. Crear un nuevo secret para cada valor:

| Secret Name | Valor |
|---|---|
| `AZURE_SUBSCRIPTION_ID` | ID de suscripción |
| `AZURE_RESOURCE_GROUP` | `Proyecto4RG` |
| `AZURE_REGISTRY_LOGIN_SERVER` | `proyecto4acr.azurecr.io` |
| `AZURE_REGISTRY_USERNAME` | Username de ACR |
| `AZURE_REGISTRY_PASSWORD` | Password de ACR |
| `AZURE_REGISTRY_NAME` | `proyecto4acr` |
| `AZURE_CREDENTIALS` | JSON completo del Service Principal |
| `MYSQL_USER` | `proyecto_user` |
| `MYSQL_PASSWORD` | Tu contraseña fuerte |
| `MYSQL_DATABASE` | `proyecto_db` |

### 3. Verificación

Para verificar que los secrets están correctamente configurados:
1. Hacer un `git push` a una rama (main o develop)
2. Ir a la pestaña "Actions" del repositorio
3. El workflow "Build and Push to ACR" debería ejecutarse automáticamente

---

## Paso 5.2: Cómo funcionan los Workflows

El proyecto configura 3 workflows separados que trabajan en conjunto:

### 1️⃣ Workflow: CI Tests (`ci.yml`)

**Triggers:** Se ejecuta automáticamente en:
- Push a `main` o `develop`
- Pull Requests a `main` o `develop`

**Pasos:**
1. Checkout del código
2. Setup de Python 3.11
3. Instalación de dependencias (pip install -r requirements.txt)
4. Ejecución de tests (pytest test_app.py -v)
5. Linting básico (black, flake8) - sin bloquear

**Proposito:** Validar que el código cumple los tests y sigue estándares de formato

**Secrets requeridos:** Ninguno

**Salida:** ✅ o ❌ en el commit/PR indicando si los tests pasaron

---

### 2️⃣ Workflow: Build and Push to ACR (`build-push.yml`)

**Triggers:** Se ejecuta automáticamente cuando hay un `push` a las ramas `main` o `develop`

**Pasos:**
1. Checkout del código
2. Setup de Python para ejecutar tests previos
3. Instalación de dependencias
4. Ejecución de tests (pytest)
5. Login en Docker (ACR)
6. Setup Docker Buildx para optimizar el build
7. Build de la imagen Docker (solo localmente en PRs)
8. Push de la imagen a ACR con dos tags:
   - Tag con SHA del commit: `mi-backend:<git-sha>`
   - Tag `latest`: `mi-backend:latest`
9. **NUEVO**: Validación - Pull de la imagen desde ACR para verificar que se subió correctamente

**Proposito:** Construir y almacenar la imagen Docker en Azure Container Registry

**Secrets requeridos:**
- `AZURE_REGISTRY_LOGIN_SERVER` (e.g., `proyecto4acr.azurecr.io`)
- `AZURE_REGISTRY_USERNAME`
- `AZURE_REGISTRY_PASSWORD`

**Salida:** Imagen disponible en ACR y lista para ser desplegada

---

### 3️⃣ Workflow: Deploy to Azure Container Instances (`deploy.yml`)

**Triggers:** Se ejecuta automáticamente después de que "Build and Push to ACR" completa exitosamente en la rama `main`

**Pasos:**
1. Login en Azure
2. Búsqueda de MySQL existente (si no existe, skip del deployment)
3. Eliminación del contenedor anterior de la app (si existe)
4. Creación de nuevo contenedor de la aplicación con:
   - Imagen desde ACR: `mi-backend:latest`
   - Recursos: 1 CPU, 1 GB RAM
   - Variables de entorno de MySQL y config
   - Puerto: 8000
   - Política de reinicio: OnFailure
5. Espera de 30 segundos para que la app inicie
6. **NUEVO**: Obtención de información de despliegue (IP pública, FQDN)
7. **NUEVO**: Validación con healthcheck (`GET /health` endpoint)
8. **NUEVO**: Resumen detallado con URLs y comandos útiles

**Proposito:** Desplegar automáticamente la aplicación en Azure Container Instances

**Secrets requeridos:**
- `AZURE_CREDENTIALS` (Service Principal JSON)
- `AZURE_RESOURCE_GROUP` (e.g., `Proyecto4RG`)
- `AZURE_REGISTRY_LOGIN_SERVER`
- `AZURE_REGISTRY_USERNAME`
- `AZURE_REGISTRY_PASSWORD`
- `MYSQL_USER`
- `MYSQL_PASSWORD`
- `MYSQL_DATABASE`

**Salida:** Aplicación desplegada en ACI en una IP pública accesible, con resumen de URLs y comandos

---

## Pipeline Completo

```
git push a main
    ↓
1. CI Tests (ci.yml)
    - Ejecutar pytest
    - Validar formato
    ↓
2. Build and Push (build-push.yml)
    - Build imagen Docker
    - Push a ACR
    ↓
3. Deploy to ACI (deploy.yml)
    - Desplegar desde ACR a Container Instances
    - Validar healthcheck
    ↓
✅ Aplicación en producción
```

---

## Paso 5.3: Monitorear y Solucionar Problemas

### Ver logs de los workflows en GitHub

1. Ir a la pestaña **"Actions"** en GitHub
2. Seleccionar el workflow (CI, Build and Push, o Deploy)
3. Clickear en el run (ejecución) más reciente
4. Expandir cada "job" para ver los steps
5. Clickear en cada step para ver el output detallado

---

### ❌ Solucionar fallos: Workflow CI (ci.yml)

**Problema:** Tests fallan ❌

**Causas posibles y soluciones:**

| Problema | Solución |
|----------|----------|
| ImportError en las dependencias | `pip install -r requirements.txt` localmente, verificar que funciona |
| Versión de Python incompatible | Verificar que Python 3.11+ está instalado localmente |
| Tests requieren BD | Ejecutar `docker-compose up` localmente primero, luego tests |
| test_app.py no existe | Verificar que el archivo existe en la raíz del proyecto |

**Debugging local:**
```bash
# Simular exactamente lo que hace el workflow
python -m pip install --upgrade pip
pip install -r requirements.txt
python -m pytest test_app.py -v --tb=short
```

---

### ❌ Solucionar fallos: Workflow Build and Push (build-push.yml)

**Problema:** Azure Login falla ❌

**Causa:** Secret `AZURE_CREDENTIALS` no está configurado o es inválido

**Solución:**
```bash
# Regenerar el Service Principal
az ad sp create-for-rbac \
  --name "GithubActionsDeployer" \
  --role contributor \
  --scopes /subscriptions/$(az account show --query id -o tsv) \
  --json-auth

# Copiar el JSON completo al secret AZURE_CREDENTIALS en GitHub Settings → Secrets
```

---

**Problema:** Docker Login falla ❌

**Causa:** Secrets de ACR son incorrectos

**Solución:**
```bash
# Verificar que ACR existe
az acr list --output table

# Obtener credenciales correctas
az acr credential show \
  --resource-group Proyecto4RG \
  --name proyecto4acr

# Actualizar en GitHub:
# - AZURE_REGISTRY_LOGIN_SERVER: (el valor loginServer)
# - AZURE_REGISTRY_USERNAME: (el valor username)
# - AZURE_REGISTRY_PASSWORD: (el valor password)
```

---

**Problema:** Build falla con error de Dockerfile ❌

**Causa:** Dockerfile tiene sintaxis inválida

**Solución:**
```bash
# Validar Dockerfile localmente
docker build -t test-image .

# Si falla, revisar:
# - COPY commands con rutas correctas
# - Dependencias de Python en requirements.txt
# - Imagen base (FROM python:3.12-slim)
```

---

**Problema:** Image push falla, pero build pasó ✓ 

**Causa:** Falta memoria en ACR o cuenta de almacenamiento llena

**Solución:**
```bash
# Limpiar imágenes antiguas en ACR
az acr repository delete \
  --resource-group Proyecto4RG \
  --name proyecto4acr \
  --repository mi-backend

# Luego re-ejecutar el workflow
```

---

### ❌ Solucionar fallos: Workflow Deploy (deploy.yml)

**Problema:** Deployment no inicia porque MySQL no existe ⚠️

**Mensaje en logs:**
```
⚠️ Contenedor MySQL NO encontrado
📖 Instrucciones: Crear MySQL primero usando FASE4_DESPLIEGUE_MANUAL.md
```

**Solución:** 
Primero se DEBE desplegar MySQL manualmente (ver [FASE4_DESPLIEGUE_MANUAL.md](FASE4_DESPLIEGUE_MANUAL.md)), luego hacer push a main para que se ejecute el deploy workflow.

---

**Problema:** Deployment falla con error de autenticación ACR ❌

**Causa:** Credenciales de ACR incorrectas

**Solución:**
```bash
# Verificar que los secrets están correctamente en GitHub
# Ir a: Settings → Secrets and variables → Actions

# Verificar credenciales en Azure CLI
az acr credential show --resource-group Proyecto4RG --name proyecto4acr

# Actualizar los secrets si es necesario
```

---

**Problema:** Contenedor está corriendo pero `/health` endpoint devuelve 404 ❌

**Causa:** Aplicación aún no ha iniciado completamente

**Solución:**
```bash
# Ver logs del contenedor
az container logs \
  --resource-group Proyecto4RG \
  --name fastapi-app-produccion \
  --follow

# Esperar 1-2 minutos y luego intentar de nuevo
# El healthcheck en deploy workflow reintenta 10 veces con 5 segundos de espera
```

---

**Problema:** Aplicación desplegada pero no conecta a MySQL ❌

**Causa:** Variables de entorno MYSQL_* son incorrectas

**Solución:**
```bash
# Ver variables de entorno en ACI
az container show \
  --resource-group Proyecto4RG \
  --name fastapi-app-produccion \
  --query containers[0].environmentVariables

# Verificar que MYSQL_HOST contiene la IP correcta del contenedor MySQL
# Verificar que MYSQL_USER, MYSQL_PASSWORD y MYSQL_DATABASE coinciden con MySQL

# Revisar logs para error de conexión
az container logs \
  --resource-group Proyecto4RG \
  --name fastapi-app-produccion \
  | grep -i "mysql\|connection\|error"
```

---

### ✅ Verificación final: El workflow está funcionando correctamente

Después de hacer un `git push` a main, verificar:

```bash
# 1. Ver workflows ejecutándose en GitHub Actions
# (pestaña Actions en https://github.com/usuario/Proyecto4)

# 2. Obtener IP de la aplicación desplegada
APP_IP=$(az container show \
  --resource-group Proyecto4RG \
  --name fastapi-app-produccion \
  --query ipAddress.ip -o tsv)

# 3. Verificar que la aplicación responde
curl http://${APP_IP}:8000/health
# Debe retornar: {"status":"ok","service":"fastapi-app-produccion","version":"1.0.0"}

# 4. Acceder a documentación API
# Abrir en navegador: http://${APP_IP}:8000/docs

# 5. Ver logs
az container logs \
  --resource-group Proyecto4RG \
  --name fastapi-app-produccion \
  --follow
```

---

## Paso 5.4: Mantenimiento

### Rotar credenciales periódicamente:
```bash
# Rotación de ACR credentials
az acr credential rotate --resource-group Proyecto4RG --name proyecto4acr --password-name password
```

### Limpiar Azure resources si no se usan:
```bash
# Eliminar contenedor
az container delete --resource-group Proyecto4RG --name fastapi-app-produccion --yes

# Eliminar ACR (cuidado: esto borra todas las imágenes)
az acr delete --resource-group Proyecto4RG --name proyecto4acr --yes
```

---

## Notas de Seguridad

- ⚠️ Los secrets de GitHub están encriptados y no son visibles en los logs
- ⚠️ No compartir el AZURE_CREDENTIALS JSON con nadie
- ⚠️ Cambiar las contraseñas de MYSQL_USER y MYSQL_ROOT_PASSWORD después del despliegue inicial
- ✅ Los secrets expiran cuando se rota la contraseña en Azure

