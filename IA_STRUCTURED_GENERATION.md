# Generación de Historias y Tareas con IA (Respuestas Estructuradas)

## 🤖 Descripción

La aplicación ahora puede generar **historias de usuario** y **tareas** automáticamente usando OpenAI o Azure OpenAI, con **respuestas estructuradas basadas en Pydantic**. Esto garantiza:

- ✅ Datos validados automáticamente (sin parseo manual de texto)
- ✅ Campos estructurados: `priority`, `story_points`, `effort_hours`, etc.
- ✅ Calidad consistente de datos en la BD
- ✅ Mejor experiencia en la API

---

## 🔧 Configuración

### Opción 1: OpenAI API

**1. Obtener API Key**
- Ir a https://platform.openai.com/account/api-keys
- Crear una nueva API key
- Copiar la clave

**2. Configurar `.env`**
```bash
AI_ENABLED=true
AI_PROVIDER=openai
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4-turbo-preview
```

### Opción 2: Azure OpenAI

**1. Crear recurso en Azure**
```bash
az cognitiveservices account create \
  --name mi-openai \
  --resource-group Proyecto4RG \
  --kind OpenAI \
  --sku S0 \
  --location eastus
```

**2. Crear deployment**
```bash
az cognitiveservices account deployment create \
  --name mi-openai \
  --resource-group Proyecto4RG \
  --deployment-id gpt4-turbo \
  --model-name gpt-4-turbo-preview \
  --model-version 2024-04
```

**3. Obtener credenciales**
```bash
az cognitiveservices account show \
  --name mi-openai \
  --resource-group Proyecto4RG \
  --query properties.endpoint
```

**4. Configurar `.env`**
```bash
AI_ENABLED=true
AI_PROVIDER=azure_openai
AZURE_OPENAI_API_KEY=...
AZURE_OPENAI_ENDPOINT=https://mi-openai.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT=gpt4-turbo
```

---

## 📊 Modelos Pydantic

### UserStoryGenerated
```json
{
  "title": "Autenticación de usuarios",
  "description": "Sistema seguro de login/logout",
  "project": "Backend - Autenticación",
  "priority": "high",
  "story_points": 21,
  "effort_hours": 24.5
}
```

### UserStoriesGeneratedResponse
```json
{
  "stories": [...],
  "total_story_points": 89,
  "total_effort_hours": 95.5
}
```

### TaskGenerated
```json
{
  "title": "Implementar JWT",
  "description": "Crear sistema de tokens JWT",
  "priority": "high",
  "effort_hours": 8.0,
  "subtasks": ["Guardar secreto", "Generar token", "Validar token"]
}
```

### TasksGeneratedResponse
```json
{
  "tasks": [...],
  "total_effort_hours": 40.0,
  "estimated_days": 5.0
}
```

---

## 🚀 Uso de la API

### 1. Generar Historias de Usuario

**Endpoint:** `POST /api/generate-user-stories`

```bash
curl -X POST http://localhost:8000/api/generate-user-stories \
  -H "Content-Type: application/json" \
  -d '{
    "context": "Sistema de gestión de tareas para equipos distribuidos. Necesitamos crear historias para MVP inicial enfocado en autenticación y gestión básica",
    "count": 3
  }'
```

**Respuesta:**
```json
{
  "stories_generated": 3,
  "stories": [
    {
      "id": 10,
      "title": "Autenticación con email/contraseña",
      "description": "Los usuarios pueden registrarse e iniciar sesión...",
      "project": "Backend - Autenticación",
      "priority": "high",
      "story_points": 21,
      "effort_hours": 24.5
    },
    {...},
    {...}
  ],
  "total_story_points": 89,
  "total_effort_hours": 95.5,
  "message": "✅ 3 historias generadas y guardadas exitosamente",
  "ai_provider": "openai"
}
```

---

### 2. Generar Tareas para una Historia

**Endpoint:** `POST /api/user-stories/{story_id}/generate-tasks`

```bash
# Generar tareas para la historia con ID 1
curl -X POST http://localhost:8000/api/user-stories/1/generate-tasks
```

