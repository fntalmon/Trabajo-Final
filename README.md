# Evaluación Empírica de Estructuras de Datos: Teoría vs Rendimiento Real

Proyecto final de carrera. Evaluación empírica del rendimiento de cinco estructuras de datos fundamentales —Tabla Hash, Árbol Red-Black, B-Tree, Skip List y Lista Enlazada— contrastando las complejidades teóricas (notación Big O) con el comportamiento real medido mediante benchmarks controlados.

Se implementaron versiones canónicas de cada estructura siguiendo algoritmos de referencia académica (Cormen et al., 2009; Pugh, 1990) en Python 3.12, y se ejecutaron benchmarks con datasets de hasta 500.000 elementos en cuatro escenarios: inserciones masivas, búsquedas intensivas, consultas por rango y eficiencia de memoria.

## Índice

- [Estructura del repositorio](#estructura-del-repositorio)
- [Requisitos](#requisitos)
- [Ejecutar los benchmarks](#ejecutar-los-benchmarks)
- [Generar los gráficos](#generar-los-gráficos)
- [Metodología de medición](#metodología-de-medición)
- [Resultados principales](#resultados-principales)

## Estructura del repositorio

```
structures/              Implementaciones de las 5 estructuras de datos
├── linked_list.py       Lista simplemente enlazada (Cormen, Cap. 10)
├── hash_table.py        Tabla Hash con chaining (Cormen, Cap. 11)
├── red_black_tree.py    Árbol Rojo-Negro (Cormen, Cap. 13)
├── skip_list.py         Skip List (Pugh, 1990)
└── btree.py             B-Tree t=50 (Cormen, Cap. 18)

benchmarks/              Scripts de cada benchmark
├── bench_insertions.py  Inserciones masivas
├── bench_search.py      Búsqueda intensiva
├── bench_range.py       Consultas por rango
└── bench_memory.py      Eficiencia de memoria

results/                 Resultados de benchmarks en JSON (ya incluidos)
graphs/                  Gráficos generados a partir de los resultados (ya incluidos)
main.py                  Runner principal de benchmarks
graphs.py                Generador de gráficos
requirements.txt         Dependencias
```

## Requisitos

- Python 3.12+
- `pip install -r requirements.txt` (psutil, matplotlib, numpy)

## Ejecutar los benchmarks

```bash
python main.py              # corre los 4 escenarios en secuencia (tarda varias horas)
python main.py insertions   # solo inserciones      (~30-60 min)
python main.py search       # solo búsqueda         (~20-40 min)
python main.py range        # solo consultas por rango (~30-60 min)
python main.py memory       # solo eficiencia de memoria (~10-20 min)
```

Cada benchmark imprime los resultados en consola y los guarda en `results/<nombre>.json`, sobreescribiendo el JSON existente. También se puede ejecutar cada script directamente: `python benchmarks/bench_insertions.py`, etc.

Los resultados son reproducibles gracias a un seed fijo (42) y a `gc.disable()` durante las mediciones. Los valores absolutos van a variar según el hardware; lo que se mantiene son las relaciones relativas entre estructuras.

## Generar los gráficos

Una vez que existen los JSON en `results/` (ya incluidos en este repo, o recién generados):

```bash
python graphs.py             # genera los 7 gráficos
python graphs.py insertions  # o uno individual: insertions | search | range | memory | summary
```

Los gráficos se regeneran a partir de los JSON sin necesidad de volver a correr los benchmarks, y se guardan en `graphs/`.

## Metodología de medición

- **Inserciones** (`bench_insertions.py`): throughput (`avg_ops`, ops/s) en modo secuencial y aleatorio, sobre 100K/250K/500K elementos (Linked List se mide hasta 250K por el tiempo que tardan las búsquedas posteriores).
- **Búsqueda** (`bench_search.py`): latencia por percentil (`p50`/`p95`/`p99`, en μs) y `throughput`, con 80% hit rate sobre estructuras pre-pobladas con 500K elementos (100K para Linked List).
- **Consultas por rango** (`bench_range.py`): latencia promedio (`avg_latency_us`) y `query_rate` sobre un intervalo `[low, high]`. Las estructuras O(log n + k) (B-Tree, RB-Tree, Skip List) se miden sobre 500K elementos; las O(n) (Hash Table, Linked List) sobre 50K, con menos consultas, por el costo prohibitivo de la operación a mayor escala.
- **Memoria** (`bench_memory.py`): elementos almacenados (`elements`) y `bytes_per_element` hasta alcanzar un límite de 256 MB.

## Resultados principales

- **Hash Table**: la más rápida en búsquedas (~1,21M búsquedas/s, p50 = 0,80 μs), pero la peor en consultas por rango (O(n)) y en eficiencia de memoria (344 bytes/elemento).
- **B-Tree**: el más eficiente en memoria (5,41M elementos en 256 MB) y el más rápido en consultas por rango (15,32 μs, 2,7x más rápido que Skip List) gracias a la localidad de caché de sus nodos con claves contiguas.
- **Red-Black Tree**: mejor balance general entre las estructuras ordenadas, y la mayor estabilidad entre inserción secuencial y aleatoria (1,06x).
- **Linked List**: confirma la inviabilidad de O(n) para búsquedas (1.855x más lenta que Hash Table).

No existe una estructura universal óptima: la elección depende de los patrones de acceso y las restricciones del sistema.
