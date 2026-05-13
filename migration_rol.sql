-- Migración: agregar columna rol a la tabla usuario
-- Ejecutar una sola vez en pgAdmin o psql sobre db_GameReviews

ALTER TABLE public.usuario
    ADD COLUMN IF NOT EXISTS rol VARCHAR(10) NOT NULL DEFAULT 'cliente';

-- Opcional: promover un usuario existente a administrador
-- Reemplazar <id_del_usuario> por el id real del admin:
-- UPDATE public.usuario SET rol = 'admin' WHERE idusuario = <id_del_usuario>;
