-- ============================================
-- GameReviews - Creación de tablas
-- Ejecutar en pgAdmin conectado a db_GameReviews
-- ============================================

-- Primero crea la base de datos manualmente en pgAdmin,
-- luego conéctate a ella y ejecuta este script.

CREATE TABLE IF NOT EXISTS public.estudio (
    idestudio SERIAL PRIMARY KEY,
    nombre character varying(100) NOT NULL
);

CREATE TABLE IF NOT EXISTS public.genero_juego (
    idgenero SERIAL PRIMARY KEY,
    nombre character varying(100) NOT NULL
);

CREATE TABLE IF NOT EXISTS public.plataforma (
    idplataforma SERIAL PRIMARY KEY,
    nombre character varying(100) NOT NULL
);

CREATE TABLE IF NOT EXISTS public.usuario (
    idusuario SERIAL PRIMARY KEY,
    nombre character varying(100) NOT NULL,
    correo character varying(150) NOT NULL UNIQUE,
    contrasenahash character varying(255) NOT NULL,
    cantidadresenas integer DEFAULT 0,
    rol character varying(10) NOT NULL DEFAULT 'cliente',
    avatar character varying(255)
);

CREATE TABLE IF NOT EXISTS public.juego (
    idjuego SERIAL PRIMARY KEY,
    idestudio integer NOT NULL REFERENCES public.estudio(idestudio) ON UPDATE CASCADE ON DELETE SET NULL,
    idgenero integer NOT NULL REFERENCES public.genero_juego(idgenero) ON UPDATE CASCADE ON DELETE SET NULL,
    idplataforma integer NOT NULL REFERENCES public.plataforma(idplataforma) ON UPDATE CASCADE ON DELETE SET NULL,
    titulo character varying(150) NOT NULL,
    fechalanzamiento date,
    descripcion text,
    precio numeric(10,2),
    calificacionprom numeric(3,2),
    urlimagen text
);

CREATE TABLE IF NOT EXISTS public.resena (
    idresena SERIAL PRIMARY KEY,
    idusuario integer NOT NULL REFERENCES public.usuario(idusuario) ON UPDATE CASCADE ON DELETE CASCADE,
    idjuego integer NOT NULL REFERENCES public.juego(idjuego) ON UPDATE CASCADE ON DELETE CASCADE,
    comentario text,
    puntuacion integer CHECK (puntuacion >= 1 AND puntuacion <= 10),
    fecharesena date DEFAULT CURRENT_DATE
);

CREATE TABLE IF NOT EXISTS public.consulta (
    idconsulta SERIAL PRIMARY KEY,
    idusuario integer NOT NULL REFERENCES public.usuario(idusuario) ON UPDATE CASCADE ON DELETE CASCADE,
    idjuego integer NOT NULL REFERENCES public.juego(idjuego) ON UPDATE CASCADE ON DELETE CASCADE,
    idestudio integer NOT NULL REFERENCES public.estudio(idestudio) ON UPDATE CASCADE ON DELETE CASCADE,
    descripcioncons text,
    fechaconsulta date DEFAULT CURRENT_DATE
);
