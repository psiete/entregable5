# Guía de Uso Local - MySQL en Docker

## Estado Actual: ✅ MySQL LISTO PARA USAR

La aplicación **FastAPI** está completamente integrada con **MySQL** dentro de Docker. Ya no necesitas instalar nada en tu máquina.

---

## 🚀 Uso en Local (3 comandos)

### 1. Iniciar los servicios
```bash
cd /Users/albertopeset/UNIR/Proyecto4
docker-compose up --build -d
```

### 2. Acceder a la API
```bash
# Raíz
http://localhost:8000

# Documentación interactiva (Swagger UI)
http://localhost:8000/docs

# ReDoc
http://localhost:8000/redoc
```

### 3. Detener los servicios
```bash
docker-compose down

# Si quieres también limpiar datos de BD:
docker-compose down -v
```

---

## 📊 Endpoints Disponibles

### Historias de Usuario
```bash
# Obtener todas
curl http://localhost:8000/api/user-stories

# Crear una
curl -X POST http://localhost:8000/api/user-stories \
  -H "Content-Type: application/json" \
  -d '{"title": "Mi historia", "description": "Descripción"}'

# Obtener una específica
curl http://localhost:8000/api/user-stories/1
```

### Tareas
```bash
# Obtener tareas de una historia
curl http://localhost:8000/api/user-stories/1/tasks

# Crear tarea
curl -X POST http://localhost:8000/api/user-stories/1/tasks \
  -H "Content-Type: application/json" \
  -d '{"title": "Tarea", "priority": "high"}'
```

---

## 🗄️ Base de Datos en Docker

### Ver logs de MySQL
```bash
docker-compose logs mysql
```

### Conectarte a MySQL directamente
```bash
docker-compose exec mysql mysql -u proyecto_user -p proyecto_db
# Contraseña: changeme123!

# Una vez dentro:
SHOW TABLES;
SELECT * FROM user_stories;
SELECT * FROM tasks;
```

### Archivo de inicialización
- Ubicado en: `init.sql`
- Se ejecuta automáticamente en el primer inicio
- Define tablas: `user_stories`, `tasks`

---

## 📝 Variables de Entorno

Las credenciales están en `.env`:
```
MYSQL_HOST=mysql          # Nombre del servicio (Docker)
MYSQL_PORT=3306
MYSQL_USER=proyecto_user
MYSQL_PASSWORD=changeme123!
MYSQL_DATABASE=proyecto_db
MYSQL_ROOT_PASSWORD=root123!
```

---

## ✅ Lo que Está Funcionando

- ✅ FastAPI corriendo en puerto 8000
- ✅ MySQL corriendo en puerto 3306
- ✅ Conexión entre app y BD
- ✅ CRUD completo (Crear, Leer, Actualizar, Eliminar - potencial)
- ✅ Datos persistentes (volumen `mysql_data`)
- ✅ Health checks automáticos
- ✅ Hot reload para desarrollo (cambios en código se recargan automáticamente)

---

## 🔧 Troubleshooting

### Los puertos 8000 o 3306 ya están en uso
```bash
# Ver qué está usando el puerto
lsof -i :8000
lsof -i :3306

# Si Docker está usando los puertos, detener primero
docker-compose down
```

### MySQL no inicia
```bash
# Ver logs
docker-compose logs mysql

# Reintentar
docker-compose down -v
docker-compose up --build mysql
```

### La app no puede conectarse a MySQL
```bash
# Verificar logs de la app
docker-compose logs app

# Verificar que MySQL está healthy
docker-compose ps
# Debe mostrar MySQL con estado "Up (healthy)"
```

---

## 📚 Archivos Creados

```
lib/
├── __init__.py        # Paquete Python
├── database.py        # Conexión y operaciones BD
└── routes.py          # Endpoints API
```

Todos los archivos están integrados automáticamente en la aplicación.

---

## 🎯 Próximos Pasos

1. ✅ **Desarrollo local** → Usar `docker-compose up`
2. 📖 **Despliegue en Azure** → Seguir [FASE3_AZURE_SETUP.md](FASE3_AZURE_SETUP.md)
3. 🔄 **CI/CD automático** → Configurar [FASE5_GITHUB_ACTIONS.md](FASE5_GITHUB_ACTIONS.md)

---

Ahora MySQL está completamente funcional dentro de Docker y listo para desarrollo.
