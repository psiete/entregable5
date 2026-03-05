# Fase 6: Monitoreo y Validación

Este documento guía cómo monitorear la aplicación desplegada en Azure y validar que funciona correctamente.

---

## Paso 6.1: Acceder a Logs de la Aplicación

### Logs del contenedor de aplicación:
```bash
RESOURCE_GROUP="Proyecto4RG"
APP_CONTAINER_NAME="fastapi-app-produccion"

# Ver los últimos logs
az container logs \
  --resource-group $RESOURCE_GROUP \
  --name $APP_CONTAINER_NAME

# Ver logs en tiempo real (follow)
az container logs \
  --resource-group $RESOURCE_GROUP \
  --name $APP_CONTAINER_NAME \
  --follow
```

### Logs del contenedor MySQL:
```bash
MYSQL_CONTAINER_NAME="mysql-bd-produccion"

# Ver los últimos logs
az container logs \
  --resource-group $RESOURCE_GROUP \
  --name $MYSQL_CONTAINER_NAME
```

### Ver eventos del contenedor:
```bash
az container show \
  --resource-group $RESOURCE_GROUP \
  --name $APP_CONTAINER_NAME \
  --query containers[0].instanceView.events
```

---

## Paso 6.2: Pruebas de Conectividad

### 1. Obtener IP de la aplicación:
```bash
APP_IP=$(az container show \
  --resource-group $RESOURCE_GROUP \
  --name $APP_CONTAINER_NAME \
  --query ipAddress.ip -o tsv)

echo "IP de la aplicación: $APP_IP"
```

### 2. Test de endpoint raíz:
```bash
curl http://${APP_IP}:8000/

# Respuesta esperada:
# {"message":"API de gestión de tareas","endpoints":{...}}
```

### 3. Acceder a documentación interactiva (Swagger UI):
```bash
echo "Visitar en navegador: http://${APP_IP}:8000/docs"
```

### 4. Test de endpoint OpenAPI schema:
```bash
curl http://${APP_IP}:8000/openapi.json | jq .

# Debería devolver un JSON con la especificación OpenAPI
```

### 5. Test de conectividad con base de datos:
Si la aplicación tiene un endpoint específico para verificar la BD:
```bash
curl http://${APP_IP}:8000/health

# O prueba un endpoint que requiera BD (si existe)
curl -X POST http://${APP_IP}:8000/user-stories
```

---

## Paso 6.3: Pruebas de Carga Básicas (Opcional)

Si tienes `ab` (Apache Bench) instalado:
```bash
# 100 requests, 10 simultáneos
ab -n 100 -c 10 http://${APP_IP}:8000/

# Analizar respuestas, req/sec, tiempo promedio, etc.
```

---

## Paso 6.4: Validar Configuración de Ambiente

### Verificar variables de entorno en el contenedor:
```bash
az container show \
  --resource-group $RESOURCE_GROUP \
  --name $APP_CONTAINER_NAME \
  --query containers[0].environmentVariables
```

Debería mostrar todas las variables MYSQL_*, APP_ENV, etc.

---

## Paso 6.5: Troubleshooting Común

### La aplicación no responde (status code 502/503)
```bash
# Ver logs más detallados
az container logs --resource-group $RESOURCE_GROUP --name $APP_CONTAINER_NAME --follow

# Verificar que el contenedor sigue corriendo
az container show \
  --resource-group $RESOURCE_GROUP \
  --name $APP_CONTAINER_NAME \
  --query "{{ 'instanceView': containers[0].instanceView }}"
```

### Error de conexión a MySQL
```bash
# Verificar que MySQL está corriendo
az container show \
  --resource-group $RESOURCE_GROUP \
  --name mysql-bd-produccion \
  --query "{{ 'state': instanceView.state, 'IP': ipAddress.ip }}"

# Verificar que la IP en variables de entorno es correcta
az container show \
  --resource-group $RESOURCE_GROUP \
  --name $APP_CONTAINER_NAME \
  --query containers[0].environmentVariables | grep MYSQL_HOST
```

### Puerto 8000 no está accesible
```bash
# Verificar que el puerto está expuesto
az container show \
  --resource-group $RESOURCE_GROUP \
  --name $APP_CONTAINER_NAME \
  --query "ipAddress.ports"

# Debería mostrar puerto 8000 en TCP
```

---

## Paso 6.6: Captura de Pantallas para Informe

Para documentar el despliegue, capturar:

1. **Salida de `az container list`:**
   ```bash
   az container list --resource-group $RESOURCE_GROUP -o table
   ```

2. **IP pública y acceso a /docs:**
   - Captura del navegador mostrando `http://${APP_IP}:8000/docs`

3. **Logs de salida exitosa:**
   ```bash
   az container logs --resource-group $RESOURCE_GROUP --name $APP_CONTAINER_NAME
   ```

4. **Respuesta JSON de la API:**
   ```bash
   curl http://${APP_IP}:8000/ | jq .
   ```

5. **Información del contenedor:**
   ```bash
   az container show --resource-group $RESOURCE_GROUP --name $APP_CONTAINER_NAME -o json
   ```

---

## Paso 6.7: Health Checks Automáticos

Para monitoreo continuo, puedes crear un script local:

```bash
#!/bin/bash
# check-health.sh

RESOURCE_GROUP="Proyecto4RG"
APP_CONTAINER_NAME="fastapi-app-produccion"

APP_IP=$(az container show \
  --resource-group $RESOURCE_GROUP \
  --name $APP_CONTAINER_NAME \
  --query ipAddress.ip -o tsv)

echo "Verificando salud de la aplicación..."
echo "IP: $APP_IP"

# Test 1: Conectividad básica
if curl -s http://${APP_IP}:8000/ > /dev/null; then
  echo "✅ API respondiendo correctamente"
else
  echo "❌ API no responde"
fi

# Test 2: Documentación OpenAPI
if curl -s http://${APP_IP}:8000/openapi.json > /dev/null; then
  echo "✅ OpenAPI schema disponible"
else
  echo "❌ OpenAPI schema no accesible"
fi

echo "Timestamp: $(date)"
```

Ejecutar periódicamente:
```bash
chmod +x check-health.sh
./check-health.sh
```

---

## Resumen de Validación

| Validación | Comando | Resultado Esperado |
|---|---|---|
| **Contenedores activos** | `az container list -g Proyecto4RG -o table` | 2 contenedores (app + mysql) |
| **API respondiendo** | `curl http://$IP:8000/` | JSON con endpoints |
| **Documentación visible** | Navegador a `http://$IP:8000/docs` | Swagger UI cargado |
| **BD conectada** | Logs de app sin errores de conexión | Sin "Connection refused" |
| **Variables correctas** | `az container show ... query containers[0].environmentVariables` | MYSQL_HOST, MYSQL_USER poblados |

