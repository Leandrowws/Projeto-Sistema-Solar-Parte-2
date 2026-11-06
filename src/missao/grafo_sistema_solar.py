"""
Grafo do Sistema Solar (agencia de viagens espacial).

Os modulos de planejamento (A*, fluxo maximo, ...) nao criam o proprio grafo:
todos importam daqui, entao trabalham sempre sobre a mesma rede.

Cada rota (aresta) guarda TRES atributos:
    preco       - mil creditos
    tempo       - dias
    capacidade  - toneladas de carga por mes (nos dois sentidos)

"""

# (astro_a, astro_b, preco, tempo, capacidade)   - rotas de mao dupla
arestas = [
    ("Terra", "Lua", 41, 3, 200),
    ("Terra", "Venus", 123, 24, 80),
    ("Terra", "Marte", 197, 42, 100),
    ("Venus", "Mercurio", 141, 28, 60),
    ("Venus", "Sol", 256, 57, 30),
    ("Mercurio", "Sol", 156, 32, 40),
    ("Venus", "Marte", 423, 33, 25),            
    ("Terra", "Ceres", 886, 69, 20),         
    ("Marte", "Ceres", 412, 96, 70),
    ("Ceres", "Jupiter", 769, 185, 50),
    ("Terra", "Jupiter", 2052, 160, 30),       
    ("Jupiter", "Europa", 41, 3, 90),
    ("Jupiter", "Saturno", 1351, 331, 60),
    ("Saturno", "Titan", 41, 3, 40),
    ("Marte", "Saturno", 3900, 305, 20),        
    ("Saturno", "Urano", 2914, 722, 35),
    ("Urano", "Netuno", 3288, 815, 30),
    ("Saturno", "Netuno", 9835, 768, 15),     
    ("Netuno", "Plutao", 2862, 709, 25),
]


def montar_grafo(lista_arestas=arestas):
    """Dicionario de adjacencia {astro: [(vizinho, preco, tempo, capacidade), ...]}."""
    g = {}
    for a, b, preco, tempo, capacidade in lista_arestas:
        g.setdefault(a, []).append((b, preco, tempo, capacidade))
        g.setdefault(b, []).append((a, preco, tempo, capacidade))
    return g


def sem_conexao(lista_arestas, a, b):
    """Copia da lista de arestas sem a rota entre 'a' e 'b' (simula uma falha).
    Lanca ValueError se essa rota nao existir."""
    restantes = [e for e in lista_arestas if {e[0], e[1]} != {a, b}]
    if len(restantes) == len(lista_arestas):
        raise ValueError(f"Nao existe rota entre '{a}' e '{b}'.")
    return restantes
