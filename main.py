"""
Ponto de entrada do Sistema de Gerenciamento e Planejamento de Missoes
Espaciais. Menu de linha de comando simples. toda a logica de verdade
fica em src/sistema.py (SistemaMissoes).
"""

from src.sistema import SistemaMissoes
from src.missao.planejador_luas import imprimir_resultado as imprimir_resultado_luas
from src.missao.planejador_rota_a_estrela import imprimir_resultado as imprimir_resultado_volta
from src.missao.fluxo_maximo import imprimir_resultado as imprimir_resultado_fluxo
from src.missao.planejador_rota_gulosa import imprimir_resultado as imprimir_resultado_guloso

CAMINHO_PADRAO_DADOS = "dados/exemplo_bodies.json"
LIMITE_LUAS = 10_000   # a DP usa memoria proporcional a n * x


def exibir_menu() -> None:
    print("\n" + "=" * 60)
    print("  SISTEMA DE PLANEJAMENTO DE MISSOES ESPACIAIS")
    print("=" * 60)
    print(" 1  - Carregar dados de arquivo local (.json)")
    print(" 2  - Carregar dados da API (requer SOLAR_API_KEY)")
    print(" 3  - Buscar corpo por ID")
    print(" 4  - Pesquisar por nome (trecho)")
    print(" 5  - Pesquisar por tipo (Planet, Moon, Dwarf Planet, ...)")
    print(" 6  - Listar todos os corpos carregados")
    print(" 7  - Filtrar por faixa de distancia (km)")
    print(" 8  - Listar ordenado por distancia")
    print(" 9  - Ver estatisticas da Tabela Hash (colisoes / fator de carga)")
    print(" 10 - Ver estatisticas da Trie (Nos visitados / Total de Nos)")
    print(" 11 - Ver estatisticas da Arvore B (Altura / Divisoes)")
    print(" 12 - Planejar missao (algoritmo guloso)")
    print(" 13 - Planejar luas (programacao dinamica)")
    print(" 14 - Voltar para a Terra (A*: escolher preco ou tempo)")
    print(" 15 - Fluxo maximo de carga (Edmonds-Karp + corte minimo)")
    print(" 0  - Sair")
    print("=" * 60)


def ler_lista(texto: str) -> list:
    """'Terra, Lua' -> ['Terra', 'Lua']"""
    return [parte.strip() for parte in texto.split(",") if parte.strip()]


def ler_origens_destinos():
    origens = ler_lista(input("Origem(ns), separadas por virgula (ex: Terra,Lua): "))
    destinos = ler_lista(input("Destino(s), separados por virgula (ex: Marte,Titan): "))
    return origens, destinos


def imprimir_lista(corpos) -> None:
    if not corpos:
        print("Nenhum resultado encontrado.")
        return
    for corpo in corpos:
        print(f"  {corpo}")
    print(f"Total: {len(corpos)}")


def main() -> None:
    sistema = SistemaMissoes()

    while True:
        exibir_menu()
        opcao = input("Escolha uma opcao: ").strip()

        if opcao == "1":
            caminho = input(f"Caminho do arquivo [{CAMINHO_PADRAO_DADOS}]: ").strip()
            caminho = caminho or CAMINHO_PADRAO_DADOS
            try:
                qtd = sistema.carregar_de_arquivo(caminho)
                print(f"OK: {qtd} corpos carregados de '{caminho}'.")
            except FileNotFoundError:
                print(f"Erro: arquivo '{caminho}' nao encontrado.")

        elif opcao == "2":
            try:
                qtd = sistema.carregar_da_api()
                print(f"OK: {qtd} corpos carregados da API.")
            except RuntimeError as e:
                print(f"Erro: {e}")
            except Exception as e:
                print(f"Erro ao consultar a API: {e}")

        elif opcao == "3":
            id_corpo = input("ID do corpo (ex: terre, mars): ").strip()
            corpo = sistema.buscar_por_id(id_corpo)
            print(corpo if corpo else "Corpo nao encontrado.")

        elif opcao == "4":
            trecho = input("Trecho do nome: ").strip()
            imprimir_lista(sistema.pesquisar_por_nome_parcial(trecho))

        elif opcao == "5":
            tipo = input("Tipo: ").strip()
            imprimir_lista(sistema.pesquisar_por_tipo(tipo))

        elif opcao == "6":
            imprimir_lista(sistema.listar_todos())

        elif opcao == "7":
            try:
                minimo = float(input("Distancia minima (km): ").strip())
                maximo = float(input("Distancia maxima (km): ").strip())
                imprimir_lista(sistema.filtrar_por_faixa_distancia(minimo, maximo))
            except ValueError:
                print("Erro: informe numeros validos.")

        elif opcao == "8":
            imprimir_lista(sistema.listar_ordenado_por_distancia())

        elif opcao == "9":
            print(f"Quantidade de corpos carregados: {sistema.quantidade_corpos()}")
            sistema.imprimir_estatisticas_hash()

        elif opcao == "10":
            print(f"Quantidade de corpos carregados: {sistema.quantidade_corpos()}")
            sistema.imprimir_estatisticas_trie()

        elif opcao == "11":
            print(f"Quantidade de corpos carregados: {sistema.quantidade_corpos()}")
            sistema.imprimir_estatisticas_arvore_b()

        elif opcao == "12":
            try:
                combustivel = float(input("Combustivel total da nave (em milhoes de km): ").strip())
                custo_parada = float(input("Custo fixo de combustivel por parada (em milhoes de km): ").strip())
                if combustivel <= 0 or custo_parada < 0:
                    print("Erro: combustivel deve ser > 0 e custo de parada >= 0.")
                    continue
                resultado = sistema.planejar_rota(combustivel, custo_parada)
                imprimir_resultado_guloso(resultado)
            except ValueError:
                print("Erro: informe um numero valido.")

        elif opcao == "13":
            if sistema.quantidade_corpos() == 0:
                print("Erro: carregue os dados primeiro (opcao 1 ou 2).")
                continue
            try:
                x = int(input("Quantidade exata de luas a visitar: ").strip())
                if x > LIMITE_LUAS:
                    print(f"Erro: o limite e {LIMITE_LUAS} luas.")
                    continue
                imprimir_resultado_luas(sistema.planejar_luas(x))
            except ValueError as e:
                print(f"Erro: {e}")

        elif opcao == "14":
            try:
                origem = input("Astro de origem (ex: Plutao, Titan, Marte): ").strip().capitalize()
                criterio = input("Minimizar [preco/tempo]: ").strip().lower()
                imprimir_resultado_volta(sistema.planejar_volta(origem, criterio))
            except ValueError as e:
                print(f"Erro: {e}")

        elif opcao == "15":
            try:
                origem = input("Astro de origem (ex: Terra): ").strip().capitalize()
                destino = input("Astro de destino (ex: Saturno): ").strip().capitalize()
                imprimir_resultado_fluxo(sistema.calcular_fluxo(origem, destino))
            except ValueError as e:
                print(f"Erro: {e}")


        elif opcao == "0":
            print("Encerrando o sistema.")
            break

        else:
            print("Opcao invalida.")


if __name__ == "__main__":
    main()