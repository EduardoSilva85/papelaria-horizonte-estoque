
from django.test import TestCase
from django.db.models.deletion import ProtectedError
from .models import Categoria, Produto


class CategoriaTest(TestCase):

    def test_criar_categoria(self):
        categoria = Categoria.objects.create(
            nome="Cadernos",
            descricao="Cadernos escolares"
        )

        self.assertEqual(categoria.nome, "Cadernos")
        self.assertTrue(categoria.ativa)
        self.assertEqual(str(categoria), "Cadernos")


class ProdutoTest(TestCase):

    def setUp(self):
        self.categoria = Categoria.objects.create(
            nome="Canetas"
        )

    def test_criar_produto(self):
        produto = Produto.objects.create(
            categoria=self.categoria,
            sku="CAN001",
            nome="Caneta azul",
            preco_compra="1.50",
            preco_venda="3.00",
            quantidade_estoque=100,
            estoque_minimo=10
        )

        self.assertEqual(produto.nome, "Caneta azul")
        self.assertEqual(produto.quantidade_estoque, 100)
        self.assertEqual(str(produto), "CAN001 - Caneta azul")

    def test_categoria_nao_pode_ser_excluida_com_produtos(self):
        Produto.objects.create(
            categoria=self.categoria,
            sku="CAN002",
            nome="Caneta preta",
            preco_compra="1.50",
            preco_venda="3.00"
        )

        with self.assertRaises(ProtectedError):
            self.categoria.delete()
