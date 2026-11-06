"""
Busca A* - Volta para a Terra (Sistema Solar)

Uma agencia de viagens espacial vende trechos entre astros. Cada trecho
guarda DOIS custos: preco (mil creditos) e tempo (dias). O usuario escolhe
qual deles quer minimizar. O objetivo e sempre voltar para a Terra.

O grafo NAO e criado aqui: vem de src/missao/grafo_sistema_solar.py, o mesmo
usado pelo modulo de fluxo maximo.
"""

from heapq import heappush, heappop

from src.missao.grafo_sistema_solar import arestas, montar_grafo

# ---------------------------------------------------------------------------
# HEURISTICAS (objetivo: Terra)
# ---------------------------------------------------------------------------
# Distancia ate a Terra, em milhoes de km (diferenca das distancias ao Sol).
distancia_terra = {
    "Terra": 0,
    "Lua": 0.4,
    "Venus": 41.4,
    "Marte": 78.3,
    "Mercurio": 91.7,
    "Sol": 149.6,
    "Ceres": 264.4,
    "Jupiter": 628.9,
    "Europa": 628.9,
    "Saturno": 1284.4,
    "Titan": 1284.4,
    "Urano": 2721.4,
    "Netuno": 4345.4,
    "Plutao": 5756.4,
}

# Fator = menor custo por milhao de km entre todas as arestas. Com ele a
# heuristica nunca superestima o custo real (admissivel e consistente).
FATOR_PRECO = 2.0     # mil creditos por milhao de km
FATOR_TEMPO = 0.25    # dias por milhao de km

heuristicas = {
    "preco": {astro: d * FATOR_PRECO for astro, d in distancia_terra.items()},
    "tempo": {astro: d * FATOR_TEMPO for astro, d in distancia_terra.items()},
}

OBJETIVO = "Terra"
CRITERIOS = ("preco", "tempo")


class No:
    def __init__(self, estado, pai=None, preco=0, tempo=0):
        self.estado = estado
        self.pai = pai
        self.preco = preco      # preco acumulado ate aqui
        self.tempo = tempo      # tempo acumulado ate aqui

    def custo(self, criterio):
        return self.preco if criterio == "preco" else self.tempo

    def caminho(self):
        no, sequencia = self, []
        while no:
            sequencia.append(no.estado)
            no = no.pai
        return list(reversed(sequencia))


def busca_a_estrela(grafo, inicio, criterio, dados=False, usar_heuristica=True):
    """Menor caminho de 'inicio' ate a Terra minimizando 'preco' ou 'tempo'."""
    if criterio not in CRITERIOS:
        raise ValueError("Criterio invalido. Use 'preco' ou 'tempo'.")
    if inicio not in grafo:
        raise ValueError(f"Astro '{inicio}' nao existe no grafo.")

    h = heuristicas[criterio] if usar_heuristica else {}   # astro sem heuristica => h = 0

    no = No(inicio)
    fronteira = []
    contador = 0
    heappush(fronteira, (h.get(inicio, 0), contador, no))

    g_na_fronteira = {inicio: 0}
    explorados = set()
    expandidos = 0
    fronteira_max = 1

    while fronteira:
        fronteira_max = max(fronteira_max, len(g_na_fronteira))
        _, _, no = heappop(fronteira)

        if no.estado in explorados:
            continue
        g_na_fronteira.pop(no.estado, None)
        explorados.add(no.estado)
        expandidos += 1

        if dados:
            g = no.custo(criterio)
            print(f"  [A*] expandindo '{no.estado}' | g={g:,.0f} | h={h.get(no.estado, 0):,.1f} "
                  f"| f={g + h.get(no.estado, 0):,.1f} | fronteira={len(g_na_fronteira)}")

        if no.estado == OBJETIVO:
            return {"criterio": criterio, "caminho": no.caminho(),
                    "custo": no.custo(criterio),
                    "preco_total": no.preco, "tempo_total": no.tempo,
                    "expandidos": expandidos, "fronteira_max": fronteira_max}

        for vizinho, preco, tempo, _capacidade in grafo[no.estado]:
            if vizinho in explorados:
                continue
            novo = No(vizinho, no, no.preco + preco, no.tempo + tempo)
            novo_g = novo.custo(criterio)

            if vizinho in g_na_fronteira and g_na_fronteira[vizinho] <= novo_g:
                continue

            contador += 1
            heappush(fronteira, (novo_g + h.get(vizinho, 0), contador, novo))
            g_na_fronteira[vizinho] = novo_g

    return {"criterio": criterio, "caminho": None, "custo": None,
            "preco_total": None, "tempo_total": None,
            "expandidos": expandidos, "fronteira_max": fronteira_max}


def imprimir_resultado(r):
    print(f"\n=== Volta para a Terra (A*) | minimizando {r['criterio'].upper()} ===")
    if r["caminho"] is None:
        print("Nao existe rota ate a Terra.")
        return
    print("Rota: " + " -> ".join(r["caminho"]))
    print(f"Preco total: {r['preco_total']:,.0f} mil creditos")
    print(f"Tempo total: {r['tempo_total']:,.0f} dias")
    print(f"Nos expandidos: {r['expandidos']} | Fronteira maxima: {r['fronteira_max']}")

