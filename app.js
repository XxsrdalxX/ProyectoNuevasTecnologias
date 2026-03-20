// URL de la API de Spring Boot. 
// Apunta al puerto 8080, que es donde está corriendo el backend.
const JUEGOS_API_URL = "http://localhost:8080/api/juegos";

// Declaramos las variables fuera del ámbito de la función.
let contenedorPopularesDinamico; 
let contenedorJuegos;

/**
 * 🎯 Ejecuta la función de carga solo cuando todo el HTML esté listo.
 */
document.addEventListener('DOMContentLoaded', () => {
    // Obtenemos los contenedores DESPUÉS de que el DOM esté listo
    contenedorPopularesDinamico = document.getElementById('contenedor-populares-dinamico');
    contenedorJuegos = document.getElementById('contenedor-juegos');
    
    // Si el contenedor principal existe, iniciamos la carga
    if (contenedorJuegos) {
        cargarJuegos();
    } else {
        console.error("Error FATAL: No se encontró el contenedor con ID 'contenedor-juegos'.");
    }
});


/**
 * Función principal para cargar los datos de la API.
 */
async function cargarJuegos() {
    try {
        // Muestra el mensaje de carga mientras se realiza la petición
        contenedorJuegos.innerHTML = '<p class="text-xl text-center text-gray-500 mt-10">Cargando juegos de la API...</p>';
        if (contenedorPopularesDinamico) {
             contenedorPopularesDinamico.innerHTML = '<p class="text-center text-gray-500">Cargando destacados...</p>';
        }

        const response = await fetch(JUEGOS_API_URL);

        // Si la respuesta no es 200 OK, lanzamos un error
        if (!response.ok) {
            throw new Error(`Error en la red: ${response.status} ${response.statusText}`);
        }

        const juegos = await response.json();
        
        // ORDENA los juegos por calificación de mayor a menor.
        const juegosOrdenados = juegos.sort((a, b) => {
            const calA = a.calificacionProm || 0;
            const calB = b.calificacionProm || 0;
            return calB - calA;
        });

        // 1. Renderiza los 3 primeros en la sección de POPULARES/DESTACADOS
        renderizarJuegosDestacados(juegosOrdenados.slice(0, 3));
        
        // 2. Renderiza TODO el listado completo en el CATÁLOGO COMPLETO
        renderizarJuegos(juegosOrdenados); 

    } catch (error) {
        console.error("Error al obtener los datos de la API:", error);
        // Mensaje de error unificado para ambos contenedores
        const errorMessage = `
            <div class="text-center p-6 bg-red-900 border-l-4 border-red-500 text-red-200 mt-10 rounded-lg" role="alert">
                <p class="font-bold">Error de Conexión</p>
                <p>No se pudo conectar al servidor de Spring Boot en ${JUEGOS_API_URL}.</p>
                <p class="text-sm mt-2">Asegúrate de que el backend esté ejecutándose en el puerto 8080 y que no haya problemas de CORS.</p>
            </div>
        `;
        contenedorJuegos.innerHTML = errorMessage;
        if (contenedorPopularesDinamico) {
            contenedorPopularesDinamico.innerHTML = '';
        }
    }
}

/**
 * Renderiza una pequeña lista de juegos en el contenedor de Destacados.
 * NOTA: Esta sección usa clases de Tailwind directamente ya que es una presentación simple.
 * @param {Array<Object>} juegos - Lista de objetos de juego (ya ordenados).
 */
function renderizarJuegosDestacados(juegos) {
    if (!contenedorPopularesDinamico) return; // Si no existe el div, no hace nada

    if (juegos.length === 0) {
        contenedorPopularesDinamico.innerHTML = '<p class="text-xl text-center text-gray-500 mt-10">No hay juegos destacados disponibles.</p>';
        return;
    }

    const htmlDestacados = juegos.map(juego => {
        const calificacion = juego.calificacionProm ? juego.calificacionProm.toFixed(1) : 'N/A';
        return `
            <div class="p-4 bg-gray-900 rounded-lg shadow-xl border border-indigo-700/50 transform hover:scale-[1.05] transition duration-300">
                <h3 class="text-indigo-400 font-bold text-lg truncate">${juego.titulo}</h3>
                <p class="text-xs text-gray-400 mb-2">${juego.fechaLanzamiento}</p>
                <span class="bg-indigo-600 text-white font-bold px-2 py-0.5 rounded-full text-sm">
                    ⭐ ${calificacion}
                </span>
            </div>
        `;
    }).join('');

    // Ajustamos la presentación para que parezca un grid en esa sección
    contenedorPopularesDinamico.innerHTML = `<div class="mt-6 mb-12 grid grid-cols-1 md:grid-cols-3 gap-6">${htmlDestacados}</div>`;
}


/**
 * Renderiza las tarjetas de juego en el contenedor HTML (Catálogo Completo).
 * NOTA: Esta sección usa CLASES DE styles.css (api-game-card, resena-item, etc.).
 * @param {Array<Object>} juegos - Lista de objetos de juego de la API.
 */
function renderizarJuegos(juegos) {
    if (!contenedorJuegos) return;

    if (juegos.length === 0) {
        contenedorJuegos.innerHTML = '<p class="text-xl text-center text-gray-500 mt-10">No se encontraron juegos.</p>';
        return;
    }

    // Usamos map para crear un array de cadenas HTML y luego join para unirlas
    const htmlJuegos = juegos.map(juego => {
        // Calcula la calificación (usa 0.0 si es null)
        const calificacion = juego.calificacionProm ? juego.calificacionProm.toFixed(1) : 'N/A';
        const precio = juego.precio ? `$${juego.precio.toFixed(2)}` : 'Gratis';
        
        // Construye el HTML para las reseñas
        // CLASES DE styles.css
        const htmlResenas = juego.resenas.map(resena => `
            <div class="resena-item">
                <p class="score-yellow">${resena.puntuacion}/10</p>
                <p class="italic">${resena.comentario}</p>
            </div>
        `).join('');

        return `
            <!-- CLASE DE styles.css: .api-game-card -->
            <div class="api-game-card">
                <div class="p-6">
                    <!-- Título y Calificación -->
                    <div class="flex justify-between items-start mb-4">
                        <!-- CLASE DE styles.css: .api-game-card-title -->
                        <h2 class="api-game-card-title">${juego.titulo}</h2>
                        <!-- Mantenemos Tailwind para la insignia (badge) de calificación -->
                        <span class="bg-indigo-600 text-white text-xl font-bold px-3 py-1 rounded-full shadow-lg">
                            ⭐ ${calificacion}
                        </span>
                    </div>

                    <!-- Detalles -->
                    <!-- CLASES DE styles.css: .details-text, .description-text -->
                    <p class="details-text mb-4">${juego.fechaLanzamiento}</p>
                    <p class="description-text mb-6 line-clamp-3">${juego.descripcion}</p>

                    <!-- Precio (Mantenemos Tailwind para el botón de precio) -->
                    <div class="text-center bg-green-500 text-white font-bold py-2 rounded-lg mb-4 shadow-md">
                        ${precio}
                    </div>

                    <!-- Reseñas -->
                    <!-- CLASE DE styles.css: .resena-subtitle -->
                    <h3 class="resena-subtitle pb-1 mb-2">Reseñas (${juego.resenas.length})</h3>
                    <div class="max-h-32 overflow-y-auto space-y-2">
                        ${juego.resenas.length > 0 ? htmlResenas : '<p class="text-sm text-gray-500">Sin reseñas aún.</p>'}
                    </div>

                </div>
            </div>
        `;
    }).join(''); // Unimos todos los strings HTML generados

    // CORRECCIÓN: Aplicamos las clases de GRID al contenedor principal.
    contenedorJuegos.innerHTML = `<div class="mt-6 mb-12 grid grid-cols-1 md:grid-cols-3 lg:grid-cols-4 gap-8">${htmlJuegos}</div>`;
}