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

La implementación de este repositorio está orientada a **San Pedro**. Sus parámetros ecofisiológicos provisionales requieren validación local antes de su utilización productiva.

## Configuración San Pedro 2026

- Coordenadas operativas: `-33.7328, -59.7965`.
- Estación SIGA–INTA: `A872890`.
- La ANN utiliza día juliano, TMAX del aire, TMIN del aire y precipitación.
- Los datos meteorológicos y validaciones de Tres Arroyos fueron retirados.
- El balance Kr y los restantes parámetros ecofisiológicos se conservan provisionalmente y requieren validación local antes de uso productivo.

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
