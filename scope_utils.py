"""
scope_utils.py

Utilidades compartidas para los scripts de analisis de trazas del osciloscopio.
"""

import os
import numpy as np


PROFILING_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "profiling_set")


def list_csv_files():
    """Devuelve los nombres de archivo CSV en PROFILING_DIR, ordenados."""
    return sorted(f for f in os.listdir(PROFILING_DIR) if f.upper().endswith(".CSV"))


def parse_scope_csv(path):
    """Lee un CSV del osciloscopio. Devuelve (tiempos, voltajes) como arrays numpy."""
    times, volts = [], []
    with open(path, "r") as f:
        in_data = False
        for line in f:
            line = line.strip()
            if not line:
                continue
            if not in_data:
                if line.startswith("Waveform Data"):
                    in_data = True
                continue
            parts = [p for p in line.split(",") if p.strip() != ""]
            if len(parts) < 2:
                continue
            try:
                times.append(float(parts[0]))
                volts.append(float(parts[1]))
            except ValueError:
                continue
    return np.array(times), np.array(volts)


def pearson(a, b):
    """Correlacion de Pearson entre dos arrays, alineando al minimo comun."""
    L = min(len(a), len(b))
    a, b = a[:L] - np.mean(a[:L]), b[:L] - np.mean(b[:L])
    denom = np.sqrt(np.sum(a * a) * np.sum(b * b))
    return float(np.sum(a * b) / denom) if denom != 0 else 0.0


def euclidean(a, b):
    """Distancia euclidea entre dos arrays, alineando al minimo comun."""
    L = min(len(a), len(b))
    return float(np.sqrt(np.sum((a[:L] - b[:L]) ** 2)))


def print_stats(v, name):
    print(f"  {name}: n={len(v)}  media={np.mean(v):+.4f} V  "
          f"std={np.std(v):.4f} V  min={np.min(v):+.3f} V  "
          f"max={np.max(v):+.3f} V")
