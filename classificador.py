"""Triagem de chamados de TI por mínimos quadrados. Execute com --help."""

import argparse
import csv
import sys
from pathlib import Path

from grafico import gerar_grafico
from modelo import (classe_prevista, equacoes_normais, escore, ler_ponto,
                    ler_treino, nome_classe, resolver_sistema)


def decimal(valor, com_sinal=False):
    """Formata para exibição. O cálculo das classes usa as frações originais."""
    formato = "+.6f" if com_sinal else ".6f"
    return format(float(valor), formato).replace(".", ",")


def exibir_previsao(numero, ponto, pesos):
    """Mostra os dados do chamado, o escore e o rótulo escolhido."""
    u, t = ponto
    valor = escore(pesos, u, t)
    classe = classe_prevista(valor)
    print(f"T{numero} | u={u}, t={t} min | escore={decimal(valor, True)} "
          f"| {nome_classe(classe)} ({classe:+d})")


def consultas_interativas(pontos, pesos):
    """Lê e classifica novos chamados até o usuário encerrar a sessão."""
    print("Digite usuários e minutos separados por espaço. Enter encerra.")
    while True:
        try:
            entrada = input("Novo chamado> ").strip()
        except EOFError:
            break
        if not entrada or entrada.lower() == "sair":
            break
        try:
            campos = entrada.split()
            if len(campos) != 2:
                raise ValueError("Exemplo de entrada: 8 15.")
            ponto = ler_ponto(*campos)
        except ValueError as erro:
            print(f"Entrada inválida: {erro}", file=sys.stderr)
            continue
        pontos.append(ponto)
        exibir_previsao(len(pontos), ponto, pesos)


def executar():
    """Organiza entrada, ajuste, diagnóstico de treino, consultas e gráfico."""
    parser = argparse.ArgumentParser(description=__doc__.split(".")[0])
    parser.add_argument("--treino", type=Path, default=Path(__file__).with_name("treino.csv"),
                        help="CSV com cabeçalho usuarios,minutos,classe.")
    parser.add_argument("--ponto", nargs=2, action="append", default=[],
                        metavar=("USUARIOS", "MINUTOS"), help="Pode ser repetido.")
    parser.add_argument("--interativo", action="store_true", help="Recebe pontos pelo teclado.")
    parser.add_argument("--grafico", type=Path, default=Path("decisao.svg"),
                        help="Arquivo SVG de saída (padrão: decisao.svg).")
    args = parser.parse_args()

    try:
        # Valide as entradas antes de abrir o arquivo de saída.
        if args.grafico.suffix.lower() != ".svg" or args.grafico.resolve() == args.treino.resolve():
            raise ValueError("Escolha um arquivo de saída .svg diferente da base.")
        amostras = ler_treino(args.treino)
        pontos = [ler_ponto(u, t) for u, t in args.ponto]
        gram, alvo = equacoes_normais(amostras)
        pesos, posto = resolver_sistema(gram, alvo)

        # O erro quadrático mede a distância aos rótulos. O acerto depende do sinal.
        acertos, soma_erros = 0, 0
        for u, t, classe in amostras:
            valor = escore(pesos, u, t)
            soma_erros += (valor - classe) ** 2
            acertos += classe_prevista(valor) == classe
        b, w_u, w_t = pesos
        print(f"s(u,t) = {decimal(b)} {decimal(w_u, True)} u {decimal(w_t, True)} t")
        print(f"Treino: {acertos}/{len(amostras)} acertos | soma dos erros quadráticos = {decimal(soma_erros)}")
        if posto < 3:
            print("Ajuste não único: os coeficientes livres foram fixados em zero.")
        if w_u == 0 and w_t == 0:
            print("Escore constante: todos os pontos recebem a mesma classe. Não há reta separadora.")
        else:
            print("Fronteira: s(u,t) = 0. A igualdade recebe a classe prioritária.")

        # A ordem dos testes é a mesma no terminal e nos rótulos T1, T2... da figura.
        for numero, ponto in enumerate(pontos, 1):
            exibir_previsao(numero, ponto, pesos)
        if args.interativo:
            consultas_interativas(pontos, pesos)
        gerar_grafico(args.grafico, amostras, pesos, pontos)
        print(f"Gráfico: {args.grafico}")
    except (OSError, ValueError, csv.Error, OverflowError) as erro:
        parser.exit(2, f"Erro: {erro}\n")


# Também é possível importar as funções em testes sem executar o programa.
if __name__ == "__main__":
    executar()
