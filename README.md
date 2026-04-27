# UOV DPA — Power Analysis sobre UOV Línea 9 en F₁₂₈

Herramientas de captura y análisis de trazas de consumo de potencia para
estudiar la Línea 9 del algoritmo **UOV.Sign** implementado sobre el campo
finito F₁₂₈.

## Contexto

La Línea 9 del algoritmo UOV calcula la forma cuadrática:

```
y_i = v^T · P_i^(1) · v    para i ∈ [m]
```

donde `v` es el vector *vinegar* y las `P_i` son matrices triangulares
superiores fijas. La implementación en C (`uov_line9 F128.c`) se ejecuta en el
dispositivo objetivo; el osciloscopio registra su consumo de potencia durante
`compute_y()`. El banco de perfilamiento contiene 10 vectores de entrada
conocidos (`V0`–`V9`), cada uno con una traza capturada.

## Estructura del repositorio

```
.
├── uov_line9 F128.c       # Implementacion C del target (F_128, n=m=3)
├── profiling_set/         # Trazas de osciloscopio para los 10 vectores
│   ├── V0.CSV … V9.CSV
├── scope_utils.py         # Modulo compartido: parser CSV, Pearson, Euclidea
├── compare_traces.py      # Compara dos trazas en detalle
├── correlation_matrix.py  # Matriz de correlacion de Pearson (heatmap)
├── live.py                # Compara una traza nueva contra el profiling set
└── output/                # Imagenes generadas
```

## Requisitos

```
Python >= 3.9
numpy
matplotlib
```

```bash
pip install numpy matplotlib
```

## Scripts

### `compare_traces.py`

Compara dos trazas del `profiling_set/` e imprime métricas globales
(Pearson, distancia euclidea, diferencia máxima y media) y un análisis
por ventanas deslizantes. Genera `compare_result.png` con 3 paneles:
trazas superpuestas, diferencia punto a punto y correlación por ventana.

```bash
python compare_traces.py
# Seleccionar: Traza A: V0   Traza B: V3
```

### `correlation_matrix.py`

Calcula la matriz de correlación de Pearson entre los 10 CSVs y muestra
un heatmap (verde ≥ 0.9, blanco < 0.9). Guarda la imagen en `output/correlation_matrix.png`.

```bash
python correlation_matrix.py
```

### `live.py`

Carga una traza externa (por ejemplo, capturada durante un ataque) y la
compara contra todas las trazas del `profiling_set/`, mostrando el TOP 5
de vectores más similares por correlación de Pearson.

```bash
python live.py
# Traza a comparar: <ruta al CSV>
```

## Formato CSV

Los archivos CSV deben provenir de un osciloscopio Rigol o GW Instek.
El parser busca la línea `Waveform Data` como inicio de datos y lee pares
`tiempo, voltaje` a continuación.

## Módulo compartido — `scope_utils.py`

Todos los scripts importan desde este módulo:

| Función | Descripción |
|---|---|
| `PROFILING_DIR` | Ruta absoluta a `profiling_set/` |
| `list_csv_files()` | Lista los CSVs disponibles en el directorio |
| `parse_scope_csv(path)` | Devuelve `(times, volts)` como arrays NumPy |
| `pearson(a, b)` | Correlación de Pearson con alineación de longitud |
| `euclidean(a, b)` | Distancia euclidea con alineación de longitud |
| `print_stats(v, name)` | Imprime media, std, min y max de una traza |
