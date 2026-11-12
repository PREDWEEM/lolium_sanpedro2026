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

### Campaña vigente y actualización automática

Cada campaña carga clima del **1 de enero al 1 de octubre** (inclusive) del año en curso, hora de Argentina. Mientras
la campaña está abierta, la serie se actualiza automáticamente dos veces por día (07:30 y 15:30): SIGA–INTA hasta
ayer, puente provisional ECMWF IFS para los días que SIGA todavía no publicó y pronóstico ECMWF ENS (P50) de los
siete días siguientes; el pronóstico se recorta al 1 de octubre.

Del 2 de octubre al 31 de diciembre la campaña queda cerrada: no se consulta el ensamble y la serie se conserva. El
**1 de enero se reinicia automáticamente la carga** con la campaña nueva (la de 2027 empieza el 1/01/2027); mientras
SIGA no publica días del año, el puente provisional ECMWF los cubre, y la caché SIGA se limita a la campaña vigente.
Las variables `CAMPANIA_INICIO` y `CAMPANIA_FIN` (AAAA-MM-DD) permiten fijar otras fechas. Los archivos de pronóstico
históricos se conservan.

## Alerta validada de grandes flujos (sección independiente)

Debajo del motor PREDWEEM, la app muestra una **alerta de flushes**: la probabilidad de que en los próximos 7 días
emerja ≥ 5 % de la campaña, con dos niveles fijos (*Atención* desde 15 %, *Alerta* desde 25 %). Es la alerta calibrada
con 17 campañas de Bordenave (`alerta_lolmu.py`, `visualizacion_alerta_lolmu.py`, `alerta_lolmu_params.json`), sin
reajustar. No modifica el motor ni sus resultados.

Combina el calendario medio de emergencia de LOLMU, la respuesta a las lluvias ya registradas y, opcionalmente, la
fecha de las primeras plántulas del lote (que además ancla el reloj térmico de la ventana de control 600–800 °Cd;
sin ese dato la ventana no se calcula) y los conteos. Las semanas que un conteo posterior en cero
(sin plántulas previas) confirma sin emergencia quedan en 0 %.

Validación con los conteos de San Pedro publicados en el gemelo digital (2023 y 2024 con su clima; 2026 con el clima
de esta app): 30 intervalos entre conteos, 6 con flush. Alerta emitida al comienzo de cada intervalo:

| Información disponible | AUC | 2023 | 2024 | 2026 | Flushes en *Alerta* | Intervalos sin flush en *Alerta* |
|---|---|---|---|---|---|---|
| Solo clima | 0,79 | 1,00 | 0,91 | 0,50 | 4 de 6 | 6 de 24 |
| + primeras plántulas | 0,83 | 1,00 | 0,91 | 0,67 | 5 de 6 | 6 de 24 |
| + conteos | 0,85 | 0,88 | 0,95 | 0,67 | 5 de 6 | 6 de 24 |
| Gemelo `SAN-PEDRO_digitaltween` (motor SP-FINAL-2025-2026, calibración local) | 0,58 | 0,69 | 0,61 | 0,53 | — | — |

El gemelo usó el clima observado de los 7 días siguientes (pronóstico perfecto) y su motor se calibró con 2026; aun
así la alerta lo supera en las tres campañas. Límites: tres campañas y pocos flushes; la emergencia varía mucho entre
años (50 % al 19/02 en 2026, al 14/04 en 2024 y al 03/05 en 2023). Ni un calendario propio de San Pedro ni un factor
de agotamiento de la cohorte mejoraron de forma clara la alerta, por eso se usa sin cambios. Los datos están en
`data/campanias/`.

La página conserva el motor (con la parametrización congelada 2025–2026) y su horizonte de pronóstico; se retiraron
la sección «Datos del lote», el mapa de riesgo, las pestañas y el reporte del motor, y la imagen de fondo (fondo liso
claro). La barra lateral conserva solo los parámetros de la ventana de control. La descarga final reúne los
resultados de la alerta.

## Despliegue desde repositorio privado

La aplicación está preparada para utilizar archivos locales incluidos en el checkout privado de Streamlit y no depende de URLs públicas del propio repositorio para cargar datos meteorológicos, logo o activos del modelo.

