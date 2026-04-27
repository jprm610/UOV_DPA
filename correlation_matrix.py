"""
correlation_matrix.py

Genera la matriz de correlacion de Pearson entre todos los CSVs
en profiling_set/ y la muestra como heatmap.
"""

import os
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap, BoundaryNorm

from scope_utils import PROFILING_DIR, list_csv_files, parse_scope_csv, pearson


def main():
    files = list_csv_files()
    n = len(files)
    labels = [os.path.splitext(f)[0] for f in files]

    print(f"Cargando {n} trazas...")
    traces = [parse_scope_csv(os.path.join(PROFILING_DIR, f))[1] for f in files]

    matrix = np.ones((n, n))
    for i in range(n):
        for j in range(i + 1, n):
            r = pearson(traces[i], traces[j])
            matrix[i, j] = r
            matrix[j, i] = r

    col_w = 8
    header = f"{'':>6}" + "".join(f"{l:>{col_w}}" for l in labels)
    print("\n" + header)
    print("-" * len(header))
    for i, row_label in enumerate(labels):
        row = f"{row_label:>6}" + "".join(f"{matrix[i, j]:>{col_w}.4f}" for j in range(n))
        print(row)

    cmap = ListedColormap(["white", "tab:green"])
    norm = BoundaryNorm([matrix.min() - 1, 0.9, 1.0 + 1e-9], cmap.N)

    fig, ax = plt.subplots(figsize=(8, 7))
    im = ax.imshow(matrix, cmap=cmap, norm=norm)
    fig.colorbar(im, ax=ax, ticks=[0.45, 0.95], label="Pearson r")

    ax.set_xticks(range(n)); ax.set_xticklabels(labels, rotation=45, ha="right")
    ax.set_yticks(range(n)); ax.set_yticklabels(labels)
    ax.set_title("Matriz de correlacion de Pearson — profiling_set")

    for i in range(n):
        for j in range(n):
            ax.text(j, i, f"{matrix[i, j]:.3f}", ha="center", va="center",
                    fontsize=8, color="black")

    fig.tight_layout()
    out = "output/correlation_matrix.png"
    fig.savefig(out, dpi=120)
    print(f"\nHeatmap guardado en '{out}'.")


if __name__ == "__main__":
    main()
