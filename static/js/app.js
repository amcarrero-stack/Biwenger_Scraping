let usuariosData = [];

async function loadUsuarios() {
    const res = await fetch("/api/usuarios");
    const usuarios = await res.json();
    usuariosData = usuarios; // Guardamos para no pedir otra vez
    const select = document.getElementById("usuarioSelect");
    usuarios.forEach(u => {
        const option = document.createElement("option");
        option.value = u.id;
        option.textContent = u.name;
        select.appendChild(option);
    });
    select.addEventListener("change", () => {
        loadCards();
        showTab('plantilla'); // siempre mostrar Plantilla al cambiar usuario
    });
}

async function loadCards() {
    const usuarioId = document.getElementById("usuarioSelect").value;
    if (!usuarioId) return;

    const usuario = usuariosData.find(u => u.id == usuarioId);

    // Traer jugadores
    const res = await fetch(`/api/jugadores/${usuarioId}`);
    const jugadores = await res.json();

    const container = document.getElementById("tabContent");
    container.innerHTML = "";

    // Plantilla
    const plantillaCard = document.createElement("div");
    plantillaCard.id = "plantilla";
    plantillaCard.className = "tab-card bg-green-800 rounded-lg p-4";
    plantillaCard.innerHTML = `<h2 class='text-xl font-bold mb-2'>Plantilla (${usuario?.num_jugadores ?? 0} jugadores)</h2>`;
    jugadores.forEach(j => {
        const jugadorDiv = document.createElement("div");
        jugadorDiv.className = "bg-gray-700 p-2 rounded mb-1";
        jugadorDiv.textContent = `${j.nombre} - ${j.equipo} - ${j.posicion} - ${j.valor}`;
        plantillaCard.appendChild(jugadorDiv);
    });
    container.appendChild(plantillaCard);

    // Saldo
    const saldoCard = document.createElement("div");
    saldoCard.id = "saldo";
    saldoCard.className = "tab-card bg-gray-800 rounded-lg p-4 hidden";
    const saldoFormateado = new Intl.NumberFormat('es-ES', {
        style: 'currency',
        currency: 'EUR'
    }).format(usuario?.saldo ?? 0);
    saldoCard.innerHTML = `<h2 class="text-lg font-bold">Saldo: ${saldoFormateado}</h2>`;
    container.appendChild(saldoCard);

    // Movimientos
    const movimientosCard = document.createElement("div");
    movimientosCard.id = "movimientos";
    movimientosCard.className = "tab-card hidden flex flex-col items-center"; // contenedor flex centrado
    movimientosCard.innerHTML = "<h2 class='text-xl font-bold mb-2'>Movimientos</h2>";
    container.appendChild(movimientosCard);

    // Traer movimientos del usuario
    const resMov = await fetch(`/api/movimientos/${usuarioId}`);
    const movimientos = await resMov.json();
    if (movimientos.length === 0) {
        const p = document.createElement("p");
        p.textContent = "No hay movimientos registrados.";
        p.className = "text-gray-300";
        movimientosCard.appendChild(p);
    } else {
        movimientos.forEach(m => {
            let tipo = m.tipo?.toUpperCase() ?? '';
            let jugador = m.jugador;
            let importe = m.cantidad;
            let fecha = m.fecha;
            if (tipo !== 'ABONO' && tipo !== 'PENALIZACION' && tipo !== 'CAMBIONOMBRE') {
                const movDiv = document.createElement("div");
                movDiv.className = "bg-gray-700 p-4 rounded mb-2 w-full max-w-xl"; // max-w-xl centra y limita tamaño
                let importeFormateado = importe
                    ? new Intl.NumberFormat('es-ES', { style: 'currency', currency: 'EUR' }).format(importe)
                    : '';
                movDiv.innerHTML = `
                    <p><strong>Tipo:</strong> ${tipo}</p>
                    <p><strong>Jugador:</strong> ${jugador ?? '-'}</p>
                    <p><strong>Importe:</strong> ${importeFormateado}</p>
                    <p><strong>Fecha:</strong> ${fecha ?? '-'}</p>
                `;
                movimientosCard.appendChild(movDiv);
            }
        });
    }

    // Estadísticas
    const estadisticasCard = document.createElement("div");
    estadisticasCard.id = "estadisticas";
    estadisticasCard.className = "tab-card bg-gray-700 rounded-lg p-4 hidden";
    estadisticasCard.innerHTML = "<h2 class='text-xl font-bold'>Estadísticas</h2><p>Próximamente...</p>";
    container.appendChild(estadisticasCard);
}

function showTab(tabName) {
    document.querySelectorAll('.tab-card').forEach(card => {
        card.classList.add('hidden');
    });
    const active = document.getElementById(tabName);
    if (active) active.classList.remove('hidden');
}

// Event listeners tabs
document.querySelectorAll('.tab-btn').forEach(btn => {
    btn.addEventListener('click', () => {
        showTab(btn.dataset.tab);
    });
});

loadUsuarios();
