# Proyecto 4 - Entregable 5: CI/CD y Despliegue en Azure

Implementación completa de **Integración Continua (CI) y Despliegue Continuo (CD)** para una aplicación FastAPI con base de datos MySQL, contenerizada con Docker y desplegada en Azure Container Instances (ACI).

## 🎯 Objetivos Alcanzados

- ✅ **Configuración de Entorno**: Estructura de código + variables de entorno
- ✅ **Contenerización**: Dockerfile para FastAPI + docker-compose para desarrollo local
- ✅ **Registro en Azure**: Azure Container Registry (ACR) para almacenar imágenes
- ✅ **Despliegue en Azure**: Automatización con GitHub Actions → ACI
- ✅ **Pipeline CI/CD**: Tests automáticos, build, push y despliegue
- ✅ **Monitoreo**: Logs, health checks y validación de funcionamiento



## 📦 Requisitos Previos

### Software Local
- **Docker Desktop** 20.10+ ([Descargar](https://www.docker.com/products/docker-desktop))
- **Docker Compose** 1.29+ (incluido con Docker Desktop)
- **Git** 2.30+
- **Azure CLI** (`az` command) ([Descargar](https://docs.microsoft.com/en-us/cli/azure/install-azure-cli))
- **Python** 3.11+ (opcional, para tests locales)

### Requisitos Azure
- Cuenta Azure **activa**
- **Suscripción** con acceso a:
  - Azure Container Registry (ACR)
  - Azure Container Instances (ACI)
- **Resource Group** creado (e.g., `Proyecto4RG`)
- **Autenticación** con `az login`

### Requisitos GitHub
- **Repositorio** con este código
- Acceso a **Settings → Secrets and variables → Actions**



## 🚀 Inicio Rápido (Desarrollo Local)

### 1. Clonar y Configurar
```bash
git clone <tu-repo-url>
cd Proyecto4
cp .env.example .env  # (ya existe .env configurado)
```

### 2. Ejecutar con Docker Compose
```bash
# Build e iniciar contenedores (app + MySQL)
docker-compose up --build

# La aplicación estará en: http://localhost:8000
# Documentación interactiva: http://localhost:8000/docs
```

### 3. Pruebas
```bash
# Dentro del contenedor, o localmente si Python está instalado
python -m pytest test_app.py -v

# En navegador
curl http://localhost:8000/
```

### 4. Parar Servicios
```bash
docker-compose down
docker-compose down -v  # También elimina volúmenes (datos BD)
```

---

## 📋 Fases de Implementación

Este proyecto sigue un plan estructurado en **6 fases**:

| Fase | Descripción | Estado | Documentación |
|------|-------------|--------|---------------|
| **1** | Sincronización de código (FastAPI ↔ Dockerfile) | ✅ COMPLETADO | - |
| **2** | Docker Compose + variables de entorno | ✅ COMPLETADO | - |
| **3** | Preparación de Azure (ACR) | 📖 Guía | [FASE3_AZURE_SETUP.md](FASE3_AZURE_SETUP.md) |
| **4** | Despliegue manual en ACI | 📖 Guía | [FASE4_DESPLIEGUE_MANUAL.md](FASE4_DESPLIEGUE_MANUAL.md) |
| **5** | GitHub Actions (CI/CD) | ✅ Workflows listos | [FASE5_GITHUB_ACTIONS.md](FASE5_GITHUB_ACTIONS.md) |
| **6** | Monitoreo y validación | 📖 Guía | [FASE6_MONITOREO.md](FASE6_MONITOREO.md) |

---

## 📖 Guías por Fase

### 🔴 **REQUERIDA ACCIÓN MANUAL - Fase 3: Preparación de Azure**

Antes de poder desplegar en Azure, necesitas:

1. **Crear Azure Container Registry (ACR)**
   ```bash
   az acr create --resource-group Proyecto4RG --name proyecto4acr --sku Basic
   ```

2. **Obtener credenciales ACR e instancia de Service Principal**
   - Ver detalles completos en: **[FASE3_AZURE_SETUP.md](FASE3_AZURE_SETUP.md)**

3. **Configurar Secrets en GitHub** (9 valores)
   - Acceder a Settings → Secrets and variables → Actions
   - Crear secrets: `AZURE_REGISTRY_*`, `AZURE_CREDENTIALS`, `MYSQL_*`, etc.

### 🔴 **REQUERIDA ACCIÓN MANUAL - Fase 4: Despliegue Inicial**

Una vez configurado ACR:

1. **Desplegar Base de Datos MySQL en ACI**
   ```bash
   # Ver FASE4_DESPLIEGUE_MANUAL.md para comando completo
   az container create ... (contiene las variables correctas)
   ```

2. **Build, Push y Desplegar Aplicación**
   - Push de imagen a ACR
   - Despliegue del contenedor en ACI
   - Obtener IP pública

3. **Validar Acceso**
   ```bash
   curl http://<APP_IP>:8000/
   ```

**Guía completa:** [FASE4_DESPLIEGUE_MANUAL.md](FASE4_DESPLIEGUE_MANUAL.md)

### ✅ **Fase 5: GitHub Actions (AUTOMÁTICO después de Fase 3)**

Una vez configurados los Secrets de GitHub, el pipeline es **completamente automático**:

```
git push → GitHub Actions (Build & Push) → ACR 
                                              ↓
                                    Deploy to ACI
```

**Workflows incluidos:**
- `.github/workflows/build-push.yml` → Tests + Build + Push a ACR
- `.github/workflows/deploy.yml` → Deploy automático a ACI

**Configuración:** [FASE5_GITHUB_ACTIONS.md](FASE5_GITHUB_ACTIONS.md)

### 📊 **Fase 6: Monitoreo y Validación**

Una vez desplegado, monitorear con:

```bash
# Ver logs
az container logs -g Proyecto4RG -n fastapi-app-produccion --follow

# Test de conectividad
curl http://<APP_IP>:8000/docs

# Health check
curl http://<APP_IP>:8000/
```

**Guía completa:** [FASE6_MONITOREO.md](FASE6_MONITOREO.md)



## 📁 Estructura del Proyecto

```
Proyecto4/
├── app.py                        # Aplicación FastAPI
├── test_app.py                   # Tests con pytest
├── requirements.txt              # Dependencias Python
├── Dockerfile                    # Imagen Docker (FastAPI + uvicorn)
├── docker-compose.yml            # Orquestación local (app + mysql)
├── init.sql                      # Script de inicialización BD
│
├── .env.example                  # Plantilla de variables
├── .env                          # Config local (PROTEGIDO en .gitignore)
├── .gitignore                    # Archivos a ignorar en git
│
├── .github/workflows/
│   ├── build-push.yml            # CI: Tests + Build + Push a ACR
│   └── deploy.yml                # CD: Deploy automático a ACI
│
├── FASE3_AZURE_SETUP.md          # Crear ACR y Service Principal
├── FASE4_DESPLIEGUE_MANUAL.md    # Desplegar MySQL y app en ACI
├── FASE5_GITHUB_ACTIONS.md       # Configurar secrets y workflows
├── FASE6_MONITOREO.md            # Logs y validación en Azure
│
└── README.md                     # Este archivo
```

---

## 🔄 Flujo Completo de CI/CD

```
DESARROLLO LOCAL                      GITHUB                     AZURE
─────────────────                   ────────                    ──────

1. git push a main  ──────────→  Actions: Build & Push
                                      ├── Tests (pytest)
                                      ├── Build (docker)
                                      └── Push → ACR

2. Build: OK  ───────────────→  Actions: Deploy
                                   ├── Obtiene IP MySQL
                                   ├── Deploy app → ACI
                                   └── Obtiene IP pública

3. ✅ App Live  ◄──────────────────────────────── http://<IP>:8000
```



## 🔗 Endpoints de la Aplicación

### GET `/`
Información general de la API

```bash
curl http://localhost:8000/
```

**Respuesta**:
```json
{
  "message": "API de gestión de tareas",
  "endpoints": {
    "GET /user-stories": "Obtener todas las historias de usuario",
    "POST /user-stories": "Crear una nueva historia de usuario",
    "GET /user-stories/{id}/tasks": "Obtener tareas de una historia",
    "POST /user-stories/{id}/generate-tasks": "Generar tareas con IA"
  }
}
```

### 📚 GET `/docs`
Documentación interactiva (Swagger UI)

```
http://localhost:8000/docs
```

### 📋 GET `/openapi.json`
Especificación OpenAPI (JSON)

```bash
curl http://localhost:8000/openapi.json | jq .
```

---

## ⚠️ Troubleshooting

### Docker Compose no inicia

```bash
# Ver logs detallados
docker-compose logs -f

# Reiniciar limpiamente
docker-compose down -v
docker-compose up --build
```

### Tests fallan

```bash
# Ejecutar tests con verbose
python -m pytest test_app.py -v --tb=short

# Dentro del contenedor
docker-compose exec app pytest test_app.py -v
```

### Acceso a Base de Datos local

```bash
# Conectarse a MySQL desde otro contenedor
docker-compose exec mysql mysql -u proyecto_user -p proyecto_db

# Contraseña: changeme123!
```

### Contenedores fallan en Azure

**Revisar:**
1. Logs de aplicación: `az container logs ... --follow`
2. Variables de entorno: `az container show ... --query containers[0].environmentVariables`
3. Estado del contenedor: `az container show ... --query containers[0].instanceView.events`

Ver [FASE6_MONITOREO.md](FASE6_MONITOREO.md) para más detalles.

---

## 📚 Documentación Completa

| Sección | Archivo |
|---------|---------|
| **Configuración ACR en Azure** | [FASE3_AZURE_SETUP.md](FASE3_AZURE_SETUP.md) |
| **Despliegue manual en ACI** | [FASE4_DESPLIEGUE_MANUAL.md](FASE4_DESPLIEGUE_MANUAL.md) |
| **GitHub Actions y Secrets** | [FASE5_GITHUB_ACTIONS.md](FASE5_GITHUB_ACTIONS.md) |
| **Monitoreo y validación** | [FASE6_MONITOREO.md](FASE6_MONITOREO.md) |

---

## 🔐 Notas de Seguridad

⚠️ **IMPORTANTE ANTES DE PRODUCCIÓN:**

1. ✅ Cambiar contraseñas de MYSQL en `.env`
2. ✅ Usar Azure Key Vault para secrets (no GitHub Secrets)
3. ✅ Rotar credenciales de ACR periódicamente
4. ✅ Habilitar SSL/TLS con Azure Front Door
5. ✅ Configurar Azure Firewall para restricción de IPs

---

## 🚀 Próximos Pasos

1. **Completar Fase 3**: Crear ACR en Azure
2. **Completar Fase 4**: Desplegar MySQL y app manualmente
3. **Configurar Fase 5**: Secrets en GitHub
4. **Monitorear Fase 6**: Validar que todo funciona

---

## 📞 Soporte

- Guías de cada fase en archivos `FASEx_*.md`
- Logs en Azure: `az container logs -g Proyecto4RG -n <container>`
- GitHub Actions: Pestaña "Actions" en el repositorio

---

**Última actualización:** 5 de marzo de 2026  
**Versión:** 1.0.0 (Entregable 5)  
**Asignatura:** Programa Avanzado en IA para Programar - UNIR
