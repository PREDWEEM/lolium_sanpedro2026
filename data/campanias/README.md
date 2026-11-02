# Campañas de San Pedro

Copias fijas de las campañas de *Lolium* de San Pedro, usadas para validar la alerta de flushes. La actualización
automática del clima no modifica esta carpeta.

| Campaña | Conteos | Clima | Origen |
|---|---|---|---|
| 2023 | 9 conteos del 14/04 al 01/10, sin cero inicial | 01/01–31/08, diario | gemelo `SAN-PEDRO_digitaltween` (`data/reference`), aportados por el autor el 07/10/2026 |
| 2024 | 15 conteos del 16/03 al 17/10, sin cero inicial | 01/01–30/09, diario | ídem |
| 2026 | 12 conteos del 01/02 (cero) al 15/07 | 01/01–01/10: SIGA–INTA A872890 (263 días) y puente ECMWF IFS (11 días), copia de `meteo_daily.csv` al cierre | gemelo (`data/calibration`) y esta app |

- `emergencia_san_pedro_<año>.csv`: `Fecha`, `PLM2` (plantas nuevas por m² en el intervalo que termina en esa fecha) y
  emergencia acumulada (%). Junto a cada CSV está la planilla original.
- `clima_san_pedro_<año>.csv`: `Fecha`, `TMAX`, `TMIN` (°C), `Prec` (mm).
- `procedencia_*.json`: procedencia y sumas de verificación copiadas del gemelo (versión 186b918).

En 2023 y 2024 el primer conteo ya tenía plantas: la emergencia empezó antes y la fecha de primeras plántulas usada
en la validación es la del primer conteo. 2025 no está: el gemelo solo tiene la curva procesada de esa campaña, sin
conteos ni clima.
