"""
Fachada do sistema: junta aquisicao de dados + estrutura de busca + as
operacoes de consulta/filtragem exigidas pelo enunciado (Secao 6).

O main.py (interface de linha de comando) so deve falar com esta classe,
nunca diretamente com TabelaHash ou com o cliente da API.
"""

from typing import List, Optional

from src.missao.planejador_rota_gulosa import (
    planejar_rota as _executar_planejamento_rota,
    ResultadoRota,
)

from src.missao.planejador_rota_a_estrela import (arestas, montar_grafo, busca_a_estrela)

from src.api.solar_system_client import (
    buscar_corpos_da_api,
    carregar_corpos_de_arquivo,
)

from src.missao.planejador_luas import (
    selecionar_planetas, minimo_planetas_para_luas,
    comparar_cenarios, ResultadoLuas)



from src.estruturas.tabela_hash import TabelaHash
from src.estruturas.trie import Trie
from src.estruturas.arvore_b import ArvoreB

from src.modelos.corpo_celeste import CorpoCeleste

class SistemaMissoes:

    def __init__(self, capacidade_inicial_hash: int = 16):
        self._tabela = TabelaHash(capacidade_inicial=capacidade_inicial_hash)
        self._trie = Trie()
        self._arvore_b = ArvoreB()

    def _indexar(self, corpo: CorpoCeleste) -> None:
        self._tabela.inserir(corpo.id, corpo)
        self._trie.inserir(corpo.nome, corpo)
        self._arvore_b.inserir(corpo.distancia_km, corpo)

    # ------------------------------------------------------------------
    # Aquisicao de dados
    # ------------------------------------------------------------------
    def carregar_de_arquivo(self, caminho_json: str) -> int:
        corpos = carregar_corpos_de_arquivo(caminho_json)
        for corpo in corpos:
            self._indexar(corpo)
        return len(corpos)

    def carregar_da_api(self) -> int:
        corpos = buscar_corpos_da_api()
        for corpo in corpos:
            self._indexar(corpo)
        return len(corpos)

    # ------------------------------------------------------------------
    # Consulta de elementos (busca exata por id, via Tabela Hash)
    # ------------------------------------------------------------------
    def buscar_por_id(self, id_corpo: str) -> Optional[CorpoCeleste]:
        return self._tabela.buscar(id_corpo)

    # ------------------------------------------------------------------
    # Pesquisa por atributos
    # (Busca linear - a Tabela Hash so acelera
    # busca exata por chave, buscas por atributo vou deixar melhor pela Trie/
    # Arvore B na Parte 2)
    # ------------------------------------------------------------------
    def pesquisar_por_nome_parcial(self, trecho: str) -> List[CorpoCeleste]:
        return self._trie.buscar_por_prefixo(trecho)

    def pesquisar_por_tipo(self, tipo: str) -> List[CorpoCeleste]:
        tipo_lower = tipo.lower()
        return [c for c in self._tabela.todos_valores() if c.tipo.lower() == tipo_lower]

    # ------------------------------------------------------------------
    # Listagem e filtragem
    # ------------------------------------------------------------------
    def listar_todos(self) -> List[CorpoCeleste]:
        return self._tabela.todos_valores()

    def filtrar_por_faixa_distancia(self, minimo_km: float, maximo_km: float) -> List[CorpoCeleste]:
        return self._arvore_b.buscar_por_faixa(minimo_km, maximo_km)

    def listar_ordenado_por_distancia(self) -> List[CorpoCeleste]:
        return self._arvore_b.todos_valores()

    # ------------------------------------------------------------------
    # Instrumentacao
    # ------------------------------------------------------------------
    def quantidade_corpos(self) -> int:
        return len(self._tabela)

    def imprimir_estatisticas_hash(self) -> None:
        self._tabela.imprimir_estatisticas()

    def imprimir_estatisticas_trie(self) -> None:
        self._trie.imprimir_estatisticas()

    def imprimir_estatisticas_arvore_b(self) -> None:
        self._arvore_b.imprimir_estatisticas()

    # ------------------------------------------------------------------
    # Planejamento guloso de rota
    # ------------------------------------------------------------------
    def planejar_rota(self, combustivel_milhoes_km: float, custo_parada_milhoes_km: float = 0.0) -> ResultadoRota:
        return _executar_planejamento_rota(self._tabela.todos_valores(), combustivel_milhoes_km, custo_parada_milhoes_km)

    # ------------------------------------------------------------------
    # Planejamento por programacao dinamica (troco 0/1 com planetas)
    # ------------------------------------------------------------------
    def planejar_luas(self, x: int) -> ResultadoLuas:
        planetas = selecionar_planetas(self._tabela.todos_valores())
        return minimo_planetas_para_luas(planetas, x)

    def comparar_cenarios_luas(self, alvos: List[int]) -> None:
        comparar_cenarios(selecionar_planetas(self._tabela.todos_valores()), alvos)

    # ------------------------------------------------------------------
    # Busca (A*)
    # ------------------------------------------------------------------

    def planejar_volta(self, origem: str, criterio: str):
        return busca_a_estrela(montar_grafo(arestas), origem, criterio)


