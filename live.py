"""
live.py

Compara una traza nueva contra todos los CSVs en profiling_set/
y muestra el TOP 5 mas parecidos por correlacion de Pearson.

USO:
    python live.py
"""

import os
from scope_utils import PROFILING_DIR, list_csv_files, parse_scope_csv, pearson


def main():
    ref_files = list_csv_files()

    name = input("Traza a comparar: ").strip() + ".CSV"
    path = name
    if not os.path.isfile(path):
        print(f"Error: no existe el archivo '{path}'.")
        return

    _, query = parse_scope_csv(path)
    print(f"\nComparando '{name}' contra {len(ref_files)} trazas...\n")

    results = []
    for ref in ref_files:
        if ref.upper() == name.upper():
            continue
        _, trace = parse_scope_csv(os.path.join(PROFILING_DIR, ref))
        results.append((ref, pearson(query, trace)))

    results.sort(key=lambda x: x[1], reverse=True)

    print("=" * 40)
    print(f"TOP {min(5, len(results))} MAS PARECIDOS")
    print("=" * 40)
    for rank, (ref, r) in enumerate(results[:5], 1):
        bar = "#" * int((r + 1) / 2 * 20)
        print(f"  {rank}. {os.path.splitext(ref)[0]:<6}  Pearson = {r:+.6f}  [{bar:<20}]")
    print()


if __name__ == "__main__":
    main()
