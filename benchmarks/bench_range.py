"""
Benchmark 3: Consultas por rango (Range Queries).
Estructuras ordenadas (B-Tree, RB-Tree, Skip List): 100K consultas sobre 500K elementos.
Hash Table: 50-500 consultas sobre 50K elementos.
Linked List: 500-5000 consultas sobre 50K elementos.
Mide latencia promedio y query rate (q/s).
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

# Config per structure type
ORDERED_SIZE = 500_000
ORDERED_QUERIES = 100_000
UNORDERED_SIZE = 50_000
HASH_QUERIES = [50, 100, 500]
LINKED_QUERIES = [500, 1_000, 5_000]

# Range width: small ranges to keep k manageable
RANGE_WIDTH = 100


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


def generate_ranges(size, num_queries, seed):
    rng = random.Random(seed)
    ranges = []
    for _ in range(num_queries):
        low = rng.randint(0, size - RANGE_WIDTH - 1)
        high = low + RANGE_WIDTH
        ranges.append((low, high))
    return ranges


def benchmark_range_queries(struct, ranges):
    latencies = []

    gc.disable()
    for low, high in ranges:
        start = time.perf_counter()
        struct.range_query(low, high)
        end = time.perf_counter()
        latencies.append(end - start)
    gc.enable()

    return latencies


def run_range_benchmarks():
    results = {}

    # Ordered structures: 500K elements, 100K queries
    ordered_structures = ['SkipList', 'RedBlackTree', 'BTree']
    for name in ordered_structures:
        print(f"Pre-populating {name} with {ORDERED_SIZE:,} elements...")
        struct, size = create_and_populate(name, ORDERED_SIZE)

        all_latencies = []
        for rep in range(REPETITIONS):
            ranges = generate_ranges(size, ORDERED_QUERIES, SEED + rep)
            latencies = benchmark_range_queries(struct, ranges)
            all_latencies.append(latencies)
            print(f"  {name} - repetition {rep + 1} done.")

        avg_latency = sum(sum(l) / len(l) for l in all_latencies) / REPETITIONS
        avg_rate = sum(len(l) / sum(l) for l in all_latencies) / REPETITIONS
        results[name] = {
            'avg_latency_us': avg_latency * 1e6,
            'query_rate': avg_rate,
            'dataset': ORDERED_SIZE,
            'num_queries': ORDERED_QUERIES,
        }

    # Hash Table: 50K elements, fewer queries
    for name, query_counts in [('HashTable', HASH_QUERIES), ('LinkedList', LINKED_QUERIES)]:
        print(f"Pre-populating {name} with {UNORDERED_SIZE:,} elements...")
        struct, size = create_and_populate(name, UNORDERED_SIZE)

        for num_q in query_counts:
            all_latencies = []
            for rep in range(REPETITIONS):
                ranges = generate_ranges(size, num_q, SEED + rep)
                latencies = benchmark_range_queries(struct, ranges)
                all_latencies.append(latencies)

            avg_latency = sum(sum(l) / len(l) for l in all_latencies) / REPETITIONS
            avg_rate = sum(len(l) / sum(l) for l in all_latencies) / REPETITIONS

            result_key = f"{name}_{num_q}"
            results[result_key] = {
                'avg_latency_us': avg_latency * 1e6,
                'query_rate': avg_rate,
                'dataset': UNORDERED_SIZE,
                'num_queries': num_q,
            }
            print(f"  {name} - {num_q} queries done.")

    return results


def save_results(results, path='results/bench_range.json'):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump({'benchmark': 'range', 'results': results}, f, indent=2, ensure_ascii=False)
    print(f"\nResultados guardados en {path}")


def print_results(results):
    print("\n" + "=" * 90)
    print("BENCHMARK 3: CONSULTAS POR RANGO (RANGE QUERIES)")
    print("=" * 90)

    print(f"\n{'Estructura':<20} {'Latencia Avg (μs)':>20} {'Query Rate (q/s)':>20} {'Dataset':>12} {'Queries':>10}")
    print("-" * 82)

    # Ordered first
    for name in ['SkipList', 'RedBlackTree', 'BTree']:
        if name in results:
            r = results[name]
            print(f"{name:<20} {r['avg_latency_us']:>20.2f} {r['query_rate']:>20,.0f} {r['dataset']:>12,} {r['num_queries']:>10,}")

    # Unordered
    for prefix in ['LinkedList', 'HashTable']:
        for key, r in results.items():
            if key.startswith(prefix):
                display_name = key.replace('_', ' (') + 'q)'
                print(f"{display_name:<20} {r['avg_latency_us']:>20.2f} {r['query_rate']:>20,.0f} {r['dataset']:>12,} {r['num_queries']:>10,}")


if __name__ == '__main__':
    results = run_range_benchmarks()
    print_results(results)
    save_results(results)
