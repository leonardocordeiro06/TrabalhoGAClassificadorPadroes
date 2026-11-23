"""Gráfico SVG das regiões de decisão, feito somente com a biblioteca padrão."""

from fractions import Fraction
from math import ceil, floor, log10
from xml.etree import ElementTree as ET

from modelo import escore


def marcas_eixo(maximo, discreto=False):
    """Escolhe marcas legíveis e deixa uma margem depois do maior valor."""
    maximo = max(Fraction(maximo), 1)
    alvo = maximo / 7
    base = Fraction(10) ** floor(log10(alvo))
    passo = min((base * k for k in (1, 2, 5, 10)), key=lambda p: abs(p - alvo))
    if discreto:
        passo = max(passo, 1)  # O eixo de usuários só recebe marcas inteiras.
    quantidade = ceil(maximo * Fraction(106, 100) / passo)
    return [i * passo for i in range(quantidade + 1)]


def recortar_regiao(pesos, cantos):
    """Recorta o retângulo no semiplano positivo e localiza a fronteira."""
    poligono, fronteira = [], []
    for a, b in zip(cantos, cantos[1:] + cantos[:1]):
        sa, sb = escore(pesos, *a), escore(pesos, *b)
        if sa >= 0:
            poligono.append(a)
        if sa == 0:
            fronteira.append(a)
        if sa * sb < 0:
            # O escore varia linearmente na aresta, inclusive se a reta for vertical.
            parte = Fraction(sa) / (sa - sb)
            corte = (a[0] + parte * (b[0] - a[0]), a[1] + parte * (b[1] - a[1]))
            poligono.append(corte)
            fronteira.append(corte)
    return poligono, fronteira


def gerar_grafico(caminho, amostras, pesos, testes):
    """Desenha os fundos, a reta, os pontos, os eixos e a legenda em SVG."""
    pontos = [(u, t) for u, t, _ in amostras] + list(testes)
    marcas_u = marcas_eixo(max(u for u, _ in pontos), discreto=True)
    marcas_t = marcas_eixo(max(t for _, t in pontos))
    u_max, t_max = marcas_u[-1], marcas_t[-1]
    x0, x1, y0, y1 = 83, 734, 18, 347
    tinta, grade = "#203941", "#b9c8c8"
    rotina, prioridade = "#126570", "#99431d"
    raiz = ET.Element("svg", xmlns="http://www.w3.org/2000/svg", width="760",
                      height="454", viewBox="0 0 760 454", role="img",
                      attrib={"aria-labelledby": "titulo descricao", "font-family": "DejaVu Sans, sans-serif"})
    ET.SubElement(raiz, "title", id="titulo").text = "Triagem de chamados de suporte"
    ET.SubElement(raiz, "desc", id="descricao").text = (
        "O fundo indica a classe prevista. Círculos são chamados de rotina e "
        "triângulos são prioritários no treino. Cruzes representam novos chamados."
    )

    # Estas funções cuidam apenas de coordenadas e primitivas de desenho.
    def pixel(ponto):
        u, t = ponto
        return x0 + float(Fraction(u) / u_max) * (x1 - x0), y1 - float(Fraction(t) / t_max) * (y1 - y0)

    def forma(tag, **atributos):
        valores = {k.replace("_", "-"): str(v) for k, v in atributos.items()}
        return ET.SubElement(raiz, tag, valores)

    def texto(x, y, conteudo, ancora="middle", tamanho=15, **extras):
        forma("text", x=x, y=y, text_anchor=ancora, font_size=tamanho,
              fill=tinta, **extras).text = str(conteudo)

    def segmento(a, b, cor, espessura=1):
        forma("line", x1=a[0], y1=a[1], x2=b[0], y2=b[1],
              stroke=cor, stroke_width=espessura)

    def marcador(x, y, classe):
        if classe == -1:
            forma("circle", cx=x, cy=y, r=5.8, fill=rotina, stroke="white", stroke_width=1.5)
        else:
            forma("polygon", points=f"{x},{y-7} {x-7},{y+5.5} {x+7},{y+5.5}",
                  fill=prioridade, stroke="white", stroke_width=1.5)

    def cruz(x, y):
        segmento((x-5, y-5), (x+5, y+5), tinta, 2.8)
        segmento((x-5, y+5), (x+5, y-5), tinta, 2.8)

    # Um fundo retangular e um único polígono representam os dois semiplanos.
    forma("rect", x=0, y=0, width=760, height=454, fill="white")
    forma("rect", x=x0, y=y0, width=x1-x0, height=y1-y0, fill="#e4f2f2")
    cantos = [(0, 0), (u_max, 0), (u_max, t_max), (0, t_max)]
    regiao, cortes = recortar_regiao(pesos, cantos)
    if len(regiao) >= 3:
        vertices = " ".join(f"{x:.3f},{y:.3f}" for x, y in map(pixel, regiao))
        forma("polygon", points=vertices, fill="#faeadd")

    # Tanto a grade quanto os rótulos são derivados dos limites da amostra e dos testes.
    for u in marcas_u:
        x, _ = pixel((u, 0))
        segmento((x, y0), (x, y1), grade, 0.8)
        texto(x, y1+22, f"{float(u):g}".replace(".", ","))
    for t in marcas_t:
        _, y = pixel((0, t))
        segmento((x0, y), (x1, y), grade, 0.8)
        texto(x0-12, y+5, f"{float(t):g}".replace(".", ","), "end")
    forma("rect", x=x0, y=y0, width=x1-x0, height=y1-y0, fill="none", stroke=tinta)
    texto((x0+x1)/2, 396, "Usuários afetados (pessoas)", tamanho=17)
    texto(23, (y0+y1)/2, "Indisponibilidade (minutos)", tamanho=17,
          transform=f"rotate(-90 23 {(y0+y1)/2})")

    # Só existe um segmento de fronteira visível quando ele corta o quadro em dois pontos.
    tem_segmento = len(cortes) == 2 and (pesos[1] != 0 or pesos[2] != 0)
    if tem_segmento:
        segmento(pixel(cortes[0]), pixel(cortes[1]), tinta, 2.8)
    for u, t, classe in amostras:
        marcador(*pixel((u, t)), classe)
    for numero, ponto in enumerate(testes, 1):
        x, y = pixel(ponto)
        cruz(x, y)
        esquerda = x > x1 - 45
        # Coloca o rótulo no lado do ponto que se afasta da reta.
        acima = escore(pesos, *ponto) * pesos[2] >= 0
        altura = max(y0 + 15, min(y1 - 2, y - 8 if acima else y + 18))
        texto(x-9 if esquerda else x+9, altura, f"T{numero}",
              "end" if esquerda else "start", 14, font_weight="bold")

    # Cores e formas duplicam a informação para quem imprime em tons de cinza.
    marcador(74, 434, -1)
    texto(89, 439, "Rotina (treino)", "start")
    marcador(254, 434, 1)
    texto(269, 439, "Prioritário (treino)", "start")
    if testes:
        cruz(468, 434)
        texto(482, 439, "Teste", "start")
    if tem_segmento:
        segmento((589, 434), (618, 434), tinta, 2.8)
        texto(628, 439, "Fronteira", "start")
    ET.ElementTree(raiz).write(caminho, encoding="utf-8", xml_declaration=True)