La actualización automática de SIGA–INTA y ECMWF ENS continúa ejecutándose mediante GitHub Actions. Antes de cambiar la visibilidad, revise la guía [PRIVATE_REPOSITORY.md](PRIVATE_REPOSITORY.md), autorice a Streamlit para acceder a repositorios privados y ejecute la prueba manual del workflow meteorológico.

## Curva acumulada en tiempo térmico desde las primeras plántulas

Cuando se informa la fecha de las primeras plántulas (o hay un primer conteo con plántulas), la curva de emergencia
acumulada deja de seguir el calendario y sigue el **tiempo térmico acumulado desde esa fecha** (media y rango 10–90 % de
17 campañas de Bordenave, `curva_tt` en `alerta_lolmu_params.json`); más allá del clima disponible se suman temperaturas
medias históricas. Error medio de la emergencia acumulada en las fechas de conteo desde las primeras plántulas (puntos %):

| Localidad | Calendario por fecha | Tiempo térmico desde el inicio |
|---|---|---|
| Bordenave (17 campañas, dejando cada una afuera) | 12,9 | 11,3 |
| Lartigau 2026 | 9,9 | 5,8 |
| Olavarría 2026 | 13,7 | 10,7 |
| Pergamino 2024 y 2026 | 17,5 | 7,2 |
| San Pedro 2023, 2024 y 2026 | 19,5 | 14,4 |

Mejora sobre todo donde la fecha de inicio varía mucho entre años. En Tres Arroyos y Balcarce sigue el calendario propio
del sitio (error 6,1 y 6,9 puntos) y en Azul el calendario de Bordenave (5,3 contra 15,8 en su única campaña).

## Señal de lluvia (actualización de noviembre de 2026)

La señal de lluvia usa ahora el **modelo de pulsos ajustado con las 17 campañas de *Lolium multiflorum* de Bordenave**.
El tamaño de cada pulso depende del agua que entró al suelo, de cuán seco estaba y de la época del año (máximo para
lluvias de fines de mayo); la mitad de la respuesta emerge dentro de 114 °Cd de tiempo térmico de suelo y el 90 %
dentro de 252 °Cd. Con el nuevo núcleo se reajustaron los modelos logísticos, los percentiles de referencia y la
recalibración de flujos tardíos (`alerta_lolmu_params.json`). El balance de agua y la temperatura de suelo no cambian.

Validación con cada campaña de Bordenave predicha con el ajuste sin ella (incluido el núcleo de lluvia): AUC 0,77 solo
con clima, 0,83 con primeras plántulas y 0,87 con conteos. En las ocho localidades de validación, sin reajustar: 0,89,
0,92 y 0,93 (calendario solo, 0,89). En San Pedro: 0,81, 0,88 y 0,86 (antes 0,79, 0,83 y 0,85); las tablas de
validación de este sitio que figuran más arriba corresponden a la versión anterior.

## Aviso de flujos tardíos

Del 1 de mayo al 30 de junio la app muestra además la **probabilidad de flujos tardíos**: que en los próximos 7 días
emerja al menos 2 % de la campaña. El aviso se da desde 20 %; sin datos del lote, desde 25 % (`tardia.umbral_tramos`).
En esa época los grandes flujos (≥ 5 %) son raros, pero pocas plantas por semana importan para decidir la fecha de siembra.
Es la misma alerta recalibrada por nivel de información (`tardia` en `alerta_lolmu_params.json`). Aparece en un recuadro
debajo de la alerta, en el **semáforo semanal** del gráfico (fila «Flujos tardíos»: violeta fuerte = flujo tardío probable;
la fila «Grandes flujos» repite el nivel de cada semana) y en la descarga en Excel.

| Información | AUC Bordenave (17 campañas, 130 semanas de mayo–junio, 42 con ≥ 2 %) | Detectadas con el aviso | Semanas marcadas |
|---|---|---|---|
| Solo clima (aviso desde 25 %) | 0,57 | 67 % | 68 % |
| + primeras plántulas | 0,79 | 90 % | 62 % |
| + conteos semanales | 0,87 | 86 % | 51 % |

