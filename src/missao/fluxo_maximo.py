"""
Fluxo maximo (Secao 5.4) - Edmonds-Karp.

Pergunta: qual a maior quantidade de carga (toneladas/mes) que pode ser
enviada de UMA origem ate UM destino, dadas as capacidades das rotas?
O grafo vem de grafo_sistema_solar.py (o mesmo usado pelo A*).

As rotas sao de mao dupla: cada sentido tem a capacidade da rota.
"""

from collections import deque
from dataclasses import dataclass, field
from heapq import heappush, heappop

INF = float("inf")


@dataclass
class ResultadoFluxo:
    origem: str
    destino: str
    valor: float = 0
    caminhos: list = field(default_factory=list)           # [(caminho, quantidade)]
    arestas_com_fluxo: list = field(default_factory=list)  # [(u, v, fluxo, capacidade)]
    corte: list = field(default_factory=list)              # [(u, v, capacidade)]
    maior_caminho: list = None
    capacidade_maior_caminho: float = 0


# ----------------------------------------------------------------------
# Grafo residual e busca de caminho aumentante
# ----------------------------------------------------------------------
def _construir_residual(grafo):
    """residual[u][v] = capacidade que ainda sobra de u para v."""
    residual = {u: {} for u in grafo}
    for u, vizinhos in grafo.items():
        for v, _preco, _tempo, capacidade in vizinhos:
            residual[u][v] = residual[u].get(v, 0) + capacidade
    return residual


def _bfs(residual, s, t):
    """Caminho aumentante mais curto (em numero de arestas), ou None."""
    pai = {s: None}
    fila = deque([s])
    while fila:
        u = fila.popleft()
        for v, cap in residual[u].items():
            if cap > 0 and v not in pai:
                pai[v] = u
                if v == t:
                    caminho = [t]
                    while pai[caminho[-1]] is not None:
                        caminho.append(pai[caminho[-1]])
                    return list(reversed(caminho))
                fila.append(v)
    return None


# ----------------------------------------------------------------------
# Caminho de maior capacidade (para comparar com o fluxo maximo)
# ----------------------------------------------------------------------
def caminho_de_maior_capacidade(grafo, origem, destino):
    """Rota unica cujo gargalo (menor capacidade do caminho) e o maior possivel.
    Dijkstra trocando 'soma' por 'minimo'. Retorna (caminho, gargalo)."""
    melhor = {origem: INF}
    pai = {origem: None}
    visitados = set()
    heap = [(-INF, origem)]
    while heap:
        neg, u = heappop(heap)
        if u in visitados:
            continue
        visitados.add(u)
        if u == destino:
            break
        for v, _p, _t, cap in grafo[u]:
            nova = min(-neg, cap)
            if nova > melhor.get(v, 0):
                melhor[v] = nova
                pai[v] = u
                heappush(heap, (-nova, v))
    if destino not in pai:
        return None, 0
    caminho = [destino]
    while pai[caminho[-1]] is not None:
        caminho.append(pai[caminho[-1]])
    return list(reversed(caminho)), melhor[destino]


# ----------------------------------------------------------------------
# Edmonds-Karp
# ----------------------------------------------------------------------
def fluxo_maximo(grafo, origem, destino, verbose=False):
    if origem not in grafo:
        raise ValueError(f"Astro '{origem}' nao existe no grafo.")
    if destino not in grafo:
        raise ValueError(f"Astro '{destino}' nao existe no grafo.")
    if origem == destino:
        raise ValueError("Origem e destino devem ser astros diferentes.")

    residual = _construir_residual(grafo)
    original = {u: dict(vs) for u, vs in residual.items()}   # copia das capacidades

    res = ResultadoFluxo(origem=origem, destino=destino)

    # repete: acha caminho com espaco livre, envia o gargalo, atualiza o residual
    while True:
        caminho = _bfs(residual, origem, destino)
        if caminho is None:
            break
        gargalo = min(residual[u][v] for u, v in zip(caminho, caminho[1:]))
        for u, v in zip(caminho, caminho[1:]):
            residual[u][v] -= gargalo
            residual[v][u] += gargalo
        res.valor += gargalo
        res.caminhos.append((caminho, gargalo))
        if verbose:
            print(f"  [EK] caminho {' -> '.join(caminho)} | gargalo={gargalo} "
                  f"| fluxo total={res.valor}")

    # fluxo que passou em cada rota (capacidade original - o que sobrou)
    for u in sorted(original):
        for v in sorted(original[u]):
            fluxo = original[u][v] - residual[u][v]
            if fluxo > 0:
                res.arestas_com_fluxo.append((u, v, fluxo, original[u][v]))

    # corte minimo: astros ainda alcancaveis a partir da origem no residual final
    alcancavel = {origem}
    fila = deque([origem])
    while fila:
        u = fila.popleft()
        for v, cap in residual[u].items():
            if cap > 0 and v not in alcancavel:
                alcancavel.add(v)
                fila.append(v)
    # rotas que saem desse conjunto sao as saturadas: formam o gargalo da rede
    for u in sorted(alcancavel):
        for v in sorted(original[u]):
            if v not in alcancavel and original[u][v] > 0:
                res.corte.append((u, v, original[u][v]))

    res.maior_caminho, res.capacidade_maior_caminho = \
        caminho_de_maior_capacidade(grafo, origem, destino)
    return res


# ----------------------------------------------------------------------
# Apresentacao
# ----------------------------------------------------------------------
def imprimir_resultado(r):
    print("\n=== Fluxo maximo de carga (Edmonds-Karp) ===")
    print(f"Origem:  {r.origem}")
    print(f"Destino: {r.destino}")
    print(f"Fluxo maximo: {r.valor:g} toneladas/mes")
    if r.valor == 0:
        print("Nao existe rota com capacidade entre origem e destino.")
        return

    print(f"\n--- Caminhos aumentantes ({len(r.caminhos)}) ---")
    for i, (caminho, qtd) in enumerate(r.caminhos, start=1):
        print(f"  {i}. {' -> '.join(caminho)}  (+{qtd:g})")

    print("\n--- Rotas utilizadas (fluxo/capacidade) ---")
    for u, v, fluxo, cap in r.arestas_com_fluxo:
        marca = "  <- saturada" if fluxo == cap else ""
        print(f"  {u:9s} -> {v:9s} {fluxo:g}/{cap:g}{marca}")

    print(f"\n--- Corte minimo (conexoes criticas) | capacidade = {sum(c for *_, c in r.corte):g} ---")
    for u, v, cap in r.corte:
        print(f"  {u} -> {v}  (cap {cap:g})")

    ganho = r.valor - r.capacidade_maior_caminho
    print("\n--- Rota unica x rede inteira ---")
    print(f"  Melhor rota unica: {' -> '.join(r.maior_caminho)} "
          f"(gargalo {r.capacidade_maior_caminho:g})")
    print(f"  Usando varias rotas ao mesmo tempo: {r.valor:g}  (+{ganho:g})")