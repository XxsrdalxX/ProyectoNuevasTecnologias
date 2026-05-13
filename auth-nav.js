/**
 * auth-nav.js — Estado de sesión en la barra de navegación.
 * Incluir este script en todas las páginas antes del </body>.
 * Requiere un elemento <div id="nav-auth"></div> en el navbar.
 */
(function () {
    function getUser() {
        try { return JSON.parse(localStorage.getItem('gr_user')); } catch { return null; }
    }

    function esc(s) {
        return String(s || '').replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
    }

    function cerrarSesion() {
        localStorage.removeItem('gr_token');
        localStorage.removeItem('gr_user');
        window.location.href = 'index.html';
    }

    // Exponer para uso en botones inline
    window.cerrarSesion = cerrarSesion;

    document.addEventListener('DOMContentLoaded', function () {
        const nav = document.getElementById('nav-auth');
        if (!nav) return;

        const u = getUser();
        if (u) {
            const rolBadge = u.rol === 'admin'
                ? '<span style="background:#7c3aed;color:#fff;padding:0.15rem 0.5rem;border-radius:99px;font-size:0.7rem;font-weight:700;margin-left:0.4rem;">ADMIN</span>'
                : '';
            nav.innerHTML = `
                <span style="color:#c4b5fd;font-weight:600;font-size:0.9rem;">
                    ${esc(u.nombre)}${rolBadge}
                </span>
                <button onclick="cerrarSesion()"
                    style="background:#ef4444;color:#fff;padding:0.4rem 0.9rem;border-radius:6px;border:none;cursor:pointer;font-weight:600;font-size:0.85rem;">
                    Cerrar sesión
                </button>
            `;
        } else {
            nav.innerHTML = `
                <a href="login.html"
                    style="background:#4f46e5;color:#fff;padding:0.4rem 0.9rem;border-radius:6px;font-weight:600;font-size:0.85rem;text-decoration:none;">
                    Iniciar sesión
                </a>
                <a href="registro.html"
                    style="background:#6b7280;color:#fff;padding:0.4rem 0.9rem;border-radius:6px;font-weight:600;font-size:0.85rem;text-decoration:none;">
                    Registrarse
                </a>
            `;
        }
    });
})();
