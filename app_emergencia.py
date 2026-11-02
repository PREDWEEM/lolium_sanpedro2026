# -*- coding: utf-8 -*-
"""Punto de entrada de PREDWEEM San Pedro 2026.

La aplicación base se conserva en ``app_emergencia_core.py`` para auditoría. Antes de compilarla:

* se aplica la parametrización local congelada obtenida con las campañas completas 2025–2026 (respuesta
  termohídrica continua y agotamiento causal de cohorte; ``sanpedro_calibracion_final.py``). La ANN original no se
  modifica;
* se retiran de la página los elementos que reemplaza la alerta de flushes del final: la sección "Datos del lote"
  (se usa el clima SIGA/ECMWF del repositorio y la cobertura calibrada), el mapa de riesgo, las pestañas (Monitor de
  decisión, Precipitaciones y suelo, Análisis estratégico, Bio-calibración), el reporte del motor, la imagen de fondo
  (reemplazada por un fondo liso claro) y, en la barra lateral, los parámetros del motor (quedan en sus valores
  congelados) y el calibrador; la barra lateral conserva los parámetros de la ventana de control.

El motor sigue calculando como antes: su primer pico validado se usa como inicio estimado del reloj térmico hasta que
se informa la fecha de las primeras plántulas. La alerta (``alerta_lolmu.py``) es la calibrada con 17 campañas de
Bordenave y validada con los conteos de San Pedro 2023, 2024 y 2026.
"""
import io
from pathlib import Path

import pandas as pd

from visualizacion_horizonte_pronostico import mostrar_horizonte_pronostico
from visualizacion_intensidad_relativa import parchear_visualizacion_intensidad_relativa
from sanpedro_calibracion_final import (
    ALPHA_HIDRICA_FINAL,
    CALIBRACION,
    CHOQUE_HIDRICO_FINAL,
    COBERTURA_FINAL,
    ESCALA_LLUVIA_TH_FINAL,
    EXPONENTE_KR_FINAL,
    K_COHORTE_FINAL,
    PENDIENTE_TERMOHIDRICA_FINAL,
    T0_TERMOHIDRICO_FINAL,
    VENTANA_TERMOHIDRICA_FINAL,
    VERSION_MOTOR,
    WMAX_FINAL,
    aplicar_agotamiento_cohorte,
    aplicar_interaccion_termohidrica,
    parchear_core_sanpedro,
)

_CORE_APP = Path(__file__).with_name("app_emergencia_core.py")
_core_source = _CORE_APP.read_text(encoding="utf-8")
_core_source = parchear_core_sanpedro(_core_source)
_core_source = parchear_visualizacion_intensidad_relativa(_core_source)


def _reemplazar(origen: str, viejo: str, nuevo: str) -> str:
    if viejo not in origen:
        raise RuntimeError(f"No se encontró el bloque a reemplazar en el motor: {viejo[:70]!r}")
    return origen.replace(viejo, nuevo, 1)


def _cortar(origen: str, desde: str, hasta: str | None, nuevo: str) -> str:
    """Reemplaza el tramo [desde, hasta) del motor (hasta el final si ``hasta`` es None)."""
    ini = origen.find(desde)
    fin = len(origen) if hasta is None else origen.find(hasta, ini)
    if ini < 0 or fin < ini:
        raise RuntimeError(f"No se encontró el tramo a retirar del motor: {desde[:70]!r}")
    return origen[:ini] + nuevo + origen[fin:]


_FONDO_CSS = """<style>
.stApp { background: #f4f6f3; }
[data-testid="stAppViewContainer"] > .main, [data-testid="stMain"] { background: transparent; }
[data-testid="stSidebar"] { background-color: #e8f3ea; border-right: 1px solid #cfe3d3; }
[data-testid="stSidebar"] .stMarkdown, [data-testid="stSidebar"] p, [data-testid="stSidebar"] label { color: #14532d !important; }
[data-testid="stCaptionContainer"], .stCaption { color: #4b5563 !important; }
h1, h2, h3, h4 { color: #1f2937; }
</style>"""

# fondo liso claro en lugar de la imagen de plantas (mejor contraste)
_core_source = _reemplazar(_core_source, 'set_bg_hack("fondo_predweem_v3.png")', "st.markdown(_FONDO_CSS, unsafe_allow_html=True)")
# la regla "header {visibility: hidden;}" ocultaba también el encabezado de los calendarios desplegables
_core_source = _reemplazar(_core_source, "    header {visibility: hidden;}", '    header[data-testid="stHeader"] {visibility: hidden;}')

# "Datos del lote": clima del repositorio, sin conteos del formato anterior y cobertura calibrada
_core_source = _cortar(_core_source, 'with st.expander("📂 1. Datos del Lote", expanded=True):', "# --- SIDEBAR ---", '''cobertura_pct = float(COBERTURA_FINAL)
ke_val, mod_termico = parametros_superficie(cobertura_pct)
df_meteo_raw = load_data(None, "meteo_daily")
df_campo_raw = None

''')

# barra lateral: solo la ventana de control; parámetros del motor en sus valores congelados 2025–2026
_core_source = _cortar(_core_source, 'st.sidebar.markdown("## ⚙️ 2. Fisiología y Logística")',
                       "# ---------------------------------------------------------\n# 6. MOTOR DE CÁLCULO", '''st.sidebar.markdown("## ⚙️ Ventana de control")
st.sidebar.caption("Tiempo térmico sobre la temperatura media del aire y objetivos de la ventana post-emergente.")
col_t1, col_t2 = st.sidebar.columns(2)
with col_t1: t_base_val = st.number_input("T Base", value=2.0, step=0.5)
with col_t2: t_opt_max = st.number_input("T Óptima Max", value=20.0, step=1.0)
t_critica = st.sidebar.slider("T Crítica (Stop)", 26.0, 42.0, 30.0)
st.sidebar.markdown("**Objetivos (°Cd)**")
dga_optimo = st.sidebar.number_input("TT Control Post-emergente (°Cd)", value=600, step=10)
dga_critico = st.sidebar.number_input("Límite Ventana (°Cd)", value=800, step=10)

# parámetros del motor PREDWEEM San Pedro en sus valores congelados (controles retirados de la página)
umbral_er = 0.0001
umbral_termoinhibicion = float(T0_TERMOHIDRICO_FINAL)
umbral_choque_hidrico = float(CHOQUE_HIDRICO_FINAL)
residualidad = 0
w_max_val = float(WMAX_FINAL)
exponente_kr = float(EXPONENTE_KR_FINAL)

''')

# mapa de riesgo, pestañas y reporte del motor
_core_source = _cortar(_core_source, "    # FRONT-END VISUAL", "\nelse:\n    st.info(", "    pass\n")

exec(compile(_core_source, str(_CORE_APP), "exec"), globals())

if "df" in globals() and isinstance(df, pd.DataFrame) and not df.empty:
    st.divider()
    mostrar_horizonte_pronostico(df, "San Pedro")

NOTA_SAN_PEDRO = (
    "**Validación en San Pedro.** La alerta se calibró en Bordenave y se probó, sin reajustarla, con los conteos de "
    "San Pedro publicados en el gemelo digital: 2023 y 2024 (clima del ensayo) y 2026 (clima de esta app); 30 intervalos "
    "entre conteos, 6 con emergencia ≥ 5 % de la campaña por semana. Emitida al comienzo de cada intervalo, la alerta "
    "separó los intervalos con flush con AUC 0,79 solo con clima, 0,83 con la fecha de primeras plántulas y 0,85 con "
    "conteos (gemelo de San Pedro: 0,58). Con primeras plántulas, 5 de los 6 flushes quedaron en *Alerta*; también 6 "
    "de los 24 intervalos sin flush.\n\n"
    "**Límites en San Pedro.** Tres campañas y pocos flushes. La emergencia varía mucho entre años: 50 % al 19/02 en "
    "2026, al 14/04 en 2024 y al 03/05 en 2023. En 2026 el primer flush (01/02–21/02, 59 % de la campaña) no se "
    "anticipó al 01/02: todavía no había lluvia registrada que lo explicara. Después de los grandes flushes de 2026 "
    "la alerta siguió alta sin emergencia (21/02 y 04/04), por agotamiento del banco; un factor de agotamiento no "
    "mejoró de forma clara la alerta con tan pocas campañas. La curva acumulada es el calendario de Bordenave: un "
    "calendario propio de San Pedro no la mejoró. La alerta con conteos está calibrada con conteos semanales: con "
    "recorridas cada 2–3 semanas, conviene usar sobre todo la fecha de primeras plántulas."
)

