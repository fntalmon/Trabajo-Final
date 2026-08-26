"""
Runner principal para todos los benchmarks.
Ejecuta los 4 escenarios en secuencia.
Guarda resultados en results/*.json para posterior generación de gráficos.

Uso:
    python main.py              # Ejecutar todos los benchmarks
    python main.py insertions   # Solo inserciones masivas
    python main.py search       # Solo búsqueda intensiva
    python main.py range        # Solo consultas por rango
    python main.py memory       # Solo eficiencia de memoria
"""

import sys
import time


def run_insertions():
    print("\n" + "#" * 80)
    print("# BENCHMARK 1: INSERCIONES MASIVAS")
    print("#" * 80)
    from benchmarks.bench_insertions import run_insertion_benchmarks, print_results, save_results
    results = run_insertion_benchmarks()
    print_results(results)
    save_results(results)
    return results


def run_search():
    print("\n" + "#" * 80)
    print("# BENCHMARK 2: BÚSQUEDA INTENSIVA")
    print("#" * 80)
    from benchmarks.bench_search import run_search_benchmarks, print_results, save_results
    results = run_search_benchmarks()
    print_results(results)
    save_results(results)
    return results


def run_range():
    print("\n" + "#" * 80)
    print("# BENCHMARK 3: CONSULTAS POR RANGO")
    print("#" * 80)
    from benchmarks.bench_range import run_range_benchmarks, print_results, save_results
    results = run_range_benchmarks()
    print_results(results)
    save_results(results)
    return results


def run_memory():
    print("\n" + "#" * 80)
    print("# BENCHMARK 4: EFICIENCIA DE MEMORIA")
    print("#" * 80)
    from benchmarks.bench_memory import run_memory_benchmarks, print_results, save_results
    results = run_memory_benchmarks()
    print_results(results)
    save_results(results)
    return results


BENCHMARKS = {
    'insertions': run_insertions,
    'search': run_search,
    'range': run_range,
    'memory': run_memory,
}


def main():
    if len(sys.argv) > 1:
        name = sys.argv[1].lower()
        if name in BENCHMARKS:
            start = time.perf_counter()
            BENCHMARKS[name]()
            elapsed = time.perf_counter() - start
            print(f"\nTiempo total: {elapsed:.2f}s")
        else:
            print(f"Benchmark desconocido: {name}")
            print(f"Opciones: {', '.join(BENCHMARKS.keys())}")
            sys.exit(1)
    else:
        print("=" * 80)
        print("EVALUACIÓN EMPÍRICA DE ESTRUCTURAS DE DATOS")
        print("Teoría vs Rendimiento Real")
        print("=" * 80)
        print(f"\nPython {sys.version}")
        print(f"Ejecutando todos los benchmarks...\n")

        total_start = time.perf_counter()

        for name, func in BENCHMARKS.items():
            bench_start = time.perf_counter()
            func()
            bench_elapsed = time.perf_counter() - bench_start
            print(f"\n[{name}] completado en {bench_elapsed:.2f}s")

        total_elapsed = time.perf_counter() - total_start
        print(f"\n{'=' * 80}")
        print(f"TODOS LOS BENCHMARKS COMPLETADOS en {total_elapsed:.2f}s")
        print(f"{'=' * 80}")


if __name__ == '__main__':
    main()
