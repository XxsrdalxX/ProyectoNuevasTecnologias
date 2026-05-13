-- Migration: Add avatar column to usuario table
-- Run this if you already have the database created (skip if using datos_prueba.sql fresh)

ALTER TABLE public.usuario
    ADD COLUMN IF NOT EXISTS avatar character varying(255);

-- Assign default avatars to existing test users
UPDATE public.usuario SET avatar = 'img/avatar1.jpg' WHERE correo = 'juan@example.com';
UPDATE public.usuario SET avatar = 'img/avatar2.jpg' WHERE correo = 'maria@example.com';
UPDATE public.usuario SET avatar = 'img/profile.jpg' WHERE correo = 'carlos@example.com';
UPDATE public.usuario SET avatar = 'img/avatar3.jpg' WHERE correo = 'ana@example.com';