# Alerta de flushes (independiente del motor científico; no modifica sus resultados)
if "df_meteo_raw" in globals() and isinstance(df_meteo_raw, pd.DataFrame) and not df_meteo_raw.empty and "df" in globals():
    st.divider()
    try:
        import importlib

        import alerta_lolmu as _alerta_lolmu
        import visualizacion_alerta_lolmu as _vis_alerta

        # Streamlit conserva en memoria los módulos ya importados entre ejecuciones: tras una actualización del
        # repositorio, recargarlos evita usar una versión vieja
        importlib.reload(_alerta_lolmu)
        importlib.reload(_vis_alerta)
        mostrar_alerta_lolmu = _vis_alerta.mostrar_alerta_lolmu

        _resultados_alerta = mostrar_alerta_lolmu(
            df_meteo_raw,
            inicio_predicho=globals().get("fecha_inicio_ventana"),
            t_base=float(globals().get("t_base_val", 2.0)),
            t_opt=float(globals().get("t_opt_max", 20.0)),
            t_crit=float(globals().get("t_critica", 30.0)),
            tt_control=float(globals().get("dga_optimo", 600.0)),
            tt_limite=float(globals().get("dga_critico", 800.0)),
            tope_hasta_ultimo_cero=True,  # semanas ya cerradas por un conteo posterior en cero: probabilidad 0
            curva_desde_ultimo_cero=True,  # la curva acumulada arranca a mitad de camino entre el último cero y el primer conteo con plántulas
            localidad="San Pedro",
            nota_sitio=NOTA_SAN_PEDRO,
        )
    except Exception as _error_alerta:  # noqa: BLE001
        st.warning(f"No se pudo calcular la alerta: {_error_alerta}")


def _escribir_hoja(writer, dataframe, nombre):
    """Escribe una hoja y aplica un formato básico de lectura."""
    if not isinstance(dataframe, pd.DataFrame) or dataframe.empty:
        return
    dataframe.to_excel(writer, sheet_name=nombre, index=False)
    hoja = writer.sheets[nombre]
    ultima_columna = max(0, len(dataframe.columns) - 1)
    hoja.freeze_panes(1, 0)
    hoja.autofilter(0, 0, len(dataframe), ultima_columna)
    hoja.set_column(0, ultima_columna, 18)


# Descarga final: los resultados que muestra la app (alerta, emergencia acumulada y ventana de control)
_resultados_alerta = globals().get("_resultados_alerta")
if isinstance(_resultados_alerta, dict) and _resultados_alerta:
    reporte_excel_final = io.BytesIO()
    with pd.ExcelWriter(reporte_excel_final, engine="xlsxwriter", datetime_format="dd/mm/yyyy", date_format="dd/mm/yyyy") as writer:
        for _hoja, _tabla in _resultados_alerta.items():
            _escribir_hoja(writer, _tabla, _hoja)
    reporte_excel_final.seek(0)
    _emision = _resultados_alerta["Resumen"].set_index("Indicador")["Valor"].get("Fecha de emisión", "")

    st.divider()
    st.subheader("📥 Descarga de resultados")
    st.caption(
        "Excel con los resultados que muestra la app para la fecha de emisión elegida: resumen (nivel y probabilidad de "
        "flush, inicio y ventana de control 600–800 °Cd, emergencia acumulada esperada), alerta semanal, emergencia "
        "acumulada con su rango, tiempo térmico diario desde el inicio, conteos usados, clima, parámetros y validación."
    )
    st.download_button(
        label="📊 Descargar resultados en Excel",
        data=reporte_excel_final.getvalue(),
        file_name=f"PREDWEEM_Lolium_San_Pedro_alerta_{str(_emision).replace('/', '-') or 'resultados'}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        width="stretch",
        key="descarga_excel_resultados_final_san_pedro",
    )
