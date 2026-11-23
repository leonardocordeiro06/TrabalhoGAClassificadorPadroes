"""Mínimos quadrados para duas características e um intercepto."""

import csv
from fractions import Fraction


def ler_ponto(usuarios, minutos):
    """Converte o número de usuários e a duração para as unidades da base."""
    try:
        u = int(usuarios)
        t = Fraction(minutos)
    except (ValueError, ZeroDivisionError) as erro:
        raise ValueError("Informe usuários inteiros e minutos numéricos.") from erro
    if u < 0 or t < 0:
        raise ValueError("Usuários e minutos devem ser não negativos.")
    return u, t


def ler_treino(caminho):
    """Lê o CSV em UTF-8 e confere o formato e a presença das duas classes."""
    amostras = []
    with open(caminho, encoding="utf-8-sig", newline="") as arquivo:
        leitor = csv.DictReader(arquivo)
        if leitor.fieldnames != ["usuarios", "minutos", "classe"]:
            raise ValueError("Use o cabeçalho usuarios,minutos,classe.")
        for linha in leitor:
            try:
                if None in linha or None in linha.values():
                    raise ValueError("A linha precisa ter três campos.")
                u, t = ler_ponto(linha["usuarios"], linha["minutos"])
                classe = int(linha["classe"])
                if classe not in (-1, 1):
                    raise ValueError("A classe deve ser -1 ou +1.")
            except ValueError as erro:
                raise ValueError(f"Linha {leitor.line_num}: {erro}") from erro
            amostras.append((u, t, classe))
    if {classe for _, _, classe in amostras} != {-1, 1}:
        raise ValueError("Inclua pelo menos um chamado de cada classe (-1 e +1).")
    return amostras


def equacoes_normais(amostras):
    """Acumula G = XᵀX e h = Xᵀy, linha por linha, sem guardar X inteira."""
    gram = [[0 for _ in range(3)] for _ in range(3)]
    alvo = [0, 0, 0]
    for u, t, classe in amostras:
        linha = (1, u, t)  # O 1 permite ajustar o intercepto.
        for i in range(3):
            alvo[i] += linha[i] * classe
            for j in range(3):
                gram[i][j] += linha[i] * linha[j]
    return gram, alvo


def resolver_sistema(gram, alvo):
    """Resolve o sistema normal consistente por escalonamento e substituição."""
    # Frações mantêm exatos os pivôs, o teste de zero e o desempate na reta.
    matriz = [[Fraction(n) for n in [*linha, termo]]
              for linha, termo in zip(gram, alvo)]
    pivos = []
    for coluna in range(3):
        linha_pivo = len(pivos)
        candidata = max(range(linha_pivo, 3), key=lambda i: abs(matriz[i][coluna]))
        if matriz[candidata][coluna] == 0:
            continue  # Coluna livre: o ajuste admite mais de uma solução.
        matriz[linha_pivo], matriz[candidata] = matriz[candidata], matriz[linha_pivo]
        for i in range(linha_pivo + 1, 3):
            fator = matriz[i][coluna] / matriz[linha_pivo][coluna]
            for j in range(coluna, 4):
                matriz[i][j] -= fator * matriz[linha_pivo][j]
        pivos.append(coluna)

    # Começar em zero fixa as incógnitas livres. Resolvem-se as demais de baixo para cima.
    pesos = [Fraction(0) for _ in range(3)]
    for i in reversed(range(len(pivos))):
        coluna = pivos[i]
        conhecidos = sum(matriz[i][j] * pesos[j] for j in range(coluna + 1, 3))
        pesos[coluna] = (matriz[i][3] - conhecidos) / matriz[i][coluna]
    return tuple(pesos), len(pivos)


def escore(pesos, u, t):
    """Soma o intercepto ao produto interno do vetor de pesos com o ponto."""
    b, w_u, w_t = pesos
    return b + w_u * u + w_t * t


def classe_prevista(valor):
    """A fronteira pertence à classe prioritária por convenção da aplicação."""
    return 1 if valor >= 0 else -1


def nome_classe(classe):
    """Converte o rótulo numérico no nome usado pela central de suporte."""
    return "Prioritário" if classe == 1 else "Rotina"
