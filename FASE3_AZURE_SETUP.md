# Fase 3: Preparación para Azure

Este documento guía los pasos necesarios para configurar la infraestructura en Azure.

## Paso 3.1: Crear Azure Container Registry (ACR)

### Prerequisitos
- Tener una cuenta Azure activa
- Azure CLI instalado (`az cli`)
- Estar autenticado en Azure (`az login`)
- Un Resource Group existente en Azure

### Pasos

1. **Definir variables locales:**
```bash
RESOURCE_GROUP="Proyecto4RG"  # Cambiar según tu RG
ACR_NAME="proyecto4acr"        # Nombre único (solo minúsculas, sin guiones)
REGION="eastus"                # Cambiar según tu región
```

2. **Crear el ACR:**
```bash
az acr create \
  --resource-group $RESOURCE_GROUP \
  --name $ACR_NAME \
  --sku Basic \
  --region $REGION
```

3. **Obtener credenciales ACR:**
```bash
az acr credential show \
  --resource-group $RESOURCE_GROUP \
  --name $ACR_NAME
```

Guardar los valores:
- `username`: Usar en GitHub Secrets como `AZURE_REGISTRY_USERNAME`
- `password`: Usar en GitHub Secrets como `AZURE_REGISTRY_PASSWORD`
- `loginServer`: Usar en GitHub Secrets como `AZURE_REGISTRY_LOGIN_SERVER`

---

## Paso 3.2: Configurar Secrets en GitHub

1. Ir a tu repositorio en GitHub
2. Settings → Secrets and variables → Actions
3. Crear los siguientes secrets:
   - `AZURE_REGISTRY_LOGIN_SERVER`: `<proyecto4acr>.azurecr.io`
   - `AZURE_REGISTRY_USERNAME`: `<username obtenido anteriormente>`
   - `AZURE_REGISTRY_PASSWORD`: `<password obtenido anteriormente>`
   - `AZURE_SUBSCRIPTION_ID`: ID de tu suscripción Azure (obtenible con `az account show --query id`)
   - `AZURE_RESOURCE_GROUP`: `Proyecto4RG` (nombre del resource group)

---

## Paso 3.3: Verificación

Verificar que el ACR existe:
```bash
az acr show \
  --resource-group $RESOURCE_GROUP \
  --name $ACR_NAME \
  --query loginServer -o tsv
```

Debería devolver algo como: `proyecto4acr.azurecr.io`

---

## Notas

- El SKU "Basic" es suficiente para desarrollo. Para producción, considerar "Standard" o "Premium"
- Los secrets en GitHub tienen un tiempo de vida; asegurarse de rotarlos periodicamente
- El nombre del ACR debe ser único en Azure (es recomendable incluir números o sufijos únicos)

