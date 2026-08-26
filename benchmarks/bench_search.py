"""
Benchmark 2: Búsqueda intensiva.
Estructuras pre-pobladas con 500K elementos (100K para Linked List).
Se ejecutan 10K, 50K y 100K búsquedas (5K para Linked List).
Hit rate: 80% claves existentes, 20% inexistentes.
Se reportan percentiles p50, p95, p99 y búsquedas/s.
3 repeticiones, gc deshabilitado, seed=42.
"""

import gc
import json
import time
import random
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from structures import LinkedList, HashTable, RedBlackTree, SkipList, BTree

SEED = 42
REPETITIONS = 3
PRELOAD_SIZE = 500_000
LINKED_LIST_PRELOAD = 100_000
SEARCH_COUNTS = [10_000, 50_000, 100_000]
LINKED_LIST_SEARCHES = 5_000
HIT_RATE = 0.80


def create_and_populate(name, size):
    rng = random.Random(SEED)
    data = list(range(size))
    rng.shuffle(data)

    if name == 'LinkedList':
        struct = LinkedList()
    elif name == 'HashTable':
        struct = HashTable(capacity=16, load_factor_threshold=0.75)
    elif name == 'RedBlackTree':
        struct = RedBlackTree()
    elif name == 'SkipList':
        struct = SkipList(max_level=16, p=0.5, seed=SEED)
    elif name == 'BTree':
        struct = BTree(t=50)

    for key in data:
        struct.insert(key)

    return struct, size


def generate_search_keys(size, num_searches, hit_rate, seed):
    rng = random.Random(seed)
    keys = []
    num_hits = int(num_searches * hit_rate)
    num_misses = num_searches - num_hits

    # Existing keys
    for _ in range(num_hits):
        keys.append(rng.randint(0, size - 1))

    # Non-existing keys
    for _ in range(num_misses):
        keys.append(rng.randint(size, size * 2))

    rng.shuffle(keys)
    return keys


def benchmark_search(struct, search_keys):
    latencies = []

    gc.disable()
    for key in search_keys:
        start = time.perf_counter()
        struct.search(key)
        end = time.perf_counter()
        latencies.append(end - start)
    gc.enable()

    return latencies


def compute_percentiles(latencies):
    sorted_lat = sorted(latencies)
    n = len(sorted_lat)
    p50 = sorted_lat[int(n * 0.50)]
    p95 = sorted_lat[int(n * 0.95)]
    p99 = sorted_lat[int(n * 0.99)]
    return p50, p95, p99


def run_search_benchmarks():
    structures = ['HashTable', 'RedBlackTree', 'SkipList', 'BTree', 'LinkedList']

    results = {}

    for name in structures:
        results[name] = {}
        preload = LINKED_LIST_PRELOAD if name == 'LinkedList' else PRELOAD_SIZE
        search_counts = [LINKED_LIST_SEARCHES] if name == 'LinkedList' else SEARCH_COUNTS

        print(f"Pre-populating {name} with {preload:,} elements...")
        struct, size = create_and_populate(name, preload)

        for num_searches in search_counts:
            all_p50, all_p95, all_p99, all_throughput = [], [], [], []

            for rep in range(REPETITIONS):
                search_keys = generate_search_keys(size, num_searches, HIT_RATE, SEED + rep)

                latencies = benchmark_search(struct, search_keys)
                p50, p95, p99 = compute_percentiles(latencies)
                total_time = sum(latencies)
                throughput = num_searches / total_time if total_time > 0 else 0

                all_p50.append(p50)
                all_p95.append(p95)
                all_p99.append(p99)
                all_throughput.append(throughput)

            results[name][num_searches] = {
                'p50': sum(all_p50) / len(all_p50) * 1e6,  # to microseconds
                'p95': sum(all_p95) / len(all_p95) * 1e6,
                'p99': sum(all_p99) / len(all_p99) * 1e6,
                'throughput': sum(all_throughput) / len(all_throughput),
            }
            print(f"  {name} - {num_searches:,} searches done.")

    return results


def save_results(results, path='results/bench_search.json'):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    serializable = {}
    for name, data in results.items():
        serializable[name] = {}
        for num_searches, metrics in data.items():
            serializable[name][str(num_searches)] = metrics
    with open(path, 'w', encoding='utf-8') as f:
        json.dump({'benchmark': 'search', 'results': serializable}, f, indent=2, ensure_ascii=False)
    print(f"\nResultados guardados en {path}")


def print_results(results):
    print("\n" + "=" * 90)
    print("BENCHMARK 2: BÚSQUEDA INTENSIVA")
    print("=" * 90)

    structures = ['HashTable', 'RedBlackTree', 'SkipList', 'BTree', 'LinkedList']

    # Main table (max search count per structure)
    print(f"\n{'Estructura':<20} {'p50 (μs)':>12} {'p95 (μs)':>12} {'p99 (μs)':>12} {'Búsquedas/s':>15}")
    print("-" * 71)
    for name in structures:
        max_searches = max(results[name].keys())
        r = results[name][max_searches]
        print(f"{name:<20} {r['p50']:>12.2f} {r['p95']:>12.2f} {r['p99']:>12.2f} {r['throughput']:>15,.0f}")

    # Detailed per search count
    for name in structures:
        print(f"\n--- {name} ---")
        print(f"{'Búsquedas':>12} {'p50 (μs)':>12} {'p95 (μs)':>12} {'p99 (μs)':>12} {'Throughput':>15}")
        for num_searches in sorted(results[name].keys()):
            r = results[name][num_searches]
            print(f"{num_searches:>12,} {r['p50']:>12.2f} {r['p95']:>12.2f} {r['p99']:>12.2f} {r['throughput']:>15,.0f}")


if __name__ == '__main__':
    results = run_search_benchmarks()
    print_results(results)
    save_results(results)
