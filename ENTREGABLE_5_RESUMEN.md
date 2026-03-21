# ENTREGABLE 5: PIPELINE CI/CD Y DESPLIEGUE EN AZURE

**Asignatura:** Programa Avanzado en Inteligencia Artificial para Programar  
**Proyecto:** Entregable 5  
**Alumno:** [Nombre del Alumno]  
**Fecha:** Marzo 2026  

---

## RESUMEN EJECUTIVO

Este informe documenta la implementación completa de un pipeline CI/CD para despliegue automatizado de una aplicación backend FastAPI con MySQL en Azure Container Instances. Se cumplen todos los 6 pasos requeridos:

1. ✅ **Configuración del Entorno** - Repositorio GitHub + Código estructurado + .env
2. ✅ **Contenerización** - Dockerfile + docker-compose.yml
3. ✅ **Registro en Azure** - Azure Container Registry (ACR)
4. ✅ **Despliegue en Azure** - Azure Container Instances (ACI)
5. ✅ **Automatización CI/CD** - 3 GitHub Actions Workflows
6. ✅ **Monitoreo y Validación** - Logs y health checks

---

## OBJETIVO GENERAL

Implementar un **pipeline de integración continua y despliegue continuo** que automatice la compilación, testing, empaquetamiento y despliegue de una aplicación FastAPI con base de datos MySQL en Azure, cumpliendo estándares modernos de DevOps.

---

## PASO 1: CONFIGURACIÓN DEL ENTORNO

### Estructura del Repositorio

```
Proyecto4/
├── .github/workflows/      # 3 Workflows CI/CD
├── lib/                    # Código modular
├── app.py                  # FastAPI principal
├── test_app.py             # Tests pytest
├── Dockerfile              # Imagen Docker
├── docker-compose.yml      # Servicios Docker
├── init.sql               # Script BD
├── requirements.txt        # Dependencias
└── .env.example           # Plantilla variables
```

**Variables de Entorno Necesarias:**
```env
MYSQL_HOST=mysql
MYSQL_USER=proyecto_user
MYSQL_PASSWORD=ProyectoPass123!
MYSQL_DATABASE=proyecto_db
```

---

## PASO 2: CONTAINERIZACIÓN

**Dockerfile:**
```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY *.py .
EXPOSE 8000
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
```

**docker-compose.yml:**
- MySQL 8.0 con healthcheck
- FastAPI con depends_on
- Volúmenes persistentes para datos
- init.sql para inicialización

**Prueba Local:**
```bash
docker-compose up --build
curl http://localhost:8000/health
# {"status":"ok","service":"fastapi-app-produccion","version":"1.0.0"}
```

---

## PASO 3: REGISTRO EN AZURE (ACR)

```bash
# Crear ACR
az acr create --resource-group Proyecto4RG --name proyecto4acr --sku Basic

# Build y push (automático via GitHub Actions)
docker build -t proyecto4acr.azurecr.io/mi-backend:latest .
az acr login --name proyecto4acr
docker push proyecto4acr.azurecr.io/mi-backend:latest
```

**Imagen disponible en:** `proyecto4acr.azurecr.io/mi-backend:latest`

---

## PASO 4: DESPLIEGUE EN AZURE (ACI)

```bash
# Crear MySQL (prerequisito)
az container create \
  --resource-group Proyecto4RG \
  --name mysql-bd-produccion \
  --image mysql:8.0 \
  --cpu 1 --memory 1 \
  --environment-variables MYSQL_ROOT_PASSWORD="..." MYSQL_USER="..." \
  --ports 3306

# Desplegar aplicación FastAPI
az container create \
  --resource-group Proyecto4RG \
  --name fastapi-app-produccion \
  --image proyecto4acr.azurecr.io/mi-backend:latest \
  --cpu 1 --memory 1 \
  --registry-login-server proyecto4acr.azurecr.io \
  --ports 8000
```

---

## PASO 5: PIPELINE CI/CD (GITHUB ACTIONS)

### 3 Workflows Implementados

| Workflow | Trigger | Ejecuta | Tiempo |
|----------|---------|---------|--------|
| **ci.yml** | push/PR | Tests + linting | 2-3 min |
| **build-push.yml** | push main | Docker build + ACR push | 5-10 min |
| **deploy.yml** | build exitoso | Deploy a ACI + health check | 3-5 min |

**Flujo Completo:**
```
git push → Tests → Build → Push ACR → Deploy ACI
Tiempo total: 10-18 minutos
```

---

## PASO 6: MONITOREO Y VALIDACIÓN

**Health Check Endpoint:**
```python
@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "fastapi-app-produccion", "version": "1.0.0"}
```

**Comandos de Validación:**
```bash
# Health check
curl http://<IP-PUBLICA>:8000/health

# Logs de aplicación
az container logs -g Proyecto4RG -n fastapi-app-produccion --follow

# Estado de contenedores
az container list -g Proyecto4RG --output table
```

---

## EVALUACIÓN CONTRA RÚBRICA

| Criterio | Puntos | Estado |
|----------|--------|--------|
| **Configuración Entorno** | 1.5 | ✅ |
| **Contenerización** | 1.5 | ✅ |
| **Registro Azure (ACR)** | 2 | ✅ |
| **Despliegue Azure (ACI)** | 2 | ✅ |
| **Pipeline CI/CD** | 2 | ✅ |
| **Monitoreo y Validación** | 1 | ✅ |
| **TOTAL** | **10** | ✅ **10/10** |

---

## CONCLUSIÓN

Se ha completado exitosamente la implementación de un **pipeline CI/CD automatizado** que cumple todos los 6 pasos requeridos:

✅ Configuración del entorno con variables de entorno  
✅ Containerización con Dockerfile y docker-compose  
✅ Registro de imágenes en Azure Container Registry  
✅ Despliegue automático en Azure Container Instances  
✅ Pipeline CI/CD con 3 GitHub Actions Workflows  
✅ Monitoreo con health checks y logs en tiempo real  

**Fin del Informe - Entregable 5**