**Respuesta:**
```json
{
  "story_id": 1,
  "story_title": "Primera historia de usuario",
  "tasks_generated": 5,
  "tasks": [
    {
      "id": 1,
      "title": "Diseñar esquema de BD",
      "description": "Crear tablas para user_stories y tasks...",
      "priority": "high",
      "effort_hours": 4.0,
      "subtasks": ["Análisis", "Diseño", "Validación"]
    },
    {...},
    {...}
  ],
  "total_effort_hours": 40.0,
  "estimated_days": 5.0,
  "message": "✅ 5 tareas generadas y guardadas exitosamente"
}
```

---

## 🎯 Flujo Completo (Ejemplo)

```bash
# 1. Generar 3 historias de usuario
curl -X POST http://localhost:8000/api/generate-user-stories \
  -H "Content-Type: application/json" \
  -d '{
    "context": "App de gestión de tareas tipo Jira",
    "count": 3
  }'

# 2. Obtener todas las historias
curl http://localhost:8000/api/user-stories

# 3. Generar tareas para la historia 1
curl -X POST http://localhost:8000/api/user-stories/1/generate-tasks

# 4. Ver tareas de la historia 1
curl http://localhost:8000/api/user-stories/1/tasks

# 5. Inspeccionar los datos en BD
docker-compose exec mysql mysql -u proyecto_user -p proyecto_db
# SELECT * FROM user_stories;
# SELECT * FROM tasks WHERE user_story_id = 1;
```

---

## 📝 Campos de Respuesta Estructurada

| Campo | Tipo | Descripción | Ejemplo |
|---|---|---|---|
| `title` | string | Nombre de historia/tarea | "Autenticación" |
| `description` | string | Descripción detallada | "Sistema seguro de login" |
| `project` | string | Proyecto/módulo | "Backend - Auth" |
| `priority` | string | Prioridad (low/medium/high) | "high" |
| `story_points` | int | Puntos de historia (1-100) | 21 |
| `effort_hours` | float | Horas estimadas | 24.5 |
| `subtasks` | List[str] | Subtareas (opcional) | ["Guardar secreto", ...] |

---

## ✅ Validaciones Automáticas (Pydantic)

- `priority` debe ser: `"low"`, `"medium"` o `"high"`
- `story_points`: [1, 100]
- `effort_hours` (historias): [0.5, 160]
- `effort_hours` (tareas): [0.5, 80]
- Todos los campos `title` y `description` son requeridos

Si la IA devuelve datos inválidos, Pydantic automáticamente rechaza la respuesta y retorna un error.

---

## 🔒 Seguridad y Costos

### OpenAI
- **Costo:** ~$0.01-0.05 por llamada (dependiendo del modelo)
- **Límite:** Par de historias = 1 llamada; tareas = 1 llamada
- **API Key:** Nunca commitear; usar `.env` + `.gitignore`

### Azure OpenAI
- **Costo:** Pago por tokens (incluido en suscripción Azure)
- **Seguridad:** Integración con Azure AD
- **Endpoint:** Privado en VNet si lo configuras

---

## 🐛 Solución de Problemas

### "AI_ENABLED=false"
```bash
# Solución: Actualizar .env
AI_ENABLED=true
OPENAI_API_KEY=sk-...
```

### "Error: Invalid API key"
- Verificar que la clave está correcta
- Verificar que tiene permisos (presupuesto, modelos habilitados)
- Regenerar clave si es necesario

### "Error: Model not found"
- Verificar que el modelo existe en tu cuenta (gpt-4, gpt-3.5-turbo, etc.)
- Usar el modelo que tengas disponible

### Respuesta vacía
- La IA a veces retorna respuestas mal formadas
- Reintentar (la API implementa reintentos automáticos)
- Ajustar el prompt en `lib/ai_service.py`

---

## 📚 Referencias

- [OpenAI Structured Outputs](https://platform.openai.com/docs/guides/structured-outputs)
- [Azure OpenAI Documentation](https://learn.microsoft.com/en-us/azure/cognitive-services/openai/)
- [Pydantic Documentation](https://docs.pydantic.dev/)

---

## 🚀 Mejoras Futuras

- [ ] Guardar campos de IA en BD (story_points, effort_hours)
- [ ] Histórico de generaciones con IA
- [ ] Fine-tuning de prompts por dominio
- [ ] Feedback del usuario para mejorar generaciones
- [ ] Integración con LLMs locales (Ollama, Llama)
- [ ] Caching de respuestas para mismo contexto

