# -*- coding: utf-8 -*-
"""
PREDWEEM Lolium — San Pedro.

La página muestra la alerta de grandes flujos de Lolium del paquete ``lolium-comun`` (probabilidad de gran flujo en
los próximos 7 días, qué hacer esta semana, ventana del graminicida de barbecho, residual a la siembra y flujos tardíos)
con el clima diario del repositorio (``meteo_daily.csv``).

El motor PREDWEEM anterior (red neuronal y balance hídrico, ``app_emergencia_core.py`` y sus modelos) ya no se
ejecuta: su inicio estimado de la emergencia erró 12–14 días en promedio y no mejoraba la alerta. Sus archivos quedan
en el repositorio solo como referencia.
"""
import importlib
from pathlib import Path

import pandas as pd
import streamlit as st

# Control de acceso (ingreso con Google y usuarios aprobados). Inactivo hasta configurar los secretos [acceso] y [auth].
from acceso_predweem import mostrar_sesion, requerir_acceso
from lolium_comun import pagina

BASE = Path(__file__).resolve().parent

requerir_acceso("San Pedro")
pagina.encabezado("🌾 PREDWEEM LOLIUM — SAN PEDRO (BA) lat=-33.7328 lon=-59.7965", "PREDWEEM SAN PEDRO")
parametros = pagina.barra_lateral(BASE, "San Pedro")
meteo = pagina.cargar_meteo(BASE, None)

NOTA_SAN_PEDRO = (
    "**Validación en San Pedro.** La alerta se probó, sin reajustarla, con los conteos de "
    "San Pedro publicados en el gemelo digital: 2023 y 2024 (clima del ensayo) y 2026 (clima de esta app); 30 intervalos "
    "entre conteos, 6 con emergencia ≥ 5 % de la campaña por semana. Emitida al comienzo de cada intervalo, la alerta "
    "separó los intervalos con gran flujo con AUC 0,79 solo con clima, 0,83 con la fecha de primeras plántulas y 0,85 con "
    "conteos (gemelo de San Pedro: 0,58). Con primeras plántulas, 5 de los 6 grandes flujos quedaron en *Alerta*; también 6 "
    "de los 24 intervalos sin gran flujo.\n\n"
    "**Límites en San Pedro.** Tres campañas y pocos grandes flujos. La emergencia varía mucho entre años: 50 % al 19/02 en "
    "2026, al 14/04 en 2024 y al 03/05 en 2023. En 2026 el primer gran flujo (01/02–21/02, 59 % de la campaña) no se "
    "anticipó al 01/02: todavía no había lluvia registrada que lo explicara. Después de los grandes grandes flujos de 2026 "
    "la alerta siguió alta sin emergencia (21/02 y 04/04), por agotamiento del banco; un factor de agotamiento no "
    "mejoró de forma clara la alerta con tan pocas campañas. La curva acumulada es el calendario de referencia regional: un "
    "calendario propio de San Pedro no la mejoró. La alerta con conteos está calibrada con conteos semanales: con "
    "recorridas cada 2–3 semanas, conviene usar sobre todo la fecha de primeras plántulas."
)


_resultados_alerta = None
if meteo is not None and not meteo.empty:
    try:
        import alerta_lolmu as _alerta_lolmu
        import visualizacion_alerta_lolmu as _vis_alerta

        # Streamlit conserva en memoria los módulos ya importados entre ejecuciones: tras una actualización del
        # repositorio, recargarlos evita usar una versión vieja
        importlib.reload(_alerta_lolmu)
        importlib.reload(_vis_alerta)
        _resultados_alerta = _vis_alerta.mostrar_alerta_lolmu(
            meteo,
            **parametros,
    tope_hasta_ultimo_cero=True,  # semanas ya cerradas por un conteo posterior en cero: probabilidad 0
    curva_desde_ultimo_cero=True,  # la curva acumulada arranca a mitad de camino entre el último cero y el primer conteo con plántulas
    curva_tiempo_termico=True,  # con primeras plántulas, curva acumulada en tiempo térmico desde esa fecha
    localidad="San Pedro",
    nota_sitio=NOTA_SAN_PEDRO,
        )
    except Exception as _error_alerta:  # noqa: BLE001
        st.warning(f"No se pudo calcular la alerta: {_error_alerta}")

pagina.descarga_excel(_resultados_alerta, "San_Pedro", "descarga_excel_resultados_final_san_pedro")
mostrar_sesion()
