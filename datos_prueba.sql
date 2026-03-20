-- ============================================
-- Script de Datos de Prueba para db_GameReviews
-- Ejecutar una sola vez en PostgreSQL
-- ============================================

-- IMPORTANTE: Asegúrate de estar conectado a la base de datos db_GameReviews
-- antes de ejecutar este script en pgAdmin

-- ============================================
-- 1. INSERTAR ESTUDIOS
-- ============================================
INSERT INTO estudio (nombre) VALUES
('FromSoftware'),
('CD Projekt Red'),
('Larian Studios'),
('Nintendo'),
('ConcernedApe'),
('Arrowhead Game Studios'),
('Square Enix'),
('Bethesda Game Studios');

-- ============================================
-- 2. INSERTAR GÉNEROS
-- ============================================
INSERT INTO genero_juego (nombre) VALUES
('RPG'),
('Acción'),
('Aventura'),
('Simulación'),
('Estrategia'),
('Shooter'),
('Indie');

-- ============================================
-- 3. INSERTAR PLATAFORMAS
-- ============================================
INSERT INTO plataforma (nombre) VALUES
('PC'),
('PlayStation 5'),
('Xbox Series X/S'),
('Nintendo Switch'),
('PlayStation 4'),
('Xbox One');

-- ============================================
-- 4. INSERTAR JUEGOS
-- ============================================
INSERT INTO juego (idestudio, idgenero, idplataforma, titulo, fechalanzamiento, descripcion, precio, calificacionprom) VALUES
(
    (SELECT idestudio FROM estudio WHERE nombre = 'FromSoftware'),
    (SELECT idgenero FROM genero_juego WHERE nombre = 'RPG'),
    (SELECT idplataforma FROM plataforma WHERE nombre = 'PC'),
    'Elden Ring',
    '2022-02-25',
    'Un RPG de acción y fantasía oscura desarrollado por FromSoftware y publicado por Bandai Namco. Explora las Tierras Intermedias en este épico juego de mundo abierto.',
    59.99,
    9.5
),
(
    (SELECT idestudio FROM estudio WHERE nombre = 'Larian Studios'),
    (SELECT idgenero FROM genero_juego WHERE nombre = 'RPG'),
    (SELECT idplataforma FROM plataforma WHERE nombre = 'PC'),
    'Baldur''s Gate 3',
    '2023-08-03',
    'Reúne a tu grupo y regresa a los Reinos Olvidados en una historia de compañerismo y traición, sacrificio y supervivencia, y la seducción del poder absoluto.',
    69.99,
    9.6
),
(
    (SELECT idestudio FROM estudio WHERE nombre = 'CD Projekt Red'),
    (SELECT idgenero FROM genero_juego WHERE nombre = 'RPG'),
    (SELECT idplataforma FROM plataforma WHERE nombre = 'PC'),
    'Cyberpunk 2077',
    '2020-12-10',
    'Un RPG de acción de mundo abierto ambientado en Night City, una megalópolis obsesionada con el poder, el glamour y la modificación corporal.',
    49.99,
    8.2
),
(
    (SELECT idestudio FROM estudio WHERE nombre = 'Nintendo'),
    (SELECT idgenero FROM genero_juego WHERE nombre = 'Aventura'),
    (SELECT idplataforma FROM plataforma WHERE nombre = 'Nintendo Switch'),
    'The Legend of Zelda: Tears of the Kingdom',
    '2023-05-12',
    'La aventura continúa en Hyrule con nuevas habilidades y misterios por descubrir en esta secuela de Breath of the Wild.',
    69.99,
    9.7
),
(
    (SELECT idestudio FROM estudio WHERE nombre = 'ConcernedApe'),
    (SELECT idgenero FROM genero_juego WHERE nombre = 'Simulación'),
    (SELECT idplataforma FROM plataforma WHERE nombre = 'PC'),
    'Stardew Valley',
    '2016-02-26',
    'Has heredado la vieja granja de tu abuelo en Stardew Valley. Armado con herramientas de segunda mano y algunas monedas, te dispones a comenzar tu nueva vida.',
    14.99,
    9.1
),
(
    (SELECT idestudio FROM estudio WHERE nombre = 'Arrowhead Game Studios'),
    (SELECT idgenero FROM genero_juego WHERE nombre = 'Shooter'),
    (SELECT idplataforma FROM plataforma WHERE nombre = 'PC'),
    'Helldivers 2',
    '2024-02-08',
    'Shooter cooperativo en tercera persona donde los Helldivers luchan por la libertad a través de la galaxia.',
    39.99,
    8.7
),
(
    (SELECT idestudio FROM estudio WHERE nombre = 'Square Enix'),
    (SELECT idgenero FROM genero_juego WHERE nombre = 'RPG'),
    (SELECT idplataforma FROM plataforma WHERE nombre = 'PlayStation 5'),
    'Final Fantasy XVI',
    '2023-06-22',
    'Una historia épica de fantasía oscura ambientada en el mundo de Valisthea, lleno de magia y conflictos.',
    69.99,
    8.8
),
(
    (SELECT idestudio FROM estudio WHERE nombre = 'CD Projekt Red'),
    (SELECT idgenero FROM genero_juego WHERE nombre = 'RPG'),
    (SELECT idplataforma FROM plataforma WHERE nombre = 'PC'),
    'The Witcher 3: Wild Hunt',
    '2015-05-19',
    'Eres Geralt de Rivia, cazador de monstruos mercenario. Ante ti se abre un continente destrozado por la guerra e infestado de monstruos para que lo explores.',
    39.99,
    9.8
),
(
    (SELECT idestudio FROM estudio WHERE nombre = 'FromSoftware'),
    (SELECT idgenero FROM genero_juego WHERE nombre = 'Acción'),
    (SELECT idplataforma FROM plataforma WHERE nombre = 'PC'),
    'Sekiro: Shadows Die Twice',
    '2019-03-22',
    'Juego de acción y aventura en tercera persona que te pone en la piel de un guerrero desfigurado y caído en desgracia.',
    59.99,
    9.3
),
(
    (SELECT idestudio FROM estudio WHERE nombre = 'Larian Studios'),
    (SELECT idgenero FROM genero_juego WHERE nombre = 'RPG'),
    (SELECT idplataforma FROM plataforma WHERE nombre = 'PC'),
    'Divinity: Original Sin 2',
    '2017-09-14',
    'El juego de rol definitivo. Reúne a tu grupo, desarrolla relaciones y domina los elementos mientras te embarcas en un viaje lleno de profundas historias.',
    44.99,
    9.4
);

