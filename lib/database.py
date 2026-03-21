"""
Módulo de gestión de base de datos PostgreSQL.
Maneja la conexión y operaciones básicas con BD.
"""

import os
import psycopg2
from psycopg2.extras import RealDictCursor
from typing import Optional, List, Dict, Any
import logging

logger = logging.getLogger(__name__)

# Configuración de BD desde variables de entorno
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT = int(os.getenv("POSTGRES_PORT", 5432))
POSTGRES_USER = os.getenv("POSTGRES_USER", "proyecto_user")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "changeme123!")
POSTGRES_DB = os.getenv("POSTGRES_DB", "proyecto_db")


class DatabaseConnection:
    """Gestor de conexiones a PostgreSQL."""
    
    _instance: Optional[psycopg2.extensions.connection] = None
    
    @classmethod
    def get_connection(cls) -> psycopg2.extensions.connection:
        """Obtiene una conexión a la BD, la crea si no existe."""
        if cls._instance is None:
            try:
                cls._instance = psycopg2.connect(
                    host=POSTGRES_HOST,
                    port=POSTGRES_PORT,
                    user=POSTGRES_USER,
                    password=POSTGRES_PASSWORD,
                    database=POSTGRES_DB
                )
                logger.info(f"✅ Conectado a BD: {POSTGRES_DB}@{POSTGRES_HOST}")
            except Exception as e:
                logger.warning(f"⚠️ Error conectando a BD: {e}")
                cls._instance = None
        return cls._instance
    
    @classmethod
    def close(cls):
        """Cierra la conexión a la BD."""
        if cls._instance:
            cls._instance.close()
            cls._instance = None


def init_db():
    """Inicializa la conexión a la base de datos."""
    try:
        conn = DatabaseConnection.get_connection()
        if conn:
            logger.info("✅ Base de datos inicializada correctamente")
            return True
    except Exception as e:
        logger.error(f"❌ Error inicializando BD: {e}")
    return False


def get_all_user_stories() -> List[Dict[str, Any]]:
    """Obtiene todas las historias de usuario."""
    try:
        conn = DatabaseConnection.get_connection()
        if not conn:
            logger.warning("No hay conexión a BD")
            return []
        
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM user_stories ORDER BY created_at DESC")
            return cursor.fetchall() or []
    except Exception as e:
        logger.error(f"Error obteniendo historias: {e}")
        return []


def create_user_story(title: str, description: str = "") -> Optional[int]:
    """Crea una nueva historia de usuario."""
    try:
        conn = DatabaseConnection.get_connection()
        if not conn:
            logger.warning("No hay conexión a BD")
            return None
        
        with conn.cursor() as cursor:
            cursor.execute(
                "INSERT INTO user_stories (title, description) VALUES (%s, %s)",
                (title, description)
            )
            conn.commit()
            return cursor.lastrowid
    except Exception as e:
        logger.error(f"Error creando historia: {e}")
        return None


def get_user_story(story_id: int) -> Optional[Dict[str, Any]]:
    """Obtiene una historia específica por ID."""
    try:
        conn = DatabaseConnection.get_connection()
        if not conn:
            return None
        
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM user_stories WHERE id = %s", (story_id,))
            return cursor.fetchone()
    except Exception as e:
        logger.error(f"Error obteniendo historia {story_id}: {e}")
        return None


def get_tasks_for_story(story_id: int) -> List[Dict[str, Any]]:
    """Obtiene todas las tareas de una historia."""
    try:
        conn = DatabaseConnection.get_connection()
        if not conn:
            return []
        
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM tasks WHERE user_story_id = %s ORDER BY created_at",
                (story_id,)
            )
            return cursor.fetchall() or []
    except Exception as e:
        logger.error(f"Error obteniendo tareas para historia {story_id}: {e}")
        return []


def create_task(story_id: int, title: str, description: str = "", 
                priority: str = "medium") -> Optional[int]:
    """Crea una nueva tarea para una historia."""
    try:
        conn = DatabaseConnection.get_connection()
        if not conn:
            return None
        
        with conn.cursor() as cursor:
            cursor.execute(
                "INSERT INTO tasks (user_story_id, title, description, priority) "
                "VALUES (%s, %s, %s, %s)",
                (story_id, title, description, priority)
            )
            conn.commit()
            return cursor.lastrowid
    except Exception as e:
        logger.error(f"Error creando tarea: {e}")
        return None
