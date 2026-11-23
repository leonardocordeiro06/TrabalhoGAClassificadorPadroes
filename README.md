# Triagem de chamados de TI

Atividade prática do Tema 2 de SPOMVAL, **Vetores, Geometria Analítica e Álgebra Linear**, do Bacharelado em Sistemas de Informação do Instituto Federal de São Paulo (IFSP). Discente: Leonardo Cordeiro da Silva, protocolo SP3301699. Docente: Profa. Josceli.

O programa ajusta por mínimos quadrados uma reta que classifica chamados de suporte a partir do número de usuários afetados e dos minutos de indisponibilidade. A base didática contém 12 cenários simulados. Os dois pontos de teste ficam fora do treinamento. [Leia o relatório em PDF](Relatorio_Tema_2.pdf).

## Execução

Com Python 3 instalado, abra o terminal na pasta do projeto. A implementação usa exclusivamente a biblioteca padrão.

```sh
python classificador.py --ponto 8 15 --ponto 8 20
python testes.py
```

Se a instalação do Python estiver disponível como `python3` ou `py`, use esse comando no lugar de `python`. A primeira execução treina o modelo com `treino.csv`, informa os escores e grava `decisao.svg` na pasta atual. O gráfico abre em um navegador. A segunda execução verifica seis condições, incluindo os dois casos do relatório.

| Caso | Usuários | Minutos | Escore esperado | Classe |
| --- | ---: | ---: | ---: | --- |
| T1 | 8 | 15 | −205/1499 ≈ −0,136758 | Rotina (−1) |
| T2 | 8 | 20 | 287/1499 ≈ +0,191461 | Prioritário (+1) |

Para testar outros chamados, informe um par por opção `--ponto` ou digite os pares no modo interativo. O programa responde a cada entrada. Pressione Enter em uma linha vazia para encerrar e salvar o gráfico.

```sh
python classificador.py --interativo --grafico consultas.svg
```

## Usar outra base

Passe o caminho do seu CSV com `--treino`. A primeira linha deve ser `usuarios,minutos,classe`. Use `-1` para rotina e `+1` para prioritário. Informe ao menos um registro de cada classe. Os usuários são contagens inteiras não negativas. Os minutos aceitam valores não negativos inteiros, decimais com ponto ou frações como `205/12`.

```sh
python classificador.py --treino outra_base.csv --ponto 8 15 --grafico outra_base.svg
```

O escore é `b + w_u*u + w_t*t`. Um valor negativo leva à fila de rotina. Zero ou um valor positivo leva à prioritária. O código monta as equações normais e as resolve por escalonamento com frações exatas. Se houver dependência entre as colunas, fixa os coeficientes livres em zero e informa que há outras soluções. Se os dois pesos forem nulos, informa que a classificação é constante.

## Arquivos do projeto

| Arquivo | Conteúdo |
| --- | --- |
| [Relatorio_Tema_2.pdf](Relatorio_Tema_2.pdf) | Relatório com a aplicação, a teoria, o gráfico, os dois testes executados e as referências. |
| [classificador.py](classificador.py) | Interface de linha de comando, modo interativo e diagnóstico do ajuste. |
| [modelo.py](modelo.py) | Leitura dos dados, montagem do sistema, eliminação de Gauss e classificação. |
| [grafico.py](grafico.py) | Geração do SVG com os dois semiplanos, a fronteira e os pontos. |
| [treino.csv](treino.csv) | Os 12 chamados de treinamento da Tabela 1. |
| [testes.py](testes.py) | T1, T2, empate, reta vertical, base colinear e padrão XOR. |
| [figura_1.svg](figura_1.svg) | Gráfico vetorial reproduzido no relatório. |
| [relatorio.html](relatorio.html) | Versão editável do texto. Abra localmente com o SVG na mesma pasta. Para exportar, escolha impressão em A4, escala de 100%, gráficos de fundo ativados e cabeçalhos do navegador desativados. |