Cada campaña se predijo con el ajuste sin ella. Sin datos del lote el aviso casi no distingue semanas: conviene cargar la
fecha de primeras plántulas. En otras seis localidades (58 intervalos de mayo–junio, 10 con ≥ 2 % por semana) la AUC fue
0,85 con primeras plántulas y 0,89 con conteos, con 90 % de detección; allí la probabilidad tiende a ser alta (30 % contra
17 % observado).

**Del 1 de julio al 1 de octubre no se muestra probabilidad** (`tardia.recorrida`): en Bordenave (80 semanas, 11 con
flujo tardío) no distinguió las semanas con emergencia (AUC 0,41–0,50), y bajar el umbral solo marcaba más semanas al
azar. En su lugar, la app recomienda **recorrer los lotes cada 2 semanas**, sobre todo donde suele haber emergencia
invernal (sudoeste bonaerense), antes de definir la fecha de siembra o un control. En el semáforo esas semanas aparecen
en gris.

En las apps con dos o más campañas propias (Bordenave, Tres Arroyos, Balcarce, San Pedro y Pergamino), el recuadro de
flujos tardíos muestra además cuánto emergió **después de la fecha de emisión en cada campaña del sitio**. Si en esas
campañas, en mediana, emergió menos de 3 % de la campaña desde esa fecha, el aviso se presenta como «Flujo tardío posible
según el modelo; en <sitio> la emergencia suele cortarse antes»: la recalibración de tardíos se ajustó con Bordenave, donde
la emergencia se extiende hasta el invierno, y en sitios donde se corta antes avisa de más (en Balcarce, en mayo de 2014,
2025 y 2026, avisó 8 semanas y hubo 2 flujos tardíos). La probabilidad se sigue mostrando.

## Residual a la siembra (guía de riesgo)

Debajo de la alerta, un recuadro siempre visible muestra el riesgo de nacimientos después de la siembra para la **fecha de
siembra prevista** (1/05–31/07; si no se carga, el 1/06 como referencia), en tres tarjetas: riesgo (alto, medio o bajo),
emergencia después de sembrar (mediana) y recomendación (usar residual, según infestación, o solo si el lote está muy
infestado). Se calcula con las 3 campañas de San Pedro (`residual` en `alerta_lolmu_params.json`):

| Siembra | Campañas con ≥ 10 % de la emergencia después de sembrar | Mediana | Riesgo | Campañas del sitio |
|---|---|---|---|---|
| 1/05 | 33% | 6 % | Medio | 2023: 53 % · 2024: 6 % · 2026: 2 % |
| 15/05 | 33% | 4 % | Medio | 2023: 19 % · 2024: 4 % · 2026: 2 % |
| 1/06 | 0% | 1 % | Bajo | 2023: 2 % · 2024: 1 % · 2026: 1 % |
| 15/06 | 0% | 1 % | Bajo | 2023: 2 % · 2024: 1 % · 2026: 0 % |
| 1/07 | 0% | 0 % | Bajo | 2023: 0 % · 2024: 1 % · 2026: 0 % |

Riesgo alto: ≥ 40 % de las campañas con ≥ 10 % de emergencia posterior; medio: 20–40 %; bajo: < 20 %. Es un **riesgo
histórico, no una predicción de la campaña**: ni la fecha de primeras plántulas ni el clima anticiparon cuánta emergencia
queda después de la siembra. Como la decisión depende de las plantas por m², en lotes con alta infestación aun una fracción
chica puede ser más de 100 plantas/m². La necesidad de un graminicida post-emergente no se puede anticipar: se recomienda
recorrer el cultivo 30–45 días después de la siembra.

## Condiciones de uso

No se concede licencia de uso por el solo hecho de acceder al repositorio. Cualquier utilización académica, técnica, institucional o comercial que exceda la visualización del contenido requiere autorización previa y escrita del titular de los derechos correspondientes.

Las solicitudes de autorización deben canalizarse mediante los medios de contacto del titular del repositorio PREDWEEM.

## Limitación de responsabilidad

PREDWEEM es una herramienta de soporte para decisiones y no sustituye el diagnóstico profesional, el monitoreo a campo ni la evaluación agronómica específica de cada lote. Las decisiones de manejo deben ser adoptadas por profesionales responsables considerando las condiciones locales y la normativa aplicable.

## Autoría

**PREDWEEM by Guillermo R. Chantre**

