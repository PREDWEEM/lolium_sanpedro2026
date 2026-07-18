from pathlib import Path
import json
import shutil

ROOT = Path('.')
TEXT_SUFFIXES = {'.py', '.md', '.txt', '.json', '.csv', '.js'}

REPLACEMENTS = [
    ('PREDWEEM/LOLIUM_TA2026', 'PREDWEEM/lolium_sanpedro2026'),
    ('PREDWEEM/loliumTA_2026', 'PREDWEEM/lolium_sanpedro2026'),
    ('TRES ARROYOS', 'SAN PEDRO'),
    ('Tres Arroyos', 'San Pedro'),
    ('tres_arroyos', 'san_pedro'),
    ('TRES_ARROYOS', 'SAN_PEDRO'),
    ('3ARROYOS', 'SAN PEDRO'),
    ('latitud_ta', 'latitud_san_pedro'),
    ('-38.4500', '-33.7328'),
    ('-38.45', '-33.7328'),
    ('-38.388', '-33.7328'),
    ('-60.346', '-59.7965'),
    ('-60.2763', '-59.7965'),
    ('NH0216', 'A872890'),
    ('INTA BARROW', 'SIGA A872890'),
    ('INTA Barrow', 'SIGA A872890'),
    ('SIGA_INTA_SAN_PEDRO_BARROW', 'SIGA_INTA_SAN_PEDRO_A872890'),
]

for path in ROOT.rglob('*'):
    if not path.is_file() or '.git' in path.parts or '.github' in path.parts:
        continue
    if path.name == 'adapt_san_pedro_once.py' or path.suffix.lower() not in TEXT_SUFFIXES:
        continue
    try:
        text = path.read_text(encoding='utf-8')
    except UnicodeDecodeError:
        continue
    original = text
    for old, new in REPLACEMENTS:
        text = text.replace(old, new)

    if path.name == 'app_emergencia.py':
        text = text.replace(
            '# - DINÁMICA HÍDRICA CRUCIAL: Preservación del Secado Exponencial del Suelo (Factor Kr) en el BHS.',
            '# - MÓDULO HÍDRICO PROVISIONAL: Kr heredado de Tres Arroyos; pendiente de validación local en San Pedro.'
        )
        text = text.replace(
            '# Factor Kr — Secado exponencial específico de San Pedro',
            '# Factor Kr — heredado de Tres Arroyos; pendiente de validación local en San Pedro'
        )
        text = text.replace(
            '# Balance Hídrico Superficial (San Pedro con secado exponencial Kr)',
            '# Balance Hídrico Superficial (Kr heredado; pendiente de validación en San Pedro)'
        )
        text = text.replace(
            'st.caption("San Pedro · VISUAL V3 · ventana eficiente verde · exportación PNG de alta resolución")',
            'st.caption("San Pedro · configuración geográfica preliminar · parámetros ecofisiológicos pendientes de validación local")'
        )

    if text != original:
        path.write_text(text, encoding='utf-8')

for source, destination in {
    Path('actualizar_meteo_tres_arroyos.py'): Path('actualizar_meteo_san_pedro.py'),
    Path('postprocesar_prec_p50_tres_arroyos.py'): Path('postprocesar_prec_p50_san_pedro.py'),
}.items():
    if source.exists() and not destination.exists():
        source.rename(destination)

legacy = Path('fetch_meteobahia.py')
if legacy.exists():
    legacy.unlink()
Path('fetch_meteobahia_legacy.py').write_text(
    '"""Fuente Meteobahía de Tres Arroyos deshabilitada para San Pedro.\n\n'
    'Use actualizar_meteo_san_pedro.py con SIGA A872890 y ECMWF ENS.\n'
    '"""\n\n'
    'raise SystemExit("Fuente legacy deshabilitada: ejecutar actualizar_meteo_san_pedro.py")\n',
    encoding='utf-8'
)

for filename in ('meteo_daily.csv', 'VALIDA (1).xlsx', 'validacion.xlsx'):
    path = Path(filename)
    if path.exists():
        path.unlink()

data_dir = Path('data')
data_dir.mkdir(exist_ok=True)
for path in data_dir.glob('siga_*_observado.csv*'):
    path.unlink()
forecast_dir = data_dir / 'historico_pronosticos'
if forecast_dir.exists():
    shutil.rmtree(forecast_dir)
forecast_dir.mkdir(parents=True, exist_ok=True)
(forecast_dir / '.gitkeep').write_text('', encoding='utf-8')

state = {
    'sitio': 'San Pedro',
    'estacion_siga': 'A872890',
    'latitud': -33.7328,
    'longitud': -59.7965,
    'estado': 'pendiente_primera_actualizacion',
    'nota': 'Los parámetros ecofisiológicos heredados requieren validación local.'
}
(data_dir / 'estado_actualizacion_meteo.json').write_text(
    json.dumps(state, ensure_ascii=False, indent=2) + '\n', encoding='utf-8'
)

Path('wake_up_script.js').write_text(
    "const { chromium } = require('playwright');\n\n"
    "(async () => {\n"
    "  const url = process.env.STREAMLIT_URL;\n"
    "  if (!url) throw new Error('Defina STREAMLIT_URL con la aplicación de San Pedro.');\n"
    "  const browser = await chromium.launch();\n"
    "  const page = await browser.newPage();\n"
    "  console.log(`Visitando ${url}...`);\n"
    "  await page.goto(url, { waitUntil: 'networkidle' });\n"
    "  const wakeUpButton = page.locator('button:has-text(\"Wake up\")');\n"
    "  if (await wakeUpButton.isVisible()) {\n"
    "    await wakeUpButton.click();\n"
    "    await page.waitForTimeout(5000);\n"
    "  }\n"
    "  await browser.close();\n"
    "})();\n",
    encoding='utf-8'
)

readme = Path('README.md')
current = readme.read_text(encoding='utf-8') if readme.exists() else '# lolium_sanpedro2026\n'
note = (
    '\n\n## Configuración San Pedro 2026\n\n'
    '- Coordenadas operativas: `-33.7328, -59.7965`.\n'
    '- Estación SIGA–INTA: `A872890`.\n'
    '- La ANN utiliza día juliano, TMAX del aire, TMIN del aire y precipitación.\n'
    '- Los datos meteorológicos y validaciones de Tres Arroyos fueron retirados.\n'
    '- El balance Kr y los restantes parámetros ecofisiológicos se conservan provisionalmente y requieren validación local antes de uso productivo.\n'
)
if '## Configuración San Pedro 2026' not in current:
    readme.write_text(current.rstrip() + note, encoding='utf-8')
