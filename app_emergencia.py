# -*- coding: utf-8 -*-
"""Punto de entrada final de PREDWEEM San Pedro 2026.

La aplicación base se conserva en ``app_emergencia_core.py`` para auditoría.
Antes de compilarla se aplica la parametrización local congelada obtenida con
las campañas completas 2025–2026: respuesta termohídrica continua y
agotamiento causal de cohorte. La ANN original no se modifica.
"""
from pathlib import Path

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
exec(compile(_core_source, str(_CORE_APP), "exec"), globals())

if "df" in globals() and isinstance(df, pd.DataFrame) and not df.empty:
    st.divider()
    mostrar_horizonte_pronostico(df, "San Pedro")


def _fecha_reporte(valor):
    """Convierte una fecha a texto legible y admite valores ausentes."""
    if valor is None or pd.isna(valor):
        return ""
    return pd.Timestamp(valor).strftime("%d/%m/%Y")


def _escribir_hoja(writer, dataframe, nombre):
    """Escribe una hoja y aplica un formato básico de lectura."""
    if not isinstance(dataframe, pd.DataFrame) or dataframe.empty:
        return

    dataframe.to_excel(writer, sheet_name=nombre, index=False)
    hoja = writer.sheets[nombre]
    ultima_fila = len(dataframe)
    ultima_columna = max(0, len(dataframe.columns) - 1)
    hoja.freeze_panes(1, 0)
    hoja.autofilter(0, 0, ultima_fila, ultima_columna)
    hoja.set_column(0, ultima_columna, 18)


