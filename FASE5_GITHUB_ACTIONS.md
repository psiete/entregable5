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

### Workflow: Build and Push to ACR (`build-push.yml`)

**Triggers:** Se ejecuta automáticamente cuando hay un `push` a las ramas `main` o `develop`

**Pasos:**
1. Checkout del código
2. Setup de Python para ejecutar tests
3. Instalación de dependencias
4. Ejecución de tests (pytest)
5. Login en Azure y ACR
6. Build de la imagen Docker
7. Push de la imagen a ACR con dos tags:
   - Un tag con el SHA del commit: `mi-backend:<sha>`
   - Un tag `latest`: `mi-backend:latest`

**Salida:** La imagen está disponible en ACR y lista para ser desplegada

---

### Workflow: Deploy to Azure Container Instances (`deploy.yml`)

**Triggers:** Se ejecuta automáticamente después de que "Build and Push to ACR" se completa exitosamente en la rama `main`

**Pasos:**
1. Login en Azure
2. Obtener la IP de MySQL (si el contenedor ya existe)
3. Eliminar el contenedor anterior de la app (si existe)
4. Crear un nuevo contenedor con la última imagen de ACR
5. Esperar a que el contenedor esté listo
6. Obtener la IP pública del nuevo contenedor
7. Mostrar la URL donde acceder a la aplicación

**Salida:** La aplicación está desplegada y accesible en una URL pública

---

## Paso 5.3: Monitorear Execuciones

### Ver logs de los workflows:
1. Ir a la pestaña "Actions" en GitHub
2. Seleccionar el workflow (Build and Push o Deploy)
3. Expandir el job para ver los pasos
4. Clicking en cada step para ver el output detallado

### Solucionar fallos:

**¿El workflow de build falló?**
- Revisar que los secrets AZURE_REGISTRY_* estén correctamente configurados
- Verificar que `pip install` no falla (revisar requirements.txt)
- Confirmar que el Dockerfile es válido

**¿El workflow de deploy falló?**
- Verificar que el contenedor MySQL exists (Paso 4.1 debe completarse manualmente primero)
- Revisar que todos los secrets MYSQL_* estén configurados
- Comprobar que las credenciales de ACR son correctas

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

