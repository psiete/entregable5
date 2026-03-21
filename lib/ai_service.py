"""
Módulo de integración con OpenAI / Azure OpenAI para generación de historias y tareas.
Utiliza respuestas estructuradas con Pydantic para asegurar calidad de datos.
"""

import os
import logging
from typing import Optional, List
from pydantic import BaseModel, Field
import json

logger = logging.getLogger(__name__)

# ============================================================================
# MODELOS PYDANTIC PARA RESPUESTAS ESTRUCTURADAS DE IA
# ============================================================================

class UserStoryGenerated(BaseModel):
    """Modelo para una historia de usuario generada por IA con campos estructurados."""
    title: str = Field(..., description="Título de la historia de usuario")
    description: str = Field(..., description="Descripción detallada de la historia")
    project: str = Field(..., description="Proyecto o módulo al que pertenece")
    priority: str = Field(..., description="Prioridad: low, medium, high")
    story_points: int = Field(..., ge=1, le=100, description="Puntos de historia estimados (1-100)")
    effort_hours: float = Field(..., ge=0.5, le=160, description="Horas estimadas de esfuerzo")


class UserStoriesGeneratedResponse(BaseModel):
    """Colección de historias generadas por IA."""
    stories: List[UserStoryGenerated] = Field(..., description="Lista de historias generadas")
    total_story_points: int = Field(..., description="Total de puntos estimados")
    total_effort_hours: float = Field(..., description="Total de horas estimadas")


class TaskGenerated(BaseModel):
    """Modelo para una tarea generada por IA con campos estructurados."""
    title: str = Field(..., description="Título de la tarea")
    description: str = Field(..., description="Descripción detallada de la tarea")
    priority: str = Field(..., description="Prioridad: low, medium, high")
    effort_hours: float = Field(..., ge=0.5, le=80, description="Horas estimadas")
    subtasks: Optional[List[str]] = Field(default=None, description="Subtareas si existen")


class TasksGeneratedResponse(BaseModel):
    """Colección de tareas generadas por IA para una historia."""
    tasks: List[TaskGenerated] = Field(..., description="Lista de tareas generadas")
    total_effort_hours: float = Field(..., description="Total de horas estimadas")
    estimated_days: float = Field(..., description="Días estimados (considerando 8h/día)")


# ============================================================================
# CONFIGURACIÓN DE PROVEEDORES DE IA
# ============================================================================

AI_PROVIDER = os.getenv("AI_PROVIDER", "openai").lower()
AI_ENABLED = os.getenv("AI_ENABLED", "false").lower() == "true"

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4-turbo-preview")

AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT")


# ============================================================================
# CLIENTE DE IA CON RESPUESTAS ESTRUCTURADAS
# ============================================================================

