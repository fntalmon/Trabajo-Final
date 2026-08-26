"""
Generador de gráficos a partir de resultados de benchmarks (results/*.json).
Genera figuras correspondientes a las tablas y figuras del informe.

Uso:
    python graphs.py                # Genera todos los gráficos
    python graphs.py insertions     # Solo gráfico de inserciones
    python graphs.py search         # Solo gráfico de búsquedas
    python graphs.py range          # Solo gráfico de range queries
    python graphs.py memory         # Solo gráfico de memoria
"""

import json
import os
import sys

import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np

RESULTS_DIR = 'results'
GRAPHS_DIR = 'graphs'

# Colores consistentes por estructura
COLORS = {
    'LinkedList': '#8B4513',
    'HashTable': '#2196F3',
    'RedBlackTree': '#F44336',
    'SkipList': '#4CAF50',
    'BTree': '#FF9800',
}

LABELS = {
    'LinkedList': 'Linked List',
    'HashTable': 'Hash Table',
    'RedBlackTree': 'Red-Black Tree',
    'SkipList': 'Skip List',
    'BTree': 'B-Tree (t=50)',
}


def load_json(filename):
    path = os.path.join(RESULTS_DIR, filename)
    if not os.path.exists(path):
        print(f"Archivo no encontrado: {path}")
        print(f"Ejecutá primero: python main.py")
        return None
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def ensure_graphs_dir():
    os.makedirs(GRAPHS_DIR, exist_ok=True)


def graph_insertions():
    """Figura 1: Rendimiento de inserciones masivas (500K elementos)."""
    data = load_json('bench_insertions.json')
    if data is None:
        return

    results = data['results']

    # Use the largest size available per structure
    structures_order = ['LinkedList', 'HashTable', 'BTree', 'RedBlackTree', 'SkipList']
    seq_ops = []
    rand_ops = []
    labels = []
    colors = []

    for name in structures_order:
        if name not in results:
            continue
        struct_data = results[name]

        # Find largest size
        sizes = set()
        for key in struct_data:
            size = int(key.split('_')[0])
            sizes.add(size)
        max_size = max(sizes)

        seq_key = f"{max_size}_sequential"
        rand_key = f"{max_size}_random"

        if seq_key in struct_data and rand_key in struct_data:
            seq_ops.append(struct_data[seq_key]['avg_ops'])
            rand_ops.append(struct_data[rand_key]['avg_ops'])
            label = LABELS.get(name, name)
            if name == 'LinkedList':
                label += f' ({max_size // 1000}K)*'
            labels.append(label)
            colors.append(COLORS[name])

    x = np.arange(len(labels))
    width = 0.35

    fig, ax = plt.subplots(figsize=(12, 7))
    bars1 = ax.bar(x - width / 2, seq_ops, width, label='Secuencial', color=colors, alpha=0.9, edgecolor='black', linewidth=0.5)
    bars2 = ax.bar(x + width / 2, rand_ops, width, label='Aleatorio', color=colors, alpha=0.5, edgecolor='black', linewidth=0.5, hatch='//')

    ax.set_ylabel('Operaciones por segundo (ops/s)', fontsize=12)
    ax.set_title('Rendimiento de Inserciones Masivas\n(mayor tamaño disponible por estructura)', fontsize=14, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=10)
    ax.legend(fontsize=11)
    ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda val, pos: f'{val:,.0f}'))
    ax.grid(axis='y', alpha=0.3)

    # Add degradation labels
    for i in range(len(seq_ops)):
        degradation = seq_ops[i] / rand_ops[i] if rand_ops[i] > 0 else 0
        ax.annotate(f'{degradation:.1f}x', xy=(x[i], max(seq_ops[i], rand_ops[i])),
                    xytext=(0, 8), textcoords='offset points', ha='center', fontsize=9, fontweight='bold')

    plt.tight_layout()
    ensure_graphs_dir()
    path = os.path.join(GRAPHS_DIR, 'fig1_inserciones.png')
    plt.savefig(path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"Guardado: {path}")

    # Also: scalability chart across sizes
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))

    for ax_idx, order in enumerate(['sequential', 'random']):
        ax = axes[ax_idx]
        for name in structures_order:
            if name not in results:
                continue

            sizes_list = []
            ops_list = []
            for key, metrics in sorted(results[name].items()):
                if key.endswith(f'_{order}'):
                    size = int(key.split('_')[0])
                    sizes_list.append(size)
                    ops_list.append(metrics['avg_ops'])

            if sizes_list:
                ax.plot(sizes_list, ops_list, 'o-', label=LABELS.get(name, name),
                        color=COLORS[name], linewidth=2, markersize=6)

        ax.set_xlabel('Cantidad de elementos', fontsize=11)
        ax.set_ylabel('Operaciones/s', fontsize=11)
        title = 'Secuencial' if order == 'sequential' else 'Aleatorio'
        ax.set_title(f'Inserción {title}', fontsize=12, fontweight='bold')
        ax.legend(fontsize=9)
        ax.grid(alpha=0.3)
        ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda val, pos: f'{val:,.0f}'))
        ax.xaxis.set_major_formatter(ticker.FuncFormatter(lambda val, pos: f'{val / 1000:.0f}K'))

    plt.suptitle('Escalabilidad de Inserciones por Tamaño de Dataset', fontsize=14, fontweight='bold')
    plt.tight_layout()
    path = os.path.join(GRAPHS_DIR, 'fig1b_escalabilidad_inserciones.png')
    plt.savefig(path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"Guardado: {path}")


def graph_search():
    """Figura 2: Latencias de búsqueda por percentil (escala logarítmica)."""
    data = load_json('bench_search.json')
    if data is None:
        return

    results = data['results']

    structures_order = ['HashTable', 'RedBlackTree', 'SkipList', 'BTree', 'LinkedList']

    # Use maximum search count per structure
    p50_vals, p95_vals, p99_vals = [], [], []
    throughputs = []
    labels = []
    colors = []

    for name in structures_order:
        if name not in results:
            continue
        struct_data = results[name]
        max_count = str(max(int(k) for k in struct_data))
        metrics = struct_data[max_count]

        p50_vals.append(metrics['p50'])
        p95_vals.append(metrics['p95'])
        p99_vals.append(metrics['p99'])
        throughputs.append(metrics['throughput'])
        labels.append(LABELS.get(name, name))
        colors.append(COLORS[name])

    x = np.arange(len(labels))
    width = 0.25

    fig, ax = plt.subplots(figsize=(12, 7))
    bars1 = ax.bar(x - width, p50_vals, width, label='p50', color=colors, alpha=0.9, edgecolor='black', linewidth=0.5)
    bars2 = ax.bar(x, p95_vals, width, label='p95', color=colors, alpha=0.6, edgecolor='black', linewidth=0.5, hatch='//')
    bars3 = ax.bar(x + width, p99_vals, width, label='p99', color=colors, alpha=0.35, edgecolor='black', linewidth=0.5, hatch='xx')

    ax.set_yscale('log')
    ax.set_ylabel('Latencia (μs) - Escala Logarítmica', fontsize=12)
    ax.set_title('Latencias de Búsqueda por Percentil\n(500K elementos, 100K búsquedas; Linked List: 100K elem, 5K búsq.)',
                 fontsize=13, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=10)
    ax.legend(fontsize=11, loc='upper left')
    ax.grid(axis='y', alpha=0.3, which='both')

    # Throughput annotation
    for i, tp in enumerate(throughputs):
        ax.annotate(f'{tp:,.0f} ops/s', xy=(x[i], p99_vals[i]),
                    xytext=(0, 12), textcoords='offset points', ha='center', fontsize=8, fontweight='bold')

    plt.tight_layout()
    ensure_graphs_dir()
    path = os.path.join(GRAPHS_DIR, 'fig2_busquedas_latencia.png')
    plt.savefig(path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"Guardado: {path}")

    # Throughput bar chart
    fig, ax = plt.subplots(figsize=(10, 6))
    bars = ax.bar(labels, throughputs, color=colors, edgecolor='black', linewidth=0.5)
    ax.set_ylabel('Búsquedas por segundo', fontsize=12)
    ax.set_title('Throughput de Búsqueda', fontsize=14, fontweight='bold')
    ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda val, pos: f'{val:,.0f}'))
    ax.grid(axis='y', alpha=0.3)
    ax.set_yscale('log')

    for bar, tp in zip(bars, throughputs):
        ax.annotate(f'{tp:,.0f}', xy=(bar.get_x() + bar.get_width() / 2, tp),
                    xytext=(0, 5), textcoords='offset points', ha='center', fontsize=9, fontweight='bold')

    plt.tight_layout()
    path = os.path.join(GRAPHS_DIR, 'fig2b_busquedas_throughput.png')
    plt.savefig(path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"Guardado: {path}")


def graph_range():
    """Figura 3: Rendimiento de consultas por rango."""
    data = load_json('bench_range.json')
    if data is None:
        return

    results = data['results']

    # Ordered structures first, then unordered (use max query count)
    ordered = ['SkipList', 'RedBlackTree', 'BTree']

    # For hash table and linked list, pick the entry with the most queries
    unordered_entries = {}
    for key, metrics in results.items():
        for prefix in ['HashTable', 'LinkedList']:
            if key.startswith(prefix + '_'):
                name = prefix
                if name not in unordered_entries or metrics['num_queries'] > unordered_entries[name]['num_queries']:
                    unordered_entries[name] = metrics

    latencies = []
    query_rates = []
    labels = []
    colors = []
    datasets = []

    for name in ordered:
        if name in results:
            latencies.append(results[name]['avg_latency_us'])
            query_rates.append(results[name]['query_rate'])
            labels.append(LABELS.get(name, name))
            colors.append(COLORS[name])
            datasets.append(f"{results[name]['dataset'] // 1000}K")

    for name in ['LinkedList', 'HashTable']:
        if name in unordered_entries:
            latencies.append(unordered_entries[name]['avg_latency_us'])
            query_rates.append(unordered_entries[name]['query_rate'])
            label = LABELS.get(name, name) + '*'
            labels.append(label)
            colors.append(COLORS[name])
            datasets.append(f"{unordered_entries[name]['dataset'] // 1000}K")

    # Chart 1: Latency comparison
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

    bars = ax1.bar(labels, latencies, color=colors, edgecolor='black', linewidth=0.5)
    ax1.set_ylabel('Latencia Promedio (μs)', fontsize=12)
    ax1.set_title('Latencia de Range Queries', fontsize=13, fontweight='bold')
    ax1.set_yscale('log')
    ax1.grid(axis='y', alpha=0.3, which='both')
    ax1.tick_params(axis='x', rotation=15)

    for bar, lat, ds in zip(bars, latencies, datasets):
        ax1.annotate(f'{lat:.1f} μs\n({ds})', xy=(bar.get_x() + bar.get_width() / 2, lat),
                     xytext=(0, 8), textcoords='offset points', ha='center', fontsize=8, fontweight='bold')

    bars2 = ax2.bar(labels, query_rates, color=colors, edgecolor='black', linewidth=0.5)
    ax2.set_ylabel('Consultas por segundo (q/s)', fontsize=12)
    ax2.set_title('Query Rate de Range Queries', fontsize=13, fontweight='bold')
    ax2.set_yscale('log')
    ax2.grid(axis='y', alpha=0.3, which='both')
    ax2.tick_params(axis='x', rotation=15)

    for bar, rate in zip(bars2, query_rates):
        ax2.annotate(f'{rate:,.0f}', xy=(bar.get_x() + bar.get_width() / 2, rate),
                     xytext=(0, 5), textcoords='offset points', ha='center', fontsize=8, fontweight='bold')

    plt.suptitle('Consultas por Rango (Range Queries)\n* HashTable y LinkedList con dataset reducido (50K) por O(n)',
                 fontsize=13, fontweight='bold')
    plt.tight_layout()
    ensure_graphs_dir()
    path = os.path.join(GRAPHS_DIR, 'fig3_range_queries.png')
    plt.savefig(path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"Guardado: {path}")


def graph_memory():
    """Figura 4: Eficiencia de memoria por estructura."""
    data = load_json('bench_memory.json')
    if data is None:
        return

    results = data['results']

    # Sort by elements (most efficient first)
    sorted_names = sorted(results.keys(), key=lambda n: results[n]['elements'], reverse=True)

    labels = [LABELS.get(n, n) for n in sorted_names]
    elements = [results[n]['elements'] for n in sorted_names]
    bytes_per_elem = [results[n]['bytes_per_element'] for n in sorted_names]
    colors = [COLORS.get(n, '#999999') for n in sorted_names]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

    # Chart 1: Elements stored in 256 MB
    bars1 = ax1.bar(labels, elements, color=colors, edgecolor='black', linewidth=0.5)
    ax1.set_ylabel('Elementos almacenados', fontsize=12)
    ax1.set_title('Elementos en 256 MB', fontsize=13, fontweight='bold')
    ax1.yaxis.set_major_formatter(ticker.FuncFormatter(lambda val, pos: f'{val / 1e6:.1f}M' if val >= 1e6 else f'{val / 1e3:.0f}K'))
    ax1.grid(axis='y', alpha=0.3)
    ax1.tick_params(axis='x', rotation=15)

    for bar, elem in zip(bars1, elements):
        ax1.annotate(f'{elem:,}', xy=(bar.get_x() + bar.get_width() / 2, elem),
                     xytext=(0, 5), textcoords='offset points', ha='center', fontsize=8, fontweight='bold')

    # Chart 2: Bytes per element
    bars2 = ax2.bar(labels, bytes_per_elem, color=colors, edgecolor='black', linewidth=0.5)
    ax2.set_ylabel('Bytes por elemento', fontsize=12)
    ax2.set_title('Sobrecarga de Memoria', fontsize=13, fontweight='bold')
    ax2.grid(axis='y', alpha=0.3)
    ax2.tick_params(axis='x', rotation=15)

    for bar, bpe in zip(bars2, bytes_per_elem):
        ax2.annotate(f'{bpe:.1f} B', xy=(bar.get_x() + bar.get_width() / 2, bpe),
                     xytext=(0, 5), textcoords='offset points', ha='center', fontsize=8, fontweight='bold')

    plt.suptitle('Eficiencia de Memoria (límite 256 MB)', fontsize=14, fontweight='bold')
    plt.tight_layout()
    ensure_graphs_dir()
    path = os.path.join(GRAPHS_DIR, 'fig4_memoria.png')
    plt.savefig(path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"Guardado: {path}")


def graph_summary():
    """Tabla resumen visual: ganador por categoría."""
    categories = ['Búsquedas\npor clave', 'Range\nQueries', 'Eficiencia\nde memoria', 'Inserciones\n(throughput)', 'Estabilidad\nseq/rand']

    # Try loading all results
    search_data = load_json('bench_search.json')
    range_data = load_json('bench_range.json')
    memory_data = load_json('bench_memory.json')
    insert_data = load_json('bench_insertions.json')

    if not all([search_data, range_data, memory_data, insert_data]):
        print("No se pueden generar el gráfico resumen sin todos los resultados.")
        return

    # Extract winners and losers with values
    winners = []
    losers = []

    # 1. Search: best/worst p50
    sr = search_data['results']
    search_p50 = {}
    for name, sd in sr.items():
        max_count = str(max(int(k) for k in sd))
        search_p50[name] = sd[max_count]['p50']
    best_search = min(search_p50, key=search_p50.get)
    worst_search = max(search_p50, key=search_p50.get)
    winners.append((LABELS[best_search], f'{search_p50[best_search]:.2f} μs'))
    losers.append((LABELS[worst_search], f'{search_p50[worst_search]:.1f} μs'))

    # 2. Range: best/worst query rate (ordered only for best)
    rr = range_data['results']
    ordered_rr = {k: v for k, v in rr.items() if k in ['SkipList', 'RedBlackTree', 'BTree']}
    best_range = max(ordered_rr, key=lambda n: rr[n]['query_rate'])
    # Worst is hash table or linked list
    all_rr = {}
    for k, v in rr.items():
        name = k.split('_')[0] if '_' in k else k
        if name not in all_rr or v['query_rate'] < all_rr[name]:
            all_rr[name] = v['query_rate']
    worst_range_name = min(all_rr, key=all_rr.get)
    winners.append((LABELS.get(best_range, best_range), f'{rr[best_range]["avg_latency_us"]:.1f} μs'))
    losers.append((LABELS.get(worst_range_name, worst_range_name), f'{all_rr[worst_range_name]:.0f} q/s'))

    # 3. Memory
    mr = memory_data['results']
    best_mem = max(mr, key=lambda n: mr[n]['elements'])
    worst_mem = min(mr, key=lambda n: mr[n]['elements'])
    winners.append((LABELS[best_mem], f'{mr[best_mem]["bytes_per_element"]:.0f} B/elem'))
    losers.append((LABELS[worst_mem], f'{mr[worst_mem]["bytes_per_element"]:.0f} B/elem'))

    # 4. Insertions: highest random throughput
    ir = insert_data['results']
    insert_throughput = {}
    for name, sd in ir.items():
        max_size = max(int(k.split('_')[0]) for k in sd)
        rand_key = f"{max_size}_random"
        if rand_key in sd:
            insert_throughput[name] = sd[rand_key]['avg_ops']
    best_insert = max(insert_throughput, key=insert_throughput.get)
    worst_insert = min(insert_throughput, key=insert_throughput.get)
    winners.append((LABELS[best_insert], f'{insert_throughput[best_insert]:,.0f} ops/s'))
    losers.append((LABELS[worst_insert], f'{insert_throughput[worst_insert]:,.0f} ops/s'))

    # 5. Stability: lowest degradation ratio
    degradation = {}
    for name, sd in ir.items():
        max_size = max(int(k.split('_')[0]) for k in sd)
        seq_key = f"{max_size}_sequential"
        rand_key = f"{max_size}_random"
        if seq_key in sd and rand_key in sd:
            ratio = sd[seq_key]['avg_ops'] / sd[rand_key]['avg_ops'] if sd[rand_key]['avg_ops'] > 0 else float('inf')
            degradation[name] = ratio
    best_stable = min(degradation, key=degradation.get)
    worst_stable = max(degradation, key=degradation.get)
    winners.append((LABELS[best_stable], f'{degradation[best_stable]:.2f}x'))
    losers.append((LABELS[worst_stable], f'{degradation[worst_stable]:.2f}x'))

    # Create table figure
    fig, ax = plt.subplots(figsize=(12, 4))
    ax.axis('off')

    table_data = []
    for i in range(len(categories)):
        table_data.append([categories[i].replace('\n', ' '), f'{winners[i][0]}\n({winners[i][1]})', f'{losers[i][0]}\n({losers[i][1]})'])

    table = ax.table(cellText=table_data, colLabels=['Categoría', 'Ganador', 'Perdedor'],
                     cellLoc='center', loc='center', colWidths=[0.3, 0.35, 0.35])
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1, 2)

    # Style headers
    for j in range(3):
        table[0, j].set_facecolor('#333333')
        table[0, j].set_text_props(color='white', fontweight='bold')

    # Style winner/loser columns
    for i in range(1, len(table_data) + 1):
        table[i, 1].set_facecolor('#C8E6C9')
        table[i, 2].set_facecolor('#FFCDD2')

    ax.set_title('Resumen: Ganador y Perdedor por Categoría', fontsize=14, fontweight='bold', pad=20)
    plt.tight_layout()
    ensure_graphs_dir()
    path = os.path.join(GRAPHS_DIR, 'fig5_resumen.png')
    plt.savefig(path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"Guardado: {path}")


GRAPHS = {
    'insertions': graph_insertions,
    'search': graph_search,
    'range': graph_range,
    'memory': graph_memory,
    'summary': graph_summary,
}


def main():
    if len(sys.argv) > 1:
        name = sys.argv[1].lower()
        if name in GRAPHS:
            GRAPHS[name]()
        elif name == 'all':
            for func in GRAPHS.values():
                func()
        else:
            print(f"Gráfico desconocido: {name}")
            print(f"Opciones: {', '.join(GRAPHS.keys())}, all")
            sys.exit(1)
    else:
        print("Generando todos los gráficos...")
        for name, func in GRAPHS.items():
            print(f"\n--- {name} ---")
            func()
        print(f"\nTodos los gráficos guardados en {GRAPHS_DIR}/")


if __name__ == '__main__':
    main()
