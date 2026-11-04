"""
Busca A* - Volta para a Terra 

Uma agencia de viagens espacial vende trechos entre astros. Cada trecho
guarda DOIS custos: preco (mil creditos) e tempo (dias). O usuario escolhe
qual deles quer minimizar. O objetivo é sempre voltar para a Terra.
"""

from heapq import heappush, heappop

# ---------------------------------------------------------------------------
# GRAFO: (astro_a, astro_b, preco, tempo)   - rotas de mao dupla
# ---------------------------------------------------------------------------
arestas = [
    ("Terra", "Lua", 41, 3),
    ("Terra", "Venus", 123, 24),
    ("Terra", "Marte", 197, 42),
    ("Venus", "Mercurio", 141, 28),
    ("Venus", "Sol", 256, 57),
    ("Mercurio", "Sol", 156, 32),
    ("Venus", "Marte", 423, 33),            
    ("Terra", "Ceres", 886, 69),            
    ("Marte", "Ceres", 412, 96),
    ("Ceres", "Jupiter", 769, 185),
    ("Terra", "Jupiter", 2052, 160),       
    ("Jupiter", "Europa", 41, 3),
    ("Jupiter", "Saturno", 1351, 331),
    ("Saturno", "Titan", 41, 3),
    ("Marte", "Saturno", 3900, 305),      
    ("Saturno", "Urano", 2914, 722),
    ("Urano", "Netuno", 3288, 815),
    ("Saturno", "Netuno", 9835, 768),     
    ("Netuno", "Plutao", 2862, 709),
]

# ---------------------------------------------------------------------------
# HEURISTICAS (objetivo: Terra)
# ---------------------------------------------------------------------------
# Distancia ate a Terra, em milhoes de km.
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


FATOR_PRECO = 2.0     # mil creditos por milhao de km
FATOR_TEMPO = 0.25    # dias por milhao de km

heuristicas = {
    "preco": {astro: d * FATOR_PRECO for astro, d in distancia_terra.items()},
    "tempo": {astro: d * FATOR_TEMPO for astro, d in distancia_terra.items()},
}

OBJETIVO = "Terra"
CRITERIOS = ("preco", "tempo")


def montar_grafo(lista_arestas):
    """Dicionario de adjacencia {astro: [(vizinho, preco, tempo), ...]}."""
    g = {}
    for a, b, preco, tempo in lista_arestas:
        g.setdefault(a, []).append((b, preco, tempo))
        g.setdefault(b, []).append((a, preco, tempo))
    return g


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


def busca_a_estrela(grafo, inicio, criterio, dados=False):
    """Menor caminho de 'inicio' ate a Terra minimizando 'preco' ou 'tempo'."""
    if criterio not in CRITERIOS:
        raise ValueError("Criterio invalido. Use 'preco' ou 'tempo'.")
    if inicio not in grafo:
        raise ValueError(f"Astro '{inicio}' nao existe no grafo.")

    h = heuristicas[criterio]

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

        for vizinho, preco, tempo in grafo[no.estado]:
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


def comparar_criterios(grafo, inicio):
    """Mostra a melhor rota por preco e a melhor por tempo."""
    for criterio in CRITERIOS:
        imprimir_resultado(busca_a_estrela(grafo, inicio, criterio))