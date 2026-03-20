// ============================================
// CONFIGURACIÓN DE LA API
// ============================================
const API_BASE_URL = 'http://localhost:8080/api/juegos';

// ============================================
// FUNCIONES PRINCIPALES
// ============================================

/**
 * Carga todos los juegos desde el backend
 */
async function cargarJuegos() {
    try {
        mostrarCargando(true);
        const response = await fetch(API_BASE_URL);
        
        if (!response.ok) {
            throw new Error(`Error HTTP: ${response.status}`);
        }
        
        const juegos = await response.json();
        mostrarJuegos(juegos);
        mostrarCargando(false);
    } catch (error) {
        console.error('Error al cargar juegos:', error);
        mostrarError('No se pudieron cargar los juegos. Verifica que el servidor esté corriendo en el puerto 8080.');
        mostrarCargando(false);
    }
}

/**
 * Busca juegos por título
 */
async function buscarJuegos(termino) {
    if (!termino.trim()) {
        cargarJuegos();
        return;
    }
    
    try {
        mostrarCargando(true);
        const response = await fetch(`${API_BASE_URL}/buscar?titulo=${encodeURIComponent(termino)}`);
        
        if (!response.ok) {
            throw new Error(`Error HTTP: ${response.status}`);
        }
        
        const juegos = await response.json();
        mostrarJuegos(juegos);
        mostrarCargando(false);
    } catch (error) {
        console.error('Error al buscar juegos:', error);
        mostrarError('Error al buscar juegos');
        mostrarCargando(false);
    }
}

/**
 * Obtiene un juego específico por ID
 */
async function obtenerJuegoPorId(id) {
    try {
        const response = await fetch(`${API_BASE_URL}/${id}`);
        
        if (!response.ok) {
            throw new Error(`Error HTTP: ${response.status}`);
        }
        
        return await response.json();
    } catch (error) {
        console.error('Error al obtener juego:', error);
        return null;
    }
}

/**
 * Obtiene los juegos mejor calificados
 */
async function cargarTopJuegos() {
    try {
        mostrarCargando(true);
        const response = await fetch(`${API_BASE_URL}/top`);
        
        if (!response.ok) {
            throw new Error(`Error HTTP: ${response.status}`);
        }
        
        const juegos = await response.json();
        mostrarJuegos(juegos);
        mostrarCargando(false);
    } catch (error) {
        console.error('Error al cargar top juegos:', error);
        mostrarError('Error al cargar los mejores juegos');
        mostrarCargando(false);
    }
}

// ============================================
// FUNCIONES DE RENDERIZADO
// ============================================

/**
 * Muestra los juegos en el grid
 */
function mostrarJuegos(juegos) {
    const gamesGrid = document.getElementById('gamesGrid');
    
    if (!juegos || juegos.length === 0) {
        gamesGrid.innerHTML = `
            <div class="no-results">
                <p>No se encontraron juegos</p>
            </div>
        `;
        return;
    }
    
    gamesGrid.innerHTML = juegos.map(juego => crearTarjetaJuego(juego)).join('');
}

/**
 * Crea el HTML de una tarjeta de juego
 */
function crearTarjetaJuego(juego) {
    console.log('Juego recibido:', juego);

    const imagenUrl = juego.urlimagen || juego.urlImagen || juego.imagenUrl || obtenerImagenPorDefecto(juego.titulo);

    // === CALIFICACIÓN ROBUSTA ===
    let calificacion = 'N/A';
    const posiblesNombres = [
        'calificacionprom', 'calificacionProm', 'calificacion_prom',
        'calificacionPromedio', 'rating', 'puntuacion', 'score'
    ];
    let valorCalificacion = null;
    for (const nombre of posiblesNombres) {
        if (juego[nombre] !== null && juego[nombre] !== undefined) {
            const num = parseFloat(juego[nombre]);
            if (!isNaN(num)) {
                valorCalificacion = num;
                break;
            }
        }
    }
    if (valorCalificacion !== null) {
        calificacion = valorCalificacion.toFixed(1);
    }

    // === PRECIO ===
    const precioFormateado = juego.precio != null 
        ? `$${Number(juego.precio).toFixed(2)}` 
        : 'Precio no disponible';

    // === FECHA ===
    let fecha = 'Fecha no disponible';
    const fechaCampo = juego.fechalanzamiento || juego.fechaLanzamiento;
    if (fechaCampo) {
        const date = new Date(fechaCampo);
        if (!isNaN(date)) {
            fecha = date.toLocaleDateString('es-ES', {
                year: 'numeric',
                month: 'long',
                day: 'numeric'
            });
        }
    }

    // === CAMPOS ANIDADOS (ya funcionando) ===
    const estudioNombre = juego.estudio?.nombre || 'Desconocido';
    const generoNombre = juego.genero?.nombre || 'N/A';
    const plataformaNombre = juego.plataforma?.nombre || 'N/A';
    const descripcion = juego.descripcion || 'Sin descripción disponible';
    const id = juego.idjuego;

    return `
        <div class="api-game-card" data-id="${id}">
            <div class="game-image-container">
                <img src="${imagenUrl}" 
                     alt="${juego.titulo}" 
                     class="game-image"
                     onerror="this.src='https://via.placeholder.com/300x400/1f1f1f/4f46e5?text=${encodeURIComponent(juego.titulo)}'">
                <div class="game-rating-badge">
                    <span class="stars">★</span>
                    <span class="score-yellow">${calificacion}</span>
                </div>
            </div>
            
            <div class="game-card-content">
                <h2>${juego.titulo}</h2>
                
                <div class="game-details">
                    <p class="details-text"><strong>Estudio:</strong> ${estudioNombre}</p>
                    <p class="details-text"><strong>Género:</strong> ${generoNombre}</p>
                    <p class="details-text"><strong>Plataforma:</strong> ${plataformaNombre}</p>
                    <p class="details-text"><strong>Lanzamiento:</strong> ${fecha}</p>
                </div>
                
                <p class="description-text">${descripcion}</p>
                
                <div class="game-footer">
                    <span class="game-price">${precioFormateado}</span>
                    <button class="btn-ver-mas" onclick="verDetallesJuego(${id})">
                        Ver más
                    </button>
                </div>
            </div>
        </div>
    `;
}

/**
 * Obtiene una imagen por defecto basada en el título del juego
 */
function obtenerImagenPorDefecto(titulo) {
    const imagenesJuegos = {
        // 🔥 TUS JUEGOS DE LA BASE DE DATOS (10 juegos)
        'Elden Ring': 'https://image.api.playstation.com/vulcan/ap/rnd/202110/2000/phvVT0qZfcRms5qDAk0SI3CM.png',
        'Baldur\'s Gate 3': 'https://image.api.playstation.com/vulcan/ap/rnd/202302/2321/3098481c9164bb5f33069b37e49fba1a572ea3b0.jpg',
        'Cyberpunk 2077': 'https://image.api.playstation.com/vulcan/ap/rnd/202111/3013/cKZ4tKNFj9C00giTzYtH8PF1.png',
        'The Legend of Zelda: Tears of the Kingdom': 'https://assets.nintendo.com/image/upload/f_auto/q_auto/dpr_2.0/c_scale,w_400/ncom/software/switch/70010000063714/4f8b4a393e79ca2cbe00d56b28f86042e6a2e55e',
        'Stardew Valley': 'https://cdn.cloudflare.steamstatic.com/steam/apps/413150/header.jpg',
        'Helldivers 2': 'https://image.api.playstation.com/vulcan/ap/rnd/202401/1018/PVElhYY8XbI8W9M7v8Y5l5mX.png',
        'Final Fantasy XVI': 'https://image.api.playstation.com/vulcan/ap/rnd/202304/1819/Bwe7t9q7a9J5f8iQd5kT1q2R.png',
        'The Witcher 3: Wild Hunt': 'https://image.api.playstation.com/vulcan/ap/rnd/202211/0711/kh4MUIuMmHlktOHar3lVl6rY.png',
        'Sekiro: Shadows Die Twice': 'https://image.api.playstation.com/vulcan/ap/rnd/202011/0515/BA7002121978175719d3d7a1f8b8b7c3e8f7c1d2.png',
        'Divinity: Original Sin 2': 'https://cdn.akamai.steamstatic.com/steam/apps/435150/header.jpg',

    };
    
    // Busca exacto o parcial (por si el título varía)
    for (const [nombreJuego, url] of Object.entries(imagenesJuegos)) {
        if (titulo.toLowerCase().includes(nombreJuego.toLowerCase().split(' ')[0]) || 
            titulo === nombreJuego) {
            return url;
        }
    }
    
    // Fallback placeholder personalizado
    return `https://via.placeholder.com/300x400/1f1f1f/4f46e5?text=${encodeURIComponent(titulo.substring(0, 15) + '...')}`;
}
/**
 * Ver detalles de un juego (puedes expandir esto)
 */
async function verDetallesJuego(id) {
    const juego = await obtenerJuegoPorId(id);
    if (juego) {
        alert(`Detalles de ${juego.titulo}\n\nCalificación: ${juego.calificacionprom}\nPrecio: $${juego.precio}\n\n${juego.descripcion}`);
        // Aquí puedes crear un modal o redirigir a una página de detalles
    }
}

// ============================================
// FUNCIONES DE UI
// ============================================

/**
 * Muestra/oculta el indicador de carga
 */
function mostrarCargando(mostrar) {
    const gamesGrid = document.getElementById('gamesGrid');
    
    if (mostrar) {
        gamesGrid.innerHTML = `
            <div class="loading-spinner">
                <div class="spinner"></div>
                <p>Cargando juegos...</p>
            </div>
        `;
    }
}

/**
 * Muestra un mensaje de error
 */
function mostrarError(mensaje) {
    const gamesGrid = document.getElementById('gamesGrid');
    gamesGrid.innerHTML = `
        <div class="error-message">
            <p>⚠️ ${mensaje}</p>
            <button class="btn-retry" onclick="cargarJuegos()">Reintentar</button>
        </div>
    `;
}

// ============================================
// INICIALIZACIÓN Y EVENT LISTENERS
// ============================================

// Cargar juegos al cargar la página
document.addEventListener('DOMContentLoaded', () => {
    cargarJuegos();
    
    // Configurar el buscador
    const searchInput = document.getElementById('searchInput');
    let searchTimeout;
    
    searchInput.addEventListener('input', (e) => {
        // Debounce: espera 500ms después de que el usuario deje de escribir
        clearTimeout(searchTimeout);
        searchTimeout = setTimeout(() => {
            buscarJuegos(e.target.value);
        }, 500);
    });
    
    // Prevenir envío del formulario si presionan Enter
    searchInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            e.preventDefault();
            buscarJuegos(e.target.value);
        }
    });
});

// ============================================
// FUNCIONES ADICIONALES ÚTILES
// ============================================

/**
 * Filtra juegos por género
 */
async function filtrarPorGenero(idGenero) {
    try {
        mostrarCargando(true);
        const response = await fetch(`${API_BASE_URL}/genero/${idGenero}`);
        
        if (!response.ok) {
            throw new Error(`Error HTTP: ${response.status}`);
        }
        
        const juegos = await response.json();
        mostrarJuegos(juegos);
        mostrarCargando(false);
    } catch (error) {
        console.error('Error al filtrar por género:', error);
        mostrarError('Error al filtrar juegos');
        mostrarCargando(false);
    }
}

/**
 * Filtra juegos por plataforma
 */
async function filtrarPorPlataforma(idPlataforma) {
    try {
        mostrarCargando(true);
        const response = await fetch(`${API_BASE_URL}/plataforma/${idPlataforma}`);
        
        if (!response.ok) {
            throw new Error(`Error HTTP: ${response.status}`);
        }
        
        const juegos = await response.json();
        mostrarJuegos(juegos);
        mostrarCargando(false);
    } catch (error) {
        console.error('Error al filtrar por plataforma:', error);
        mostrarError('Error al filtrar juegos');
        mostrarCargando(false);
    }
}