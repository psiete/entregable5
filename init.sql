-- Script de inicialización para MySQL
-- Este archivo se ejecuta automáticamente en el primer inicio del contenedor

-- Crear tabla de historias de usuario (ejemplo básico)
CREATE TABLE IF NOT EXISTS user_stories (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    status ENUM('pending', 'in_progress', 'completed') DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Crear tabla de tareas (ejemplo básico)
CREATE TABLE IF NOT EXISTS tasks (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_story_id INT NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    status ENUM('pending', 'in_progress', 'completed') DEFAULT 'pending',
    priority ENUM('low', 'medium', 'high') DEFAULT 'medium',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_story_id) REFERENCES user_stories(id) ON DELETE CASCADE
);

-- Insertar datos de ejemplo
INSERT INTO user_stories (title, description) VALUES
('Primera historia de usuario', 'Descripción de la primera historia'),
('Segunda historia de usuario', 'Descripción de la segunda historia');

-- Verificar datos
SELECT * FROM user_stories;
