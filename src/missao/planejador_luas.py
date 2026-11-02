"""
Otimizacao de missao por PROGRAMACAO DINAMICA (variante do problema do troco).

Problema: visitar EXATAMENTE x luas passando pelo MENOR numero de planetas.
Cada planeta so pode ser visitado uma vez (troco 0/1), e vale tantas "moedas"
quanto o seu numero de luas (CorpoCeleste.quantidade_luas).

Criterio principal:  menor numero de planetas visitados.
Desempate:           entre solucoes com o mesmo numero de planetas, a que tem
                     menor soma das distancias ao Sol (menos combustivel).

"""

from dataclasses import dataclass, field
from typing import List, Tuple

from src.modelos.corpo_celeste import CorpoCeleste

INF = float("inf")
CUSTO_INVIAVEL: Tuple[float, float] = (INF, INF)


@dataclass
class ResultadoLuas:
    luas_alvo: int
    planetas: List[CorpoCeleste] = field(default_factory=list)
    viavel: bool = False

    @property
    def total_planetas(self) -> int:
        return len(self.planetas)

    @property
    def total_luas(self) -> int:
        return sum(p.quantidade_luas for p in self.planetas)

    @property
    def distancia_total_km(self) -> float:
        return sum(p.distancia_km for p in self.planetas)


def selecionar_planetas(corpos: List[CorpoCeleste]) -> List[CorpoCeleste]:
    """Candidatos: planetas (isPlanet) que possuem ao menos uma lua."""
    return [c for c in corpos if c.e_planeta and c.quantidade_luas > 0]


def _somar(custo: Tuple[float, float], distancia_km: float) -> Tuple[float, float]:
    return (custo[0] + 1, custo[1] + distancia_km)


def minimo_planetas_para_luas(planetas: List[CorpoCeleste], x: int) -> ResultadoLuas:
    """Escolhe, entre 'planetas', o subconjunto com exatamente x luas, com
    minimo de planetas e, em caso de empate, menor soma de distancias ao Sol."""
    if x < 0:
        raise ValueError("A quantidade de luas deve ser >= 0.")

    itens = [p for p in planetas if p.quantidade_luas > 0]
    n = len(itens)

    dp = [[CUSTO_INVIAVEL] * (x + 1) for _ in range(n + 1)]
    dp[0][0] = (0, 0.0)

    for i in range(1, n + 1):
        planeta = itens[i - 1]
        m = planeta.quantidade_luas
        for s in range(x + 1):
            melhor = dp[i - 1][s]                       # nao visita o planeta i
            if s >= m and dp[i - 1][s - m] != CUSTO_INVIAVEL:
                candidato = _somar(dp[i - 1][s - m], planeta.distancia_km)
                if candidato < melhor:                  # comparacao lexicografica
                    melhor = candidato
            dp[i][s] = melhor

    res = ResultadoLuas(luas_alvo=x)
    if dp[n][x] == CUSTO_INVIAVEL:
        return res                                      # sem solucao

    res.viavel = True
    s = x
    for i in range(n, 0, -1):                           # reconstrucao
        if dp[i][s] != dp[i - 1][s]:                    # o planeta i foi usado
            res.planetas.append(itens[i - 1])
            s -= itens[i - 1].quantidade_luas
    res.planetas.reverse()
    return res


def imprimir_resultado(r: ResultadoLuas) -> None:
    print(f"\n=== Missao das Luas: alvo = {r.luas_alvo} luas ===")
    if not r.viavel:
        print("Nao existe combinacao de planetas que some exatamente esse numero de luas.")
        return
    print(f"Planetas visitados: {r.total_planetas}  |  Luas somadas: {r.total_luas}"
          f"  |  Soma das distancias ao Sol: {r.distancia_total_km:,.0f} km")
    for p in r.planetas:
        print(f"  {p.nome:10s} {p.quantidade_luas:4d} luas   (dist. Sol = {p.distancia_km:,.0f} km)")


def comparar_cenarios(planetas: List[CorpoCeleste], alvos: List[int]) -> None:
    """Roda a DP para varios valores de x e imprime uma tabela comparativa."""
    print("\n=== Comparacao de cenarios ===")
    print(f"{'Alvo':>6} {'Viavel':>7} {'Planetas':>9} {'Dist. total (km)':>20}")
    for x in alvos:
        r = minimo_planetas_para_luas(planetas, x)
        if r.viavel:
            print(f"{x:>6} {'sim':>7} {r.total_planetas:>9} {r.distancia_total_km:>20,.0f}")
        else:
            print(f"{x:>6} {'nao':>7} {'-':>9} {'-':>20}")