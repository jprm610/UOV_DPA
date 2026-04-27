"""
compare_traces.py

Compara dos trazas capturadas con el osciloscopio y reporta diferencias
entre ellas mediante varias metricas (globales y por ventanas).

Salida:
    - Reporte en consola.
    - Grafica 'compare_result.png' con 3 paneles:
        (1) las dos trazas superpuestas,
        (2) la resta punto a punto (A - B),
        (3) correlacion por ventanas a lo largo del tiempo.
"""

import os
import numpy as np
import matplotlib.pyplot as plt

from scope_utils import PROFILING_DIR, list_csv_files, parse_scope_csv, pearson, euclidean, print_stats


N_WINDOWS = 20
TOP_N = 10


def main():
    available = list_csv_files()
    print("Archivos disponibles en profiling_set/:")
    for i, name in enumerate(available, 1):
        print(f"  {i}. {name}")
    print()

    name_a = input("Traza A: ").strip() + ".CSV"
    name_b = input("Traza B: ").strip() + ".CSV"
    path_a = os.path.join(PROFILING_DIR, name_a)
    path_b = os.path.join(PROFILING_DIR, name_b)
    for p in (path_a, path_b):
        if not os.path.isfile(p):
            print(f"Error: no existe el archivo '{p}'.")
            return

    t_a, v_a = parse_scope_csv(path_a)
    t_b, v_b = parse_scope_csv(path_b)

    print(f"Traza A ({name_a}): {len(v_a)} muestras")
    print(f"Traza B ({name_b}): {len(v_b)} muestras")

    L = min(len(v_a), len(v_b))
    v_a, v_b, t = v_a[:L], v_b[:L], t_a[:L]
    dt = t[1] - t[0] if len(t) > 1 else 1.0

    print(f"Longitud comun: {L} muestras  (dt = {dt*1e6:.2f} us)\n")

    print("=" * 62)
    print("ESTADISTICAS INDIVIDUALES")
    print("=" * 62)
    print_stats(v_a, "A")
    print_stats(v_b, "B")
    print()

    corr = pearson(v_a, v_b)
    dist = euclidean(v_a, v_b)
    diff = v_a - v_b
    max_abs = np.max(np.abs(diff))
    mean_abs = np.mean(np.abs(diff))

    print("=" * 62)
    print("METRICAS GLOBALES")
    print("=" * 62)
    print(f"  Correlacion de Pearson: {corr:+.6f}  "
          f"(1.0 = identicas, 0 = no correlacionadas)")
    print(f"  Distancia euclidea    : {dist:.4f}")
    print(f"  Diferencia abs maxima : {max_abs:.4f} V")
    print(f"  Diferencia abs media  : {mean_abs:.4f} V\n")

    print("=" * 62)
    print(f"TOP {TOP_N} PUNTOS CON MAYOR DIFERENCIA ABSOLUTA")
    print("=" * 62)
    idx_sorted = np.argsort(-np.abs(diff))[:TOP_N]
    for rank, i in enumerate(idx_sorted, 1):
        print(f"  {rank:2d}. t = {t[i]*1e3:+8.3f} ms   "
              f"A = {v_a[i]:+.3f} V   B = {v_b[i]:+.3f} V   "
              f"dif = {diff[i]:+.3f} V")
    print()

    print("=" * 62)
    print(f"ANALISIS POR VENTANAS (dividiendo la traza en {N_WINDOWS})")
    print("=" * 62)
    win_size = L // N_WINDOWS
    win_corrs, win_dists, win_centers = [], [], []
    for w in range(N_WINDOWS):
        s = w * win_size
        e = s + win_size if w < N_WINDOWS - 1 else L
        win_corrs.append(pearson(v_a[s:e], v_b[s:e]))
        win_dists.append(euclidean(v_a[s:e], v_b[s:e]))
        win_centers.append(t[(s + e) // 2])
    win_corrs = np.array(win_corrs)
    win_dists = np.array(win_dists)
    win_centers = np.array(win_centers)

    order = np.argsort(win_corrs)
    print("  Ranking por ventana (menor correlacion = mas diferencia):")
    print(f"  {'ventana':>7}  {'t_centro [ms]':>14}  {'corr':>8}  {'dist_eucl':>10}")
    for rank, w in enumerate(order[:min(5, N_WINDOWS)], 1):
        print(f"  {w:>7}  {win_centers[w]*1e3:>14.3f}  "
              f"{win_corrs[w]:>+8.4f}  {win_dists[w]:>10.4f}")
    if N_WINDOWS > 5:
        print(f"  ... ({N_WINDOWS - 5} ventanas mas restantes)")
    print()

    fig, axes = plt.subplots(3, 1, figsize=(14, 9), sharex=True)

    axes[0].plot(t * 1e3, v_a, linewidth=0.6, label=f"A: {name_a}", color="tab:blue", alpha=0.8)
    axes[0].plot(t * 1e3, v_b, linewidth=0.6, label=f"B: {name_b}", color="tab:red", alpha=0.8)
    axes[0].set_ylabel("Voltaje (V)")
    axes[0].set_title(f"Trazas superpuestas  |  Pearson = {corr:+.4f}  |  dist = {dist:.2f}")
    axes[0].legend(loc="upper right", fontsize=9)
    axes[0].grid(True, alpha=0.3)

    axes[1].plot(t * 1e3, diff, linewidth=0.5, color="tab:purple")
    axes[1].axhline(0, color="black", linewidth=0.5)
    axes[1].set_ylabel("A - B (V)")
    axes[1].set_title(f"Diferencia punto a punto  |  "
                      f"max |dif| = {max_abs:.3f} V  |  media |dif| = {mean_abs:.3f} V")
    axes[1].grid(True, alpha=0.3)
    for i in idx_sorted[:5]:
        axes[1].axvline(t[i] * 1e3, color="orange", linewidth=0.8, linestyle="--", alpha=0.6)

    axes[2].bar(win_centers * 1e3, win_corrs,
                width=(win_size * dt) * 1e3 * 0.9,
                color=["tab:green" if c > 0.9 else "tab:olive" if c > 0.5 else "tab:red"
                       for c in win_corrs],
                edgecolor="black", linewidth=0.3)
    axes[2].axhline(1.0, color="black", linewidth=0.4, linestyle=":")
    axes[2].axhline(0.0, color="black", linewidth=0.4)
    axes[2].set_ylabel("Pearson por ventana")
    axes[2].set_xlabel("Tiempo (ms)")
    axes[2].set_title(f"Correlacion por ventana  ({N_WINDOWS} ventanas)  "
                      "-- verde: >0.9  |  oliva: 0.5-0.9  |  rojo: <0.5")
    axes[2].set_ylim([-1.05, 1.05])
    axes[2].grid(True, alpha=0.3, axis="y")

    fig.tight_layout()
    out = "compare_result.png"
    fig.savefig(out, dpi=120)
    print(f"Grafica guardada en '{out}'.")


if __name__ == "__main__":
    main()
