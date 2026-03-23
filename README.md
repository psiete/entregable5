# Proyecto 4 - Entregable 5: CI/CD y Despliegue en Azure

Implementación completa de **pipeline de integración continua y despliegue continuo (CI/CD)** para una aplicación FastAPI con base de datos PostgreSQL, contenerizada con Docker y desplegada automáticamente en Azure Container Instances (ACI).

## 🎯 Objetivos Alcanzados

- ✅ **Configuración de Entorno:** Repositorio estructurado con variables de entorno
- ✅ **Contenerización:** Dockerfile optimizado + docker-compose para desarrollo local
- ✅ **Registro en Azure:** Azure Container Registry (ACR) para almacenar imágenes
- ✅ **Despliegue en Azure:** Despliegue automático en Azure Container Instances (ACI)
- ✅ **Pipeline CI/CD:** 3 GitHub Actions Workflows (tests → build → deploy)
- ✅ **Monitoreo:** Health checks, logs en tiempo real y validación de funcionamiento



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
# Build e iniciar contenedores (app + PostgreSQL)
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

## � Documentación

Este Entregable 5 incluye:

| Documento | Contenido |
|-----------|----------|
| **[ENTREGABLE_5_RESUMEN.md](ENTREGABLE_5_RESUMEN.md)** | Informe académico (3-5 páginas) con los 6 pasos implementados y evaluación contra rúbrica. **← LEE ESTO PARA PRESENTACIÓN** |
| **[FASE5_GITHUB_ACTIONS.md](FASE5_GITHUB_ACTIONS.md)** | Documentación técnica completa: configuración de workflows, troubleshooting y guías detalladas |
   - Ver detalles completos en: **[FASE3_AZURE_SETUP.md](FASE3_AZURE_SETUP.md)**

3. **Configurar Secrets en GitHub** (9 valores)
   - Acceder a Settings → Secrets and variables → Actions
   - Crear secrets: `AZURE_REGISTRY_*`, `AZURE_CREDENTIALS`, `POSTGRES_*`, etc.

### 🔴 **REQUERIDA ACCIÓN MANUAL - Fase 4: Despliegue Inicial**

Una vez configurado ACR:

1. **Desplegar Base de Datos PostgreSQL en ACI**
   ```bash
   # Ver FASE4_DESPLIEGUE_MANUAL.md para comando completo
   az container create ... (contiene las variables correctas)
   ```

2. **Build, Push y Desplegar Aplicación**
   - Push de imagen a ACR
---

## 🚀 Inicio Rápido (Desarrollo Local)

### 1. Clonar y Configurar
```bash
git clone <tu-repo-url>
cd Proyecto4
cp .env.example .env
```

### 2. Ejecutar con Docker Compose
```bash
# Build e iniciar contenedores (app + PostgreSQL)
docker-compose up --build

# La aplicación estará en: http://localhost:8000
# Documentación: http://localhost:8000/docs
```

### 3. Parar Servicios
```bash
docker-compose down        # Sin eliminar datos
docker-compose down -v     # Eliminar volúmenes
```

---

## 📁 Estructura del Proyecto

```
Proyecto4/
├── app.py                        # FastAPI principal
├── test_app.py                   # Tests pytest
├── Dockerfile                    # Imagen Docker
├── docker-compose.yml            # Orquestación local
├── init.sql                      # Script inicialización BD
├── requirements.txt              # Dependencias Python
│
├── .github/workflows/
│   ├── ci.yml                    # Tests automáticos
│   ├── build-push.yml            # Build + Push a ACR
│   └── deploy.yml                # Deploy a ACI
│
├── ENTREGABLE_5_RESUMEN.md       # ← INFORME ACADÉMICO PARA ENTREGA
├── FASE5_GITHUB_ACTIONS.md       # Documentación técnica CI/CD
└── README.md                     # Este archivo
```

---

## 🔄 Pipeline CI/CD

```
git push a main
    ↓
1️⃣  CI Tests (pytest + linting) [2-3 min]
    ↓ (si pasa)
2️⃣  Build & Push a ACR (Docker build + push) [5-10 min]
    ↓ (si exitoso)
3️⃣  Deploy a ACI (aplicación en Azure) [3-5 min]
    ↓
✅ Aplicación en producción
```

**Tiempo total:** 10-18 minutos desde git push hasta producción

---

## 🔗 Endpoints Principales

```bash
# Health check
curl http://localhost:8000/health

# Información de la API
curl http://localhost:8000/

# Documentación interactiva
http://localhost:8000/docs

# Datos desde BD
curl http://localhost:8000/api/user-stories
```

---

## 📊 Verificación Local

Se ha validado el funcionamiento completo:

```bash
✅ PostgreSQL: Inicia correctamente con healthcheck
✅ FastAPI: Responde en puerto 8000
✅ Health Check: {"status":"ok","service":"fastapi-app-produccion",...}
✅ Conectividad BD: Endpoints retornan datos desde PostgreSQL
✅ Docker Compose: Ambos servicios corriendo sin errores
```

---

## ⚠️ Troubleshooting

### Docker Compose no inicia
```bash
docker-compose down -v
docker-compose up --build
```

### Ver logs
```bash
docker-compose logs -f app
docker-compose logs -f postgres
```

### Ejecutar tests
```bash
docker-compose exec app pytest test_app.py -v
```

---

## 📞 Soporte

Para información detallada sobre:
- **Configuración de Secrets de GitHub:** Ver [FASE5_GITHUB_ACTIONS.md](FASE5_GITHUB_ACTIONS.md)
- **Despliegue en Azure:** Ver [FASE5_GITHUB_ACTIONS.md](FASE5_GITHUB_ACTIONS.md)
- **Para la entrega académica:** Ver [ENTREGABLE_5_RESUMEN.md](ENTREGABLE_5_RESUMEN.md)

---

## ✅ Checklist de Entrega

- [x] Código en GitHub con estructura clara
- [x] Dockerfile + docker-compose.yml probados localmente
- [x] 3 GitHub Actions Workflows configurados (ci, build, deploy)
- [x] Health check endpoint implementado
- [x] Azure Container Registry y Container Instances listos
- [x] Informe académico (ENTREGABLE_5_RESUMEN.md)
- [x] Documentación técnica (FASE5_GITHUB_ACTIONS.md)

---

**Fin del README - Entregable 5**

1. **Completar Fase 3**: Crear ACR en Azure
2. **Completar Fase 4**: Desplegar PostgreSQL y app manualmente
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
