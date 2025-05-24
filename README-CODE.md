
**Actualización de Vistas para Considerar Borrado Suave**

-- Vista actualizada para profesionales con imágenes (excluyendo eliminados)
CREATE VIEW vista_profesionales_con_imagenes AS
SELECT p.*, COUNT(i.id) AS total_imagenes
FROM profesionales p
LEFT JOIN imagenes_profesionales i ON p.usuario_id = i.profesional_id AND i.eliminado = FALSE
WHERE p.eliminado = FALSE
GROUP BY p.usuario_id;

-- Vista actualizada para recomendaciones de cliente (excluyendo eliminados)
CREATE VIEW vista_recomendaciones_cliente AS
SELECT a.cliente_id, r.imagen_recomendada_id, r.puntuacion, 
       i.profesional_id, i.url_imagen, i.titulo, c.nombre AS categoria
FROM recomendaciones r
JOIN analisis_facial a ON r.analisis_id = a.id AND a.eliminado = FALSE
JOIN imagenes_profesionales i ON r.imagen_recomendada_id = i.id AND i.eliminado = FALSE
JOIN categorias_imagenes c ON i.categoria_id = c.id AND c.eliminado = FALSE
WHERE r.eliminado = FALSE;

**Procedimientos Almacenados Actualizados**


-- Procedimiento para "eliminar" un profesional (borrado suave)
DELIMITER //
CREATE PROCEDURE eliminar_profesional(
    IN p_usuario_id INT
)
BEGIN
    UPDATE profesionales 
    SET eliminado = TRUE, actualizado_en = CURRENT_TIMESTAMP
    WHERE usuario_id = p_usuario_id;
    
    UPDATE usuarios
    SET activo = FALSE, actualizado_en = CURRENT_TIMESTAMP
    WHERE id = p_usuario_id;
END //
DELIMITER ;

-- Procedimiento para restaurar un profesional
DELIMITER //
CREATE PROCEDURE restaurar_profesional(
    IN p_usuario_id INT
)
BEGIN
    UPDATE profesionales 
    SET eliminado = FALSE, actualizado_en = CURRENT_TIMESTAMP
    WHERE usuario_id = p_usuario_id;
    
    UPDATE usuarios
    SET activo = TRUE, actualizado_en = CURRENT_TIMESTAMP
    WHERE id = p_usuario_id;
END //
DELIMITER ;

-- Procedimiento para obtener solo registros no eliminados
DELIMITER //
CREATE PROCEDURE obtener_profesionales_activos()
BEGIN
    SELECT * FROM profesionales 
    WHERE eliminado = FALSE
    ORDER BY nombre, apellido;
END //
DELIMITER ;


**Consultas Ejemplo con Borrado Suave**

-- Consulta para obtener todos los profesionales no eliminados
SELECT * FROM profesionales WHERE eliminado = FALSE;

-- Consulta para obtener imágenes de un profesional (excluyendo eliminadas)
SELECT * FROM imagenes_profesionales 
WHERE profesional_id = [ID_PROFESIONAL] AND eliminado = FALSE;

-- Consulta para "eliminar" una imagen (borrado suave)
UPDATE imagenes_profesionales 
SET eliminado = TRUE, actualizado_en = CURRENT_TIMESTAMP 
WHERE id = [ID_IMAGEN];

-- Consulta para contar imágenes por categoría (excluyendo eliminadas)
SELECT c.nombre, COUNT(i.id) as total_imagenes
FROM categorias_imagenes c
LEFT JOIN imagenes_profesionales i ON c.id = i.categoria_id AND i.eliminado = FALSE
WHERE c.eliminado = FALSE
GROUP BY c.id;


///////////////////////////////////////////////////////////////

    Este diseño mejorado incluye:

    Columnas creado_en para registrar cuando se creó el registro

    Columnas actualizado_en que se auto-actualizan con cada modificación

    Columnas eliminado para implementar borrado suave (soft delete)

    Vistas y procedimientos actualizados para trabajar con el borrado suave

    Mantenimiento de integridad referencial incluso con borrado suave

    El borrado suave permite:

    Recuperar datos accidentalmente eliminados

    Mantener historiales completos

    Cumplir con regulaciones de retención de datos

    Evitar problemas de integridad referencial





la estructura del proyecto 


/proyecto_api/
│
├── app/
│   ├── __init__.py
│   ├── config.py
│   ├── extensions.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── profesional.py
│   │   ├── imagen_profesional.py
│   │   └── ... otros modelos
│   ├── services/
│   │   ├── __init__.py
│   │   ├── auth_service.py
│   │   ├── profesional_service.py
│   │   └── ... otros servicios
│   ├── controllers/
│   │   ├── __init__.py
│   │   ├── auth_controller.py
│   │   ├── profesional_controller.py
│   │   └── ... otros controladores
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── decorators.py
│   │   ├── security.py
│   │   └── ... otras utilidades
│   └── static/
│       └── ... archivos estáticos
│
├── migrations/
│   └── ... (generado por Flask-Migrate)
│
├── requirements.txt
├── run.py
└── .env