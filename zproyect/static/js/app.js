/* ════════════════════════════════════════════════════════════════════════
   app.js — Calculadora de Traslados Académicos
   Conecta el formulario HTML con la API REST de Flask.
   ════════════════════════════════════════════════════════════════════════ */

(() => {
  'use strict';

  // ── Estado ──────────────────────────────────────────────────────────────
  let ciclos = [];          // lista cargada desde /api/ciclos
  let lastResult = null;    // último resultado calculado (para copiar)

  // ── Elementos DOM ────────────────────────────────────────────────────────
  const form         = document.getElementById('calculadora-form');
  const btnCalc      = document.getElementById('btn-calcular');
  const resSec       = document.getElementById('resultado-section');
  const errToast     = document.getElementById('error-toast');
  const errMsg       = document.getElementById('error-msg');
  const resCard      = document.getElementById('resultado-card');
  const estadoBadge  = document.getElementById('estado-badge');
  const resMensaje   = document.getElementById('resultado-mensaje');
  const montoSaldo   = document.getElementById('monto-saldo');
  const montoCosto   = document.getElementById('monto-costo');
  const montoDiff    = document.getElementById('monto-diff');
  const desgloseTog  = document.getElementById('desglose-toggle');
  const desgloseBody = document.getElementById('desglose-body');
  const desgloseTbod = document.getElementById('desglose-tbody');
  const btnCopy      = document.getElementById('btn-copy');

  // Selects dinámicos
  const origenNombre   = document.getElementById('origen_nombre');
  const origenUniv     = document.getElementById('origen_universidad');
  const origenMod      = document.getElementById('origen_modalidad');
  const destinoNombre  = document.getElementById('destino_nombre');
  const destinoUniv    = document.getElementById('destino_universidad');
  const destinoMod     = document.getElementById('destino_modalidad');

  // ── Helpers ──────────────────────────────────────────────────────────────
  const fmt = (n) => `S/ ${parseFloat(n).toFixed(2).replace(/\B(?=(\d{3})+(?!\d))/g, ',')}`;

  function setLoading(on) {
    btnCalc.classList.toggle('loading', on);
    btnCalc.disabled = on;
  }

  function hideAll() {
    resSec.classList.add('hidden');
    errToast.classList.add('hidden');
    resCard.classList.add('hidden');
  }

  function showError(msg) {
    errMsg.textContent = msg;
    errToast.classList.remove('hidden');
    resCard.classList.add('hidden');
    resSec.classList.remove('hidden');
    resSec.scrollIntoView({ behavior: 'smooth', block: 'start' });
  }

  function populateSelect(select, options, placeholder) {
    const current = select.value;
    select.innerHTML = `<option value="">${placeholder}</option>`;
    options.forEach(opt => {
      const el = document.createElement('option');
      el.value = opt;
      el.textContent = opt;
      if (opt === current) el.selected = true;
      select.appendChild(el);
    });
  }

  // ── Cascada de selects ─────────────────────────────────────────────────
  function unique(arr) { return [...new Set(arr)].sort(); }

  function updateOrigenSelects() {
    const ciclosOrigen = ciclos; // todos disponibles
    const nombres = unique(ciclosOrigen.map(c => c.nombre));
    populateSelect(origenNombre, nombres, '— Selecciona ciclo —');
    updateOrigenUnivMod();
  }

  function updateOrigenUnivMod() {
    const nombre = origenNombre.value;
    const filtered = nombre ? ciclos.filter(c => c.nombre === nombre) : ciclos;
    const univs = unique(filtered.map(c => c.universidad));
    populateSelect(origenUniv, univs, '— Universidad —');
    updateOrigenMod();
  }

  function updateOrigenMod() {
    const nombre = origenNombre.value;
    const univ   = origenUniv.value;
    const filtered = ciclos.filter(c =>
      (!nombre || c.nombre === nombre) &&
      (!univ   || c.universidad === univ)
    );
    const mods = unique(filtered.map(c => c.modalidad));
    populateSelect(origenMod, mods, '— Modalidad —');
  }

  function updateDestinoSelects() {
    const nombres = unique(ciclos.map(c => c.nombre));
    populateSelect(destinoNombre, nombres, '— Selecciona ciclo —');
    updateDestinoUnivMod();
  }

  function updateDestinoUnivMod() {
    const nombre = destinoNombre.value;
    const filtered = nombre ? ciclos.filter(c => c.nombre === nombre) : ciclos;
    const univs = unique(filtered.map(c => c.universidad));
    populateSelect(destinoUniv, univs, '— Universidad —');
    updateDestinoMod();
  }

  function updateDestinoMod() {
    const nombre = destinoNombre.value;
    const univ   = destinoUniv.value;
    const filtered = ciclos.filter(c =>
      (!nombre || c.nombre === nombre) &&
      (!univ   || c.universidad === univ)
    );
    const mods = unique(filtered.map(c => c.modalidad));
    populateSelect(destinoMod, mods, '— Modalidad —');
  }

  // ── Cargar ciclos desde la API ─────────────────────────────────────────
  async function cargarCiclos() {
    try {
      const res = await fetch('/api/ciclos');
      const json = await res.json();
      if (json.success) {
        ciclos = json.ciclos;
        updateOrigenSelects();
        updateDestinoSelects();
      }
    } catch (e) {
      console.warn('No se pudieron cargar los ciclos:', e);
    }
  }

  // ── Eventos de cascada ─────────────────────────────────────────────────
  origenNombre.addEventListener('change', () => { updateOrigenUnivMod(); });
  origenUniv.addEventListener('change',   () => { updateOrigenMod(); });
  destinoNombre.addEventListener('change', () => { updateDestinoUnivMod(); });
  destinoUniv.addEventListener('change',   () => { updateDestinoMod(); });

  // ── Desglose toggle ────────────────────────────────────────────────────
  desgloseTog.addEventListener('click', () => {
    const open = desgloseTog.classList.toggle('open');
    desgloseBody.classList.toggle('open', open);
    desgloseTog.setAttribute('aria-expanded', String(open));
  });
  desgloseTog.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); desgloseTog.click(); }
  });

  // ── Mostrar resultado ──────────────────────────────────────────────────
  function mostrarResultado(resultado) {
    const r = resultado;
    lastResult = r;

    // Estado badge
    const claseMap = {
      SALDO_A_FAVOR:     'success',
      TRASLADO_CUBIERTO: 'warning',
      MONTO_PENDIENTE:   'danger',
    };
    const iconMap = {
      SALDO_A_FAVOR:     '✓ Saldo a favor',
      TRASLADO_CUBIERTO: '= Cubierto',
      MONTO_PENDIENTE:   '! Monto pendiente',
    };
    const clase = claseMap[r.estado] || 'warning';
    estadoBadge.className = `estado-badge ${clase}`;
    estadoBadge.textContent = iconMap[r.estado] || r.estado;

    // Mensaje principal
    resMensaje.textContent = r.mensaje;
    resMensaje.className = `resultado-mensaje text-${clase}`;

    // Montos
    montoSaldo.textContent = fmt(r.saldo_origen);
    montoSaldo.className   = 'monto-valor';
    montoCosto.textContent = fmt(r.costo_destino);
    montoCosto.className   = 'monto-valor';

    const diff = parseFloat(r.diferencia);
    montoDiff.textContent = fmt(Math.abs(diff));
    montoDiff.className   = `monto-valor ${diff >= 0 ? 'text-success' : 'text-danger'}`;

    // Estilo tarjeta
    resCard.className = `resultado-card ${clase}`;

    // Desglose
    const det = r.detalle || {};
    const orig = det.origen || {};
    const dest = det.destino || {};

    const filas = [
      ['Semanas totales del ciclo', orig.semanas_totales ?? '—', dest.semanas_totales ?? '—'],
      ['Semanas consumidas',        orig.semanas_consumidas ?? '—', dest.semanas_consumidas ?? '—'],
      ['Semanas restantes',         orig.semanas_restantes ?? '—', dest.semanas_restantes ?? '—'],
      ['Saldo / Costo calculado',   fmt(r.saldo_origen), fmt(r.costo_destino)],
    ];

    desgloseTbod.innerHTML = filas
      .map(([c, o, d]) =>
        `<tr><td>${c}</td><td>${o}</td><td>${d}</td></tr>`
      )
      .join('');

    // Reset toggle
    desgloseTog.classList.remove('open');
    desgloseBody.classList.remove('open');
    desgloseTog.setAttribute('aria-expanded', 'false');

    resCard.classList.remove('hidden');
    errToast.classList.add('hidden');
    resSec.classList.remove('hidden');
    resSec.scrollIntoView({ behavior: 'smooth', block: 'start' });
  }

  // ── Submit ──────────────────────────────────────────────────────────────
  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    hideAll();
    setLoading(true);

    const fd = (id) => document.getElementById(id).value.trim();

    // Convertir fecha de YYYY-MM-DD a DD/MM/YYYY
    const fechaRaw = fd('fecha_traslado');
    let fechaStr = fechaRaw;
    if (fechaRaw && fechaRaw.includes('-')) {
      const [y, m, d] = fechaRaw.split('-');
      fechaStr = `${d}/${m}/${y}`;
    }

    const payload = {
      fecha_traslado: fechaStr,
      origen: {
        nombre:              fd('origen_nombre'),
        universidad:         fd('origen_universidad'),
        modalidad_academica: fd('origen_modalidad'),
        pago_en:             fd('origen_pago'),
      },
      destino: {
        nombre:              fd('destino_nombre'),
        universidad:         fd('destino_universidad'),
        modalidad_academica: fd('destino_modalidad'),
        pago_en:             fd('destino_pago'),
      },
    };

    // Validación client-side rápida
    const campos = [
      ['fecha_traslado', 'Fecha de traslado'],
      ['origen.nombre', 'Ciclo origen'],
      ['origen.universidad', 'Universidad origen'],
      ['origen.modalidad_academica', 'Modalidad origen'],
      ['origen.pago_en', 'Condición de pago origen'],
      ['destino.nombre', 'Ciclo destino'],
      ['destino.universidad', 'Universidad destino'],
      ['destino.modalidad_academica', 'Modalidad destino'],
      ['destino.pago_en', 'Condición de pago destino'],
    ];

    for (const [ruta, nombre] of campos) {
      const val = ruta.includes('.')
        ? payload[ruta.split('.')[0]][ruta.split('.')[1]]
        : payload[ruta];
      if (!val) {
        setLoading(false);
        showError(`Por favor completa el campo: ${nombre}`);
        return;
      }
    }

    try {
      const res  = await fetch('/api/traslados/calcular', {
        method:  'POST',
        headers: { 'Content-Type': 'application/json' },
        body:    JSON.stringify(payload),
      });
      const json = await res.json();

      if (json.success && json.resultado) {
        mostrarResultado(json.resultado);
      } else {
        showError(json.error || 'Error desconocido al calcular el traslado.');
      }
    } catch (err) {
      showError('Error de conexión con el servidor. Verifica que la aplicación esté corriendo.');
    } finally {
      setLoading(false);
    }
  });

  // ── Copiar resumen ─────────────────────────────────────────────────────
  btnCopy.addEventListener('click', () => {
    if (!lastResult) return;
    const r = lastResult;
    const det = r.detalle || {};
    const o = det.origen || {};
    const d = det.destino || {};

    const texto = [
      '=== RESUMEN DE TRASLADO ACADÉMICO ===',
      '',
      `Estado: ${r.estado}`,
      `Resultado: ${r.mensaje}`,
      '',
      '--- MONTOS ---',
      `Saldo disponible (origen): ${fmt(r.saldo_origen)}`,
      `Costo del ciclo destino:   ${fmt(r.costo_destino)}`,
      `Diferencia:                ${fmt(r.diferencia)}`,
      '',
      '--- DESGLOSE ORIGEN ---',
      `Semanas totales:     ${o.semanas_totales ?? '—'}`,
      `Semanas consumidas:  ${o.semanas_consumidas ?? '—'}`,
      `Semanas restantes:   ${o.semanas_restantes ?? '—'}`,
      '',
      '--- DESGLOSE DESTINO ---',
      `Semanas totales:     ${d.semanas_totales ?? '—'}`,
      `Semanas consumidas:  ${d.semanas_consumidas ?? '—'}`,
      `Semanas restantes:   ${d.semanas_restantes ?? '—'}`,
      '',
      `Generado: ${new Date().toLocaleString('es-PE')}`,
    ].join('\n');

    navigator.clipboard.writeText(texto).then(() => {
      btnCopy.classList.add('copied');
      btnCopy.querySelector('svg + *') // texto del botón
      btnCopy.innerHTML = `
        <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 12 4 10"/><path d="M4 10l-2 2 5 5 13-13"/></svg>
        ¡Copiado!`;
      setTimeout(() => {
        btnCopy.classList.remove('copied');
        btnCopy.innerHTML = `
          <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/></svg>
          Copiar resumen`;
      }, 2000);
    }).catch(() => {
      alert('No se pudo copiar al portapapeles. Copia el texto manualmente desde el desglose.');
    });
  });

  // ── Inicializar ────────────────────────────────────────────────────────
  cargarCiclos();

})();