-- ============================================
-- 5. INSERTAR USUARIOS DE PRUEBA
-- ============================================
-- Nota: Las contraseñas están hasheadas con un hash simple para demostración
-- En producción deberías usar BCrypt o similar
INSERT INTO usuario (nombre, correo, contrasenahash, cantidadresenas) VALUES
('Juan Pérez', 'juan@example.com', 'hash123', 3),
('María García', 'maria@example.com', 'hash456', 2),
('Carlos López', 'carlos@example.com', 'hash789', 4),
('Ana Martínez', 'ana@example.com', 'hash101', 1);

-- ============================================
-- 6. INSERTAR RESEÑAS
-- ============================================
INSERT INTO resena (idusuario, idjuego, comentario, puntuacion, fecharesena) VALUES
-- Reseñas para Elden Ring
(
    (SELECT idusuario FROM usuario WHERE correo = 'juan@example.com'),
    (SELECT idjuego FROM juego WHERE titulo = 'Elden Ring'),
    'Una obra maestra absoluta. El mundo abierto de FromSoftware es impresionante y cada rincón tiene algo que descubrir.',
    10,
    '2024-01-15'
),
(
    (SELECT idusuario FROM usuario WHERE correo = 'maria@example.com'),
    (SELECT idjuego FROM juego WHERE titulo = 'Elden Ring'),
    'Difícil pero justo. La sensación de superar cada jefe es increíble. Altamente recomendado.',
    9,
    '2024-01-20'
),

