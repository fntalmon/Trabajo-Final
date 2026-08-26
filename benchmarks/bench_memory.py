"""
Benchmark 4: Eficiencia de memoria.
Límite de 256 MB. Se insertan elementos hasta alcanzar el límite.
Se mide cuántos elementos caben y bytes/elemento.
Se usa psutil.Process().memory_info().rss.
gc deshabilitado durante inserciones, seed=42.
"""

import gc
import json
import sys
import os
import random

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

try:
    import psutil
except ImportError:
    print("psutil no está instalado. Ejecutar: pip install psutil")
    sys.exit(1)

from structures import LinkedList, HashTable, RedBlackTree, SkipList, BTree

SEED = 42
MEMORY_LIMIT_MB = 256
MEMORY_LIMIT_BYTES = MEMORY_LIMIT_MB * 1024 * 1024
BATCH_SIZE = 1000


def get_rss():
    process = psutil.Process(os.getpid())
    return process.memory_info().rss


def create_structure(name):
    if name == 'LinkedList':
        return LinkedList()
    elif name == 'HashTable':
        return HashTable(capacity=16, load_factor_threshold=0.75)
    elif name == 'RedBlackTree':
        return RedBlackTree()
    elif name == 'SkipList':
        return SkipList(max_level=16, p=0.5, seed=SEED)
    elif name == 'BTree':
        return BTree(t=50)


def benchmark_memory(name):
    # Force collection before measuring baseline
    gc.collect()
    baseline_rss = get_rss()

    struct = create_structure(name)
    rng = random.Random(SEED)

    count = 0
    gc.disable()

    while True:
        for _ in range(BATCH_SIZE):
            key = rng.randint(0, 10_000_000)
            struct.insert(key, key)
            count += 1

        current_rss = get_rss()
        used = current_rss - baseline_rss
        if used >= MEMORY_LIMIT_BYTES:
            break

    gc.enable()

    current_rss = get_rss()
    used = current_rss - baseline_rss
    bytes_per_element = used / count if count > 0 else 0

    return {
        'elements': count,
        'memory_used_bytes': used,
        'bytes_per_element': bytes_per_element,
    }


def run_memory_benchmarks():
    structures = ['BTree', 'LinkedList', 'RedBlackTree', 'SkipList', 'HashTable']
    results = {}

    for name in structures:
        print(f"Testing memory efficiency for {name}...")
        results[name] = benchmark_memory(name)
        print(f"  {name}: {results[name]['elements']:,} elements, "
              f"{results[name]['bytes_per_element']:.2f} bytes/element")

        # Force cleanup before next structure
        gc.collect()

    return results


def save_results(results, path='results/bench_memory.json'):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump({'benchmark': 'memory', 'results': results}, f, indent=2, ensure_ascii=False)
    print(f"\nResultados guardados en {path}")


def print_results(results):
    print("\n" + "=" * 80)
    print(f"BENCHMARK 4: EFICIENCIA DE MEMORIA (límite {MEMORY_LIMIT_MB} MB)")
    print("=" * 80)

    # Sort by elements (most efficient first)
    sorted_names = sorted(results.keys(), key=lambda n: results[n]['elements'], reverse=True)

    best = results[sorted_names[0]]['bytes_per_element']

    print(f"\n{'Estructura':<20} {'Elementos':>15} {'Bytes/Elemento':>18} {'Eficiencia vs mejor':>22}")
    print("-" * 75)
    for name in sorted_names:
        r = results[name]
        ratio = r['bytes_per_element'] / best if best > 0 else 0
        efficiency = f"{ratio:.2f}x peor" if ratio > 1.01 else "—"
        print(f"{name:<20} {r['elements']:>15,} {r['bytes_per_element']:>18.2f} {efficiency:>22}")


if __name__ == '__main__':
    results = run_memory_benchmarks()
    print_results(results)
    save_results(results)
