"""
Rutas API para la aplicación FastAPI.
Define endpoints para gestión de historias de usuario y tareas.
Incluye generación automática con IA usando respuestas estructuradas.
"""

from fastapi import APIRouter, HTTPException, status
from typing import List, Dict, Any
from pydantic import BaseModel

from lib.database import (
    get_all_user_stories,
    create_user_story,
    get_user_story,
    get_tasks_for_story,
    create_task
)
from lib.ai_service import ai_service, UserStoriesGeneratedResponse, TasksGeneratedResponse

router = APIRouter(prefix="/api", tags=["user-stories"])


# Modelos Pydantic para validación
class UserStoryCreate(BaseModel):
    """Modelo para crear una historia de usuario."""
    title: str
    description: str = ""


class TaskCreate(BaseModel):
    """Modelo para crear una tarea."""
    title: str
    description: str = ""
    priority: str = "medium"


# ============================================================================
# ENDPOINTS DE HISTORIAS DE USUARIO
# ============================================================================

@router.get("/user-stories", response_model=List[Dict[str, Any]])
async def list_user_stories():
    """
    Obtiene todas las historias de usuario.
    
    Returns:
        Lista de historias de usuario
    """
    stories = get_all_user_stories()
    return stories


@router.post("/user-stories", status_code=status.HTTP_201_CREATED)
async def create_new_user_story(story: UserStoryCreate):
    """
    Crea una nueva historia de usuario.
    
    Args:
        story: Datos de la historia (title, description)
    
    Returns:
        Confirmación con ID de la historia creada
    """
    story_id = create_user_story(story.title, story.description)
    
    if story_id is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error crear historia en la BD"
        )
    
    return {
        "id": story_id,
        "title": story.title,
        "description": story.description,
        "message": "Historia creada exitosamente"
    }


@router.get("/user-stories/{story_id}")
async def get_story(story_id: int):
    """
    Obtiene una historia específica por ID.
    
    Args:
        story_id: ID de la historia
    
    Returns:
        Datos de la historia
    """
    story = get_user_story(story_id)
    
    if story is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Historia {story_id} no encontrada"
        )
    
    return story


# ============================================================================
# ENDPOINTS DE GENERACIÓN CON IA
# ============================================================================

class GenerateStoriesRequest(BaseModel):
    """Modelo para solicitar generación de historias con IA."""
    context: str
    count: int = 3


@router.post("/generate-user-stories")
async def generate_user_stories_with_ai(request: GenerateStoriesRequest):
    """
    Genera historias de usuario automáticamente usando IA con respuestas estructuradas.
    Las historias se crean en la BD con campos validados (priority, story_points, effort_hours).
    
    Args:
        request: Contexto o descripción del proyecto + número de historias
    
    Returns:
        Historias generadas con detalles (priority, points, effort estimada, etc.)
    """
    if not ai_service.enabled:
        return {
            "message": "Servicio de IA deshabilitado (AI_ENABLED=false)",
            "stories": [],
            "note": "Configura OPENAI_API_KEY o credenciales de Azure OpenAI en .env para habilitar",
            "setup_guide": "Ver .env.example para instrucciones de configuración"
        }
    
    # Generar historias usando IA con esquema estructurado
    stories_response: UserStoriesGeneratedResponse = ai_service.generate_user_stories(
        context=request.context,
        count=request.count
    )
    
    if not stories_response:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error generando historias con IA"
        )
    
    # Guardar historias en la BD
    created_stories = []
    for story_gen in stories_response.stories:
        story_id = create_user_story(
            title=story_gen.title,
            description=story_gen.description
        )
        
        if story_id:
            created_stories.append({
                "id": story_id,
                "title": story_gen.title,
                "description": story_gen.description,
                "project": story_gen.project,
                "priority": story_gen.priority,
                "story_points": story_gen.story_points,
                "effort_hours": story_gen.effort_hours
            })
    
    return {
        "stories_generated": len(created_stories),
        "stories": created_stories,
        "total_story_points": stories_response.total_story_points,
        "total_effort_hours": stories_response.total_effort_hours,
        "message": f"✅ {len(created_stories)} historias generadas y guardadas exitosamente",
        "ai_provider": ai_service.provider
    }


# ============================================================================
# ENDPOINTS DE TAREAS
# ============================================================================

@router.get("/user-stories/{story_id}/tasks")
async def list_tasks(story_id: int):
    """
    Obtiene todas las tareas de una historia.
    
    Args:
        story_id: ID de la historia
    
    Returns:
        Lista de tareas
    """
    # Verificar que la historia existe
    story = get_user_story(story_id)
    if story is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Historia {story_id} no encontrada"
        )
    
    tasks = get_tasks_for_story(story_id)
    return {"story_id": story_id, "tasks": tasks}


@router.post("/user-stories/{story_id}/tasks", status_code=status.HTTP_201_CREATED)
async def create_new_task(story_id: int, task: TaskCreate):
    """
    Crea una nueva tarea para una historia.
    
    Args:
        story_id: ID de la historia
        task: Datos de la tarea
    
    Returns:
        Confirmación con ID de la tarea creada
    """
    # Verificar que la historia existe
    story = get_user_story(story_id)
    if story is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Historia {story_id} no encontrada"
        )
    
    task_id = create_task(story_id, task.title, task.description, task.priority)
    
    if task_id is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error crear tarea en la BD"
        )
    
    return {
        "id": task_id,
        "story_id": story_id,
        "title": task.title,
        "description": task.description,
        "priority": task.priority,
        "message": "Tarea creada exitosamente"
    }


@router.post("/user-stories/{story_id}/generate-tasks")
async def generate_tasks_from_story(story_id: int):
    """
    Genera tareas automáticamente para una historia usando IA con respuestas estructuradas.
    Las tareas se crean en la BD con los datos validados de la IA.
    
    Args:
        story_id: ID de la historia para la cual generar tareas
    
    Returns:
        Tareas generadas con sus detalles (priority, effort_hours, etc.)
    """
    # Verificar que la historia existe
    story = get_user_story(story_id)
    if story is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Historia {story_id} no encontrada"
        )
    
    # Si IA está deshabilitada, retornar respuesta por defecto
    if not ai_service.enabled:
        return {
            "story_id": story_id,
            "message": "Servicio de IA deshabilitado (AI_ENABLED=false)",
            "tasks": [],
            "note": "Configura OPENAI_API_KEY o credenciales de Azure OpenAI en .env para habilitar"
        }
    
    # Generar tareas usando IA con esquema estructurado
    tasks_response: TasksGeneratedResponse = ai_service.generate_tasks(
        story_title=story["title"],
        story_description=story["description"],
        count=5
    )
    
    if not tasks_response:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error generando tareas con IA"
        )
    
    # Guardar tareas en la BD
    created_tasks = []
    for task in tasks_response.tasks:
        task_id = create_task(
            story_id=story_id,
            title=task.title,
            description=task.description,
            priority=task.priority
        )
        
        if task_id:
            created_tasks.append({
                "id": task_id,
                "title": task.title,
                "description": task.description,
                "priority": task.priority,
                "effort_hours": task.effort_hours,
                "subtasks": task.subtasks or []
            })
    
    return {
        "story_id": story_id,
        "story_title": story["title"],
        "tasks_generated": len(created_tasks),
        "tasks": created_tasks,
        "total_effort_hours": tasks_response.total_effort_hours,
        "estimated_days": tasks_response.estimated_days,
        "message": f"✅ {len(created_tasks)} tareas generadas y guardadas exitosamente"
    }