-- Reseñas para Baldur's Gate 3
(
    (SELECT idusuario FROM usuario WHERE correo = 'carlos@example.com'),
    (SELECT idjuego FROM juego WHERE titulo = 'Baldur''s Gate 3'),
    'El mejor RPG que he jugado en años. Las decisiones realmente importan y cada partida es diferente.',
    10,
    '2024-02-01'
),
(
    (SELECT idusuario FROM usuario WHERE correo = 'ana@example.com'),
    (SELECT idjuego FROM juego WHERE titulo = 'Baldur''s Gate 3'),
    'Increíble profundidad en los personajes y la historia. Vale cada centavo.',
    10,
    '2024-02-05'
),

-- Reseñas para Cyberpunk 2077
(
    (SELECT idusuario FROM usuario WHERE correo = 'juan@example.com'),
    (SELECT idjuego FROM juego WHERE titulo = 'Cyberpunk 2077'),
    'Después de las actualizaciones ha mejorado muchísimo. Night City es fascinante.',
    8,
    '2024-01-25'
),

-- Reseñas para Zelda TOTK
(
    (SELECT idusuario FROM usuario WHERE correo = 'maria@example.com'),
    (SELECT idjuego FROM juego WHERE titulo = 'The Legend of Zelda: Tears of the Kingdom'),
    'Nintendo lo ha vuelto a lograr. Las nuevas mecánicas son geniales y el mundo es enorme.',
    10,
    '2024-03-01'
),
(
    (SELECT idusuario FROM usuario WHERE correo = 'carlos@example.com'),
    (SELECT idjuego FROM juego WHERE titulo = 'The Legend of Zelda: Tears of the Kingdom'),
    'Mejor que Breath of the Wild, y eso ya es decir mucho. Una maravilla.',
    9,
    '2024-03-05'
),

-- Reseñas para Stardew Valley
(
    (SELECT idusuario FROM usuario WHERE correo = 'juan@example.com'),
    (SELECT idjuego FROM juego WHERE titulo = 'Stardew Valley'),
    'Relajante y adictivo. Perfecto para desconectar después del trabajo.',
    9,
    '2024-02-10'
),
(
    (SELECT idusuario FROM usuario WHERE correo = 'carlos@example.com'),
    (SELECT idjuego FROM juego WHERE titulo = 'Stardew Valley'),
    'Una joya indie. Increíble que lo haya hecho una sola persona.',
    10,
    '2024-02-15'
),

-- Reseña para The Witcher 3
(
    (SELECT idusuario FROM usuario WHERE correo = 'carlos@example.com'),
    (SELECT idjuego FROM juego WHERE titulo = 'The Witcher 3: Wild Hunt'),
    'Un clásico que nunca pasa de moda. La narrativa es excepcional.',
    10,
    '2024-01-30'
);

-- ============================================
-- VERIFICACIÓN DE DATOS INSERTADOS
-- ============================================
SELECT 'Estudios insertados:' AS info, COUNT(*) AS total FROM estudio
UNION ALL
SELECT 'Géneros insertados:', COUNT(*) FROM genero_juego
UNION ALL
SELECT 'Plataformas insertadas:', COUNT(*) FROM plataforma
UNION ALL
SELECT 'Juegos insertados:', COUNT(*) FROM juego
UNION ALL
SELECT 'Usuarios insertados:', COUNT(*) FROM usuario
UNION ALL
SELECT 'Reseñas insertadas:', COUNT(*) FROM resena;

-- Mostrar algunos juegos con sus calificaciones
SELECT
    j.titulo,
    e.nombre AS estudio,
    g.nombre AS genero,
    j.calificacionprom,
    COUNT(r.idresena) AS num_resenas
FROM juego j
LEFT JOIN estudio e ON j.idestudio = e.idestudio
LEFT JOIN genero_juego g ON j.idgenero = g.idgenero
LEFT JOIN resena r ON j.idjuego = r.idjuego
GROUP BY j.idjuego, j.titulo, e.nombre, g.nombre, j.calificacionprom
ORDER BY j.calificacionprom DESC;
