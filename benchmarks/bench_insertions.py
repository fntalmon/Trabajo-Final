"""
Benchmark 1: Inserciones masivas secuenciales y aleatorias.
Evalúa throughput (ops/s) con 100K, 250K, 500K elementos.
3 repeticiones, gc deshabilitado, seed=42.
Linked List medida con 250K máximo.
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
SIZES = [100_000, 250_000, 500_000]
LINKED_LIST_MAX = 250_000


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


def benchmark_insertion(name, size, order='sequential'):
    rng = random.Random(SEED)

    if order == 'sequential':
        data = list(range(size))
    else:
        data = list(range(size))
        rng.shuffle(data)

    struct = create_structure(name)

    gc.disable()
    start = time.perf_counter()
    for key in data:
        struct.insert(key)
    elapsed = time.perf_counter() - start
    gc.enable()

    ops_per_sec = size / elapsed
    return elapsed, ops_per_sec


def run_insertion_benchmarks():
    structures = ['LinkedList', 'HashTable', 'RedBlackTree', 'SkipList', 'BTree']

    results = {}

    for name in structures:
        results[name] = {}
        for size in SIZES:
            if name == 'LinkedList' and size > LINKED_LIST_MAX:
                continue

            for order in ['sequential', 'random']:
                times = []
                ops_list = []
                for rep in range(REPETITIONS):
                    elapsed, ops = benchmark_insertion(name, size, order)
                    times.append(elapsed)
                    ops_list.append(ops)

                avg_time = sum(times) / len(times)
                avg_ops = sum(ops_list) / len(ops_list)
                std_time = (sum((t - avg_time) ** 2 for t in times) / len(times)) ** 0.5

                key = (size, order)
                results[name][key] = {
                    'avg_time': avg_time,
                    'avg_ops': avg_ops,
                    'std_time': std_time,
                }

    return results


def save_results(results, path='results/bench_insertions.json'):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    serializable = {}
    for name, data in results.items():
        serializable[name] = {}
        for (size, order), metrics in data.items():
            key = f"{size}_{order}"
            serializable[name][key] = metrics
    with open(path, 'w', encoding='utf-8') as f:
        json.dump({'benchmark': 'insertions', 'results': serializable}, f, indent=2, ensure_ascii=False)
    print(f"\nResultados guardados en {path}")


def print_results(results):
    print("=" * 80)
    print("BENCHMARK 1: INSERCIONES MASIVAS")
    print("=" * 80)

    structures = ['LinkedList', 'HashTable', 'RedBlackTree', 'SkipList', 'BTree']

    for size in SIZES:
        print(f"\n--- {size:,} elementos ---")
        print(f"{'Estructura':<20} {'Secuencial (ops/s)':>20} {'Aleatorio (ops/s)':>20} {'Degradación':>15}")
        print("-" * 75)
        for name in structures:
            seq_key = (size, 'sequential')
            rand_key = (size, 'random')

            if seq_key in results[name] and rand_key in results[name]:
                seq_ops = results[name][seq_key]['avg_ops']
                rand_ops = results[name][rand_key]['avg_ops']
                degradation = seq_ops / rand_ops if rand_ops > 0 else float('inf')
                print(f"{name:<20} {seq_ops:>20,.0f} {rand_ops:>20,.0f} {degradation:>14.2f}x")
            elif seq_key in results[name]:
                seq_ops = results[name][seq_key]['avg_ops']
                print(f"{name:<20} {seq_ops:>20,.0f} {'N/A':>20} {'N/A':>15}")

    # Print summary for 500K (or max available)
    print(f"\n{'=' * 80}")
    print("RESUMEN (mayor tamaño disponible por estructura)")
    print(f"{'=' * 80}")
    print(f"{'Estructura':<20} {'Secuencial (ops/s)':>20} {'Aleatorio (ops/s)':>20} {'Degradación':>15}")
    print("-" * 75)
    for name in structures:
        max_size = LINKED_LIST_MAX if name == 'LinkedList' else 500_000
        seq_key = (max_size, 'sequential')
        rand_key = (max_size, 'random')
        if seq_key in results[name] and rand_key in results[name]:
            seq_ops = results[name][seq_key]['avg_ops']
            rand_ops = results[name][rand_key]['avg_ops']
            degradation = seq_ops / rand_ops if rand_ops > 0 else float('inf')
            print(f"{name:<20} {seq_ops:>20,.0f} {rand_ops:>20,.0f} {degradation:>14.2f}x")


if __name__ == '__main__':
    results = run_insertion_benchmarks()
    print_results(results)
    save_results(results)
