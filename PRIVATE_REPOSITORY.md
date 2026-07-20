# Preparación para repositorio privado

Este documento resume las verificaciones necesarias para convertir `PREDWEEM/lolium_sanpedro2026` en un repositorio privado sin interrumpir la aplicación Streamlit ni la actualización meteorológica automática.

## Cambios incorporados

- La aplicación utiliza `meteo_daily.csv`, planillas y recursos gráficos desde el checkout local del repositorio.
- Se eliminan las dependencias internas de URLs públicas `raw.githubusercontent.com`.
- Los archivos de modelos deben existir en el despliegue; la aplicación no genera pesos aleatorios de reemplazo.
- `.gitignore` bloquea secretos, credenciales, claves privadas, entornos locales y datos confidenciales.
- El workflow meteorológico continúa usando la URL pública de SIGA–INTA y secretos de GitHub Actions.
- Un control automático verifica que los recursos locales requeridos estén presentes y que no reaparezcan enlaces públicos al propio repositorio.

## Antes de cambiar la visibilidad

1. En Streamlit Community Cloud, autorizar el acceso a los repositorios privados de la cuenta u organización `PREDWEEM`.
2. Confirmar que la app desplegada esté vinculada a `PREDWEEM/lolium_sanpedro2026`, rama `main` y archivo `app_emergencia.py`.
3. Revisar en GitHub `Settings → Secrets and variables → Actions` que los secretos SIGA opcionales continúen disponibles.
4. Verificar que GitHub Actions esté habilitado para el repositorio.
5. Conservar una copia probatoria del repositorio y de los SHA de la versión previa a la privatización.

## Prueba posterior a la privatización

1. Ejecutar manualmente el workflow **Actualizar SIGA San Pedro y ECMWF ENS** mediante `workflow_dispatch`.
2. Confirmar que finalice correctamente y actualice `meteo_daily.csv` y los archivos de `data/`.
3. Verificar que Streamlit reconstruya o reinicie la app después del nuevo commit.
4. Abrir la aplicación y comprobar:
   - carga del logo local;
   - lectura de `meteo_daily.csv`;
   - carga de la ANN y del clasificador;
   - visualización de resultados;
   - descarga del reporte Excel.
5. Esperar y revisar al menos una ejecución programada de las 07:30 o 15:30 hora Argentina.

## Recursos que deben permanecer en el repositorio privado

- `IW.npy`
- `LW.npy`
- `bias_IW.npy`
- `bias_out.npy`
- `modelo_clusters_k3.pkl`
- `app_emergencia_core.py`
- `meteo_daily.csv`
- `logo.png`

Estos archivos son necesarios para el despliegue actual. En una etapa posterior, los activos del modelo deberían trasladarse a un backend o API privada centralizada.

## Advertencia sobre el historial

Cambiar la visibilidad protege el acceso futuro, pero no elimina copias, forks o clones realizados mientras el repositorio era público. La protección de mejoras posteriores debe apoyarse en repositorios privados, control de accesos, registro de versiones y contratos de confidencialidad/licencia.
