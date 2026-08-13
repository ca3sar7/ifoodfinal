// js/config.js — Configuração de rota da API e pasta base
if (typeof BASE_FOLDER === 'undefined') {
    var BASE_FOLDER = (function() {
        if (typeof window === 'undefined' || !window.location) return '';
        var p = String(window.location.pathname || '');
        if (p.includes('/ifood/quiz-clone')) return '/ifood/quiz-clone';
        if (p.includes('/ifood/')) return '/ifood';
        if (p.startsWith('/ifood')) return '/ifood';
        return '';
    })();
}

if (typeof API_BASE === 'undefined') {
    var API_BASE = BASE_FOLDER + '/api';
}

if (typeof window !== 'undefined') {
    window.BASE_FOLDER = BASE_FOLDER;
    window.API_BASE = API_BASE;
}