if "df" in globals() and isinstance(df, pd.DataFrame) and not df.empty:
    reporte_excel_final = io.BytesIO()

    resumen_decision = pd.DataFrame(
        {
            "Indicador": [
                "Localidad",
                "Versión motor local",
                "Calibración",
                "Fecha de generación",
                "Inicio del conteo térmico",
                "Fecha objetivo de control",
                "Fecha límite de la ventana",
                "TT acumulado actual (°Cd)",
                "TT pronosticado +7 días (°Cd)",
                "Estado operativo",
                "Cobertura efectiva calibrada (%)",
                "Wmax superficial calibrado (mm)",
                "Ke aplicado",
                "Exponente Kr",
            ],
            "Valor": [
                "San Pedro (Buenos Aires)",
                VERSION_MOTOR,
                CALIBRACION,
                pd.Timestamp.now().strftime("%d/%m/%Y %H:%M"),
                _fecha_reporte(globals().get("fecha_inicio_ventana")),
                _fecha_reporte(globals().get("fecha_control")),
                _fecha_reporte(globals().get("fecha_limite")),
                globals().get("dga_hoy", 0.0),
                globals().get("dga_7dias", 0.0),
                globals().get("msg_estado", ""),
                globals().get("cobertura_pct", COBERTURA_FINAL),
                globals().get("w_max_val", WMAX_FINAL),
                globals().get("ke_val", ""),
                globals().get("exponente_kr", EXPONENTE_KR_FINAL),
            ],
        }
    )

    metricas_reporte = pd.DataFrame(
        {
            "Métrica": [
                "PEC (%)",
                "Lag control vs. pico de campo (días)",
                "Lead time (días)",
                "Pearson de flujos",
                "NSE de flujos",
                "KGE de flujos",
                "RMSE acumulado",
                "R2 acumulado",
                "CCC acumulado",
                "Desfase T50 (días)",
                "F1-Score de coincidencia",
                "Exactitud global",
                "Hits",
                "Misses",
                "Falsos positivos",
                "Correctos negativos",
                "Desfase del primer flujo (días)",
            ],
            "Valor": [
                globals().get("pec", 0.0),
                globals().get("peak_lag", 0),
                globals().get("lead_time", 0),
                globals().get("pearson_r", 0.0),
                globals().get("nse_flujos", 0.0),
                globals().get("kge_flujos", 0.0),
                globals().get("rmse_acum", 0.0),
                globals().get("r2_acum", 0.0),
                globals().get("ccc_acum", 0.0),
                globals().get("desfase_t50", 0),
                globals().get("f1_score_coincidencia", 0.0),
                globals().get("exactitud_global", 0.0),
                globals().get("hits_val", 0),
                globals().get("misses_val", 0),
                globals().get("falsos_pos_val", 0),
                globals().get("correctos_neg_val", 0),
                globals().get("lag_inicio_dias", "N/A"),
            ],
        }
    )

    parametros_reporte = pd.DataFrame(
        {
            "Parámetro": [
                "Latitud",
                "Longitud",
                "Latencia fija (JD)",
                "Motor termoinhibición",
                "Ventana termohídrica (días)",
                "T0 termohídrico (°C)",
                "Alivio hídrico alpha (°C)",
                "Pendiente logística térmica (°C)",
                "Escala lluvia termohídrica 3d (mm)",
                "k agotamiento de cohorte",
                "Choque hídrico 3d (mm)",
                "Fin choque hídrico (JD)",
                "Techo del bypass hídrico",
                "Umbral del primer pico",
                "Cobertura efectiva (%)",
                "Wmax superficial (mm)",
                "Ke",
                "Exponente Kr",
                "Temperatura base (°C)",
                "Temperatura óptima (°C)",
                "Temperatura crítica (°C)",
                "TT objetivo de control (°Cd)",
                "TT límite de ventana (°Cd)",
                "Residualidad del herbicida (días)",
                "Umbral de alerta temprana",
            ],
            "Valor": [
                -33.7328,
                -59.7965,
                25,
                "Continuo T×H",
                VENTANA_TERMOHIDRICA_FINAL,
                T0_TERMOHIDRICO_FINAL,
                ALPHA_HIDRICA_FINAL,
                PENDIENTE_TERMOHIDRICA_FINAL,
                ESCALA_LLUVIA_TH_FINAL,
                K_COHORTE_FINAL,
                CHOQUE_HIDRICO_FINAL,
                110,
                0.75,
                globals().get("UMBRAL_PRIMER_PICO", 0.20),
                COBERTURA_FINAL,
                WMAX_FINAL,
                globals().get("ke_val", ""),
                EXPONENTE_KR_FINAL,
                globals().get("t_base_val", ""),
                globals().get("t_opt_max", ""),
                globals().get("t_critica", ""),
                globals().get("dga_optimo", ""),
                globals().get("dga_critico", ""),
                globals().get("residualidad", ""),
                globals().get("umbral_er", ""),
            ],
        }
    )

    with pd.ExcelWriter(
        reporte_excel_final,
        engine="xlsxwriter",
        datetime_format="dd/mm/yyyy",
        date_format="dd/mm/yyyy",
    ) as writer:
        _escribir_hoja(writer, df, "Resultados_Diarios")
        _escribir_hoja(writer, globals().get("df_sincronizado"), "Validacion_Intervalos")
        _escribir_hoja(writer, globals().get("df_campo"), "Observaciones_Campo")
        _escribir_hoja(writer, resumen_decision, "Resumen_Decision")
        _escribir_hoja(writer, metricas_reporte, "Metricas_Validacion")
        _escribir_hoja(writer, parametros_reporte, "Parametros_Modelo")
        _escribir_hoja(writer, globals().get("df_desde_pico"), "Tiempo_Termico")

    reporte_excel_final.seek(0)

    st.divider()
    st.subheader("📥 Descarga final de resultados")
    st.caption(
        "El archivo reúne resultados diarios, validación Event-to-Event, "
        "observaciones de campo, métricas, parámetros congelados y tiempo térmico."
    )
    st.download_button(
        label="📊 Descargar resultados completos en Excel",
        data=reporte_excel_final.getvalue(),
        file_name="PREDWEEM_San_Pedro_Resultados_Completos.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        width="stretch",
        key="descarga_excel_resultados_final_san_pedro",
    )
