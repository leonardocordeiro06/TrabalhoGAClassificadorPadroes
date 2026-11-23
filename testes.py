"""Reproduz os dois casos do relatório e verifica situações de fronteira."""

import unittest
from fractions import Fraction
from pathlib import Path

from grafico import recortar_regiao
from modelo import classe_prevista, equacoes_normais, escore, ler_treino, resolver_sistema


class TestesDoClassificador(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Ajuste único para os testes do relatório, sem incluir os pontos consultados.
        cls.amostras = ler_treino(Path(__file__).with_name("treino.csv"))
        cls.pesos, _ = resolver_sistema(*equacoes_normais(cls.amostras))

    def verificar_caso(self, ponto, esperado, classe):
        # Compara com os valores calculados à mão a partir do sistema do relatório.
        self.assertNotIn(ponto, [(u, t) for u, t, _ in self.amostras])
        calculado = escore(self.pesos, *ponto)
        self.assertEqual(calculado, esperado)
        self.assertEqual(classe_prevista(calculado), classe)

    def test_t1_rotina(self):
        self.verificar_caso((8, 15), Fraction(-205, 1499), -1)

    def test_t2_prioritario(self):
        self.verificar_caso((8, 20), Fraction(287, 1499), 1)

    def test_empate_exato(self):
        # Para oito usuários, a reta passa por t = 205/12 minutos.
        self.verificar_caso((8, Fraction(205, 12)), 0, 1)

    def test_reta_vertical(self):
        # Neste conjunto, apenas a primeira coordenada determina a classe.
        amostras = [(0, 0, -1), (0, 2, -1), (2, 0, 1), (2, 2, 1)]
        pesos, posto = resolver_sistema(*equacoes_normais(amostras))
        self.assertEqual((pesos, posto), ((-1, 1, 0), 3))
        _, cortes = recortar_regiao(pesos, [(0, 0), (2, 0), (2, 2), (0, 2)])
        self.assertEqual(set(cortes), {(1, 0), (1, 2)})

    def test_base_colinear(self):
        # Uma variável redundante permite várias soluções. A função escolhe uma delas.
        amostras = [(1, 1, -1), (3, 3, 1)]
        pesos, posto = resolver_sistema(*equacoes_normais(amostras))
        self.assertEqual(posto, 2)
        self.assertEqual([escore(pesos, u, t) for u, t, _ in amostras], [-1, 1])

    def test_sem_separacao_linear(self):
        # Um padrão XOR simétrico leva a escore constante neste ajuste.
        amostras = [(0, 0, -1), (0, 2, 1), (2, 0, 1), (2, 2, -1)]
        pesos, _ = resolver_sistema(*equacoes_normais(amostras))
        self.assertEqual(pesos, (0, 0, 0))
        self.assertEqual(classe_prevista(escore(pesos, 1, 1)), 1)


# A biblioteca padrão encontra e executa todos os métodos iniciados por test_.
if __name__ == "__main__":
    unittest.main(verbosity=2)
