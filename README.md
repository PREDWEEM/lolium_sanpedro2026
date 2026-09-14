# PREDWEEM — Lolium San Pedro 2026

Repositorio correspondiente a la implementación de **PREDWEEM** para la predicción de la emergencia y la dinámica fenológica de *Lolium multiflorum* en San Pedro, provincia de Buenos Aires, Argentina.

> **Propiedad intelectual**  
> Copyright © 2026 Guillermo R. Chantre / PREDWEEM.  
> Todos los derechos reservados.
>
> Este repositorio constituye software propietario. Su disponibilidad pública no concede autorización para utilizar, copiar, modificar, redistribuir, sublicenciar, realizar ingeniería inversa ni explotar comercialmente el código, los modelos, los parámetros, los pesos neuronales, la documentación o los datos incluidos.
>
> Consulte el aviso completo en [COPYRIGHT.md](COPYRIGHT.md).

## Finalidad

PREDWEEM es una herramienta de apoyo a la toma de decisiones agronómicas basada en la integración de datos meteorológicos, modelos predictivos y filtros ecofisiológicos para anticipar los flujos de emergencia de raigrás anual.

La implementación de este repositorio está orientada a **San Pedro** y utiliza una **parametrización local congelada calibrada conjuntamente con las campañas completas 2025 y 2026**. La ANN original se mantiene sin modificaciones.

## Configuración San Pedro 2026 — versión final

- Coordenadas operativas: `-33.7328, -59.7965`.
- Estación SIGA–INTA: `A872890`.
- La ANN utiliza día juliano, TMAX del aire, TMIN del aire y precipitación.
- Cobertura efectiva calibrada: `17.1176548 %`.
- Wmax superficial calibrado: `21.8352965 mm`.
- Respuesta térmica: función logística continua con `T0 = 24.5547763 °C` y ventana de `7 días`.
- Interacción hídrica del umbral térmico: `alpha = 0.0523993 °C`.
- Pendiente logística térmica: `0.3659931 °C`.
- Agotamiento causal de cohorte: `k = 0.4302566`.
- Choque hídrico: `45 mm` acumulados en 3 días.
- Exponente Kr: `0.0`.
- Umbral de primer pico válido: `EMERREL > 0.20`.

La termoinhibición binaria anterior fue reemplazada por una interacción continua temperatura × humedad. Posteriormente se aplica un reservorio causal de cohorte que reduce la disponibilidad remanente a medida que ocurren los pulsos de emergencia. Los parámetros de esta versión quedan **congelados** para preservar reproducibilidad.

Los valores exactos se documentan también en [`sanpedro_calibration_2025_2026.json`](sanpedro_calibration_2025_2026.json).

## Trazabilidad del motor

`app_emergencia_core.py` se conserva como base histórica y auditable. El punto de entrada `app_emergencia.py` aplica de forma determinística el módulo [`sanpedro_calibracion_final.py`](sanpedro_calibracion_final.py) antes de compilar el core. El parche exige una única coincidencia de cada bloque esperado y detiene la aplicación si el core cambia de manera incompatible, evitando actualizaciones silenciosamente parciales.

## Actualización meteorológica robusta

La serie operativa utiliza una jerarquía explícita de fuentes:

1. **SIGA–INTA A872890** como observación prioritaria y definitiva.
2. **ECMWF IFS histórico** como cobertura provisional de cualquier fecha vencida sin una observación SIGA completa y válida.
3. **ECMWF IFS ENS 0.25°** para hoy y los próximos seis días, con P50 operativo para TMAX, TMIN, TMEDIA y precipitación.

La precipitación faltante nunca se interpreta como cero. Si falta únicamente TMEDIA y Tmax/Tmin son válidas, se deriva desde ambas temperaturas. El ensamble se empareja por identificador de miembro, exige 24 horas válidas por día y conserva medias, P10, P50 y P90 para auditoría. Los datos provisionales se reemplazan automáticamente cuando SIGA publica una observación completa.

## Despliegue desde repositorio privado

La aplicación está preparada para utilizar archivos locales incluidos en el checkout privado de Streamlit y no depende de URLs públicas del propio repositorio para cargar datos meteorológicos, logo o activos del modelo.

La actualización automática de SIGA–INTA y ECMWF ENS continúa ejecutándose mediante GitHub Actions. Antes de cambiar la visibilidad, revise la guía [PRIVATE_REPOSITORY.md](PRIVATE_REPOSITORY.md), autorice a Streamlit para acceder a repositorios privados y ejecute la prueba manual del workflow meteorológico.

## Condiciones de uso

No se concede licencia de uso por el solo hecho de acceder al repositorio. Cualquier utilización académica, técnica, institucional o comercial que exceda la visualización del contenido requiere autorización previa y escrita del titular de los derechos correspondientes.

Las solicitudes de autorización deben canalizarse mediante los medios de contacto del titular del repositorio PREDWEEM.

## Limitación de responsabilidad

PREDWEEM es una herramienta de soporte para decisiones y no sustituye el diagnóstico profesional, el monitoreo a campo ni la evaluación agronómica específica de cada lote. Las decisiones de manejo deben ser adoptadas por profesionales responsables considerando las condiciones locales y la normativa aplicable.

## Autoría

**PREDWEEM by Guillermo R. Chantre**