class AIService:
    """Servicio de IA para generar historias y tareas con respuestas estructuradas."""
    
    def __init__(self):
        """Inicializa el cliente de IA basado en el proveedor configurado."""
        self.enabled = AI_ENABLED
        self.provider = AI_PROVIDER
        self.client = None
        
        if not self.enabled:
            logger.info("Servicio de IA deshabilitado (AI_ENABLED=false)")
            return
        
        try:
            if self.provider == "openai":
                if not OPENAI_API_KEY:
                    raise ValueError("OPENAI_API_KEY no está configurada")
                from openai import OpenAI
                self.client = OpenAI(api_key=OPENAI_API_KEY)
                logger.info(f"✅ Cliente OpenAI inicializado (modelo: {OPENAI_MODEL})")
                
            elif self.provider == "azure_openai":
                if not all([AZURE_OPENAI_API_KEY, AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_DEPLOYMENT]):
                    raise ValueError("Credenciales de Azure OpenAI incompletas")
                from openai import AzureOpenAI
                self.client = AzureOpenAI(
                    api_key=AZURE_OPENAI_API_KEY,
                    api_version="2024-02-15-preview",
                    azure_endpoint=AZURE_OPENAI_ENDPOINT
                )
                logger.info(f"✅ Cliente Azure OpenAI inicializado (deployment: {AZURE_OPENAI_DEPLOYMENT})")
            else:
                raise ValueError(f"Proveedor de IA desconocido: {self.provider}")
                
        except Exception as e:
            logger.error(f"❌ Error inicializando servicio de IA: {e}")
            self.enabled = False
    
    def generate_user_stories(self, context: str, count: int = 3) -> Optional[UserStoriesGeneratedResponse]:
        """
        Genera historias de usuario estructuradas usando respuestas de IA.
        
        Args:
            context: Contexto o descripción del proyecto/requisito
            count: Número de historias a generar (defecto: 3)
        
        Returns:
            UserStoriesGeneratedResponse con historias validadas, o None si IA está deshabilitada
        """
        if not self.enabled or not self.client:
            logger.warning("IA deshabilitada; usando valores por defecto")
            return None
        
        try:
            prompt = f"""
            Genera {count} historias de usuario bien estructuradas basadas en el siguiente contexto:
            
            {context}
            
            Para cada historia, proporciona:
            - title: Nombre conciso de la historia (máx 100 caracteres)
            - description: Descripción detallada de qué se necesita (máx 500 caracteres)
            - project: Proyecto o módulo al que pertenece
            - priority: Prioridad estimada (low, medium, high)
            - story_points: Puntos de historia (1-100)
            - effort_hours: Horas estimadas de trabajo (0.5-160)
            
            Responde en formato JSON que pueda ser parseado a lista de objetos con esos campos.
            """
            
            if self.provider == "openai":
                response = self.client.beta.chat.completions.parse(
                    model=OPENAI_MODEL,
                    messages=[{"role": "user", "content": prompt}],
                    response_format=UserStoriesGeneratedResponse,
                    temperature=0.7,
                    max_tokens=2000
                )
            else:  # Azure OpenAI
                response = self.client.beta.chat.completions.parse(
                    model=AZURE_OPENAI_DEPLOYMENT,
                    messages=[{"role": "user", "content": prompt}],
                    response_format=UserStoriesGeneratedResponse,
                    temperature=0.7,
                    max_tokens=2000
                )
            
            # Parsear respuesta estructurada
            result = response.choices[0].message.parsed
            
            if result:
                logger.info(f"✅ Generadas {len(result.stories)} historias de usuario")
                return result
            else:
                logger.warning("IA retornó respuesta vacía")
                return None
                
        except Exception as e:
            logger.error(f"❌ Error generando historias: {e}")
            return None
    
    def generate_tasks(self, story_title: str, story_description: str, 
                      count: int = 5) -> Optional[TasksGeneratedResponse]:
        """
        Genera tareas estructuradas para una historia de usuario usando IA.
        
        Args:
            story_title: Título de la historia
            story_description: Descripción de la historia
            count: Número de tareas a generar (defecto: 5)
        
        Returns:
            TasksGeneratedResponse con tareas validadas, o None si IA está deshabilitada
        """
        if not self.enabled or not self.client:
            logger.warning("IA deshabilitada; usando valores por defecto")
            return None
        
        try:
            prompt = f"""
            Genera {count} tareas técnicas para la siguiente historia de usuario:
            
            Título: {story_title}
            Descripción: {story_description}
            
            Para cada tarea, proporciona:
            - title: Nombre de la tarea (máx 100 caracteres)
            - description: Descripción técnica de lo que se debe hacer (máx 300 caracteres)
            - priority: Prioridad dentro de la historia (low, medium, high)
            - effort_hours: Horas estimadas de trabajo (0.5-80)
            - subtasks: Lista de subtareas si existen (opcional)
            
            Las tareas deben ser independientes pero coherentes para completar la historia.
            Responde en formato JSON que pueda ser parseado a lista de objetos con esos campos.
            """
            
            if self.provider == "openai":
                response = self.client.beta.chat.completions.parse(
                    model=OPENAI_MODEL,
                    messages=[{"role": "user", "content": prompt}],
                    response_format=TasksGeneratedResponse,
                    temperature=0.7,
                    max_tokens=2000
                )
            else:  # Azure OpenAI
                response = self.client.beta.chat.completions.parse(
                    model=AZURE_OPENAI_DEPLOYMENT,
                    messages=[{"role": "user", "content": prompt}],
                    response_format=TasksGeneratedResponse,
                    temperature=0.7,
                    max_tokens=2000
                )
            
            # Parsear respuesta estructurada
            result = response.choices[0].message.parsed
            
            if result:
                logger.info(f"✅ Generadas {len(result.tasks)} tareas para la historia")
                return result
            else:
                logger.warning("IA retornó respuesta vacía")
                return None
                
        except Exception as e:
            logger.error(f"❌ Error generando tareas: {e}")
            return None


# Instancia global del servicio de IA
ai_service = AIService()
