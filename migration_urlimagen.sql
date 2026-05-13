-- Migración: agregar columna urlimagen a la tabla juego
-- Ejecutar una sola vez en pgAdmin o psql sobre db_GameReviews

ALTER TABLE public.juego
    ADD COLUMN IF NOT EXISTS urlimagen TEXT;

-- Actualizar imágenes para los juegos de prueba
UPDATE public.juego SET urlimagen = 'img/Eldenring.jpg'              WHERE titulo = 'Elden Ring';
UPDATE public.juego SET urlimagen = 'img/baldurs.jpg'                WHERE titulo = 'Baldur''s Gate 3';
UPDATE public.juego SET urlimagen = 'img/cyberpunk.jpg'              WHERE titulo = 'Cyberpunk 2077';
UPDATE public.juego SET urlimagen = 'img/ZeldaTearsOfTheKingdom.jpg' WHERE titulo = 'The Legend of Zelda: Tears of the Kingdom';
UPDATE public.juego SET urlimagen = 'img/StardewValley.jpg'          WHERE titulo = 'Stardew Valley';
UPDATE public.juego SET urlimagen = 'img/helldivers.jpg'             WHERE titulo = 'Helldivers 2';
UPDATE public.juego SET urlimagen = 'img/ff16.jpg'                   WHERE titulo = 'Final Fantasy XVI';
UPDATE public.juego SET urlimagen = 'img/witcher.jpg'                WHERE titulo = 'The Witcher 3: Wild Hunt';
UPDATE public.juego SET urlimagen = 'img/Juego.jpg'                  WHERE titulo = 'Sekiro: Shadows Die Twice';
UPDATE public.juego SET urlimagen = 'img/rdr.jpg'                    WHERE titulo = 'Divinity: Original Sin 2';
