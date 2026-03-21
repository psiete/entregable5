-- Script de inicialización para PostgreSQL
-- Este archivo se ejecuta automáticamente en el primer inicio del contenedor

-- Crear tipos ENUM para estados
CREATE TYPE story_status AS ENUM ('pending', 'in_progress', 'completed');
CREATE TYPE task_status AS ENUM ('pending', 'in_progress', 'completed');
CREATE TYPE task_priority AS ENUM ('low', 'medium', 'high');

-- Crear tabla de historias de usuario
CREATE TABLE user_stories (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    status story_status DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Crear tabla de tareas
CREATE TABLE tasks (
    id SERIAL PRIMARY KEY,
    user_story_id INTEGER NOT NULL REFERENCES user_stories(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    status task_status DEFAULT 'pending',
    priority task_priority DEFAULT 'medium',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Crear índices para mejorar performance
CREATE INDEX idx_tasks_user_story_id ON tasks(user_story_id);

-- Insertar datos de ejemplo
INSERT INTO user_stories (title, description) VALUES
('Primera historia de usuario', 'Descripción de la primera historia'),
('Segunda historia de usuario', 'Descripción de la segunda historia');

-- Verificar datos
SELECT * FROM user_stories;
