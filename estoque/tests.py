
from django.test import TestCase
from django.core.exceptions import ValidationError
from django.db.models.deletion import ProtectedError

from .models import Categoria, Produto, MovimentacaoEstoque


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


class MovimentacaoEstoqueTest(TestCase):

    def setUp(self):
        self.categoria = Categoria.objects.create(
            nome="Cadernos"
        )

        self.produto = Produto.objects.create(
            categoria=self.categoria,
            sku="CAD001",
            nome="Caderno universitário",
            preco_compra="12.00",
            preco_venda="20.00",
            quantidade_estoque=10,
            estoque_minimo=2
        )

    # TESTE 1: Entrada de estoque

    def test_entrada_aumenta_estoque(self):
        MovimentacaoEstoque.objects.create(
            produto=self.produto,
            tipo=MovimentacaoEstoque.Tipo.ENTRADA,
            quantidade=5,
            motivo="Compra de mercadorias"
        )

        self.produto.refresh_from_db()

        self.assertEqual(self.produto.quantidade_estoque, 15)

    # TESTE 2: Saída de estoque

    def test_saida_diminui_estoque(self):
        MovimentacaoEstoque.objects.create(
            produto=self.produto,
            tipo=MovimentacaoEstoque.Tipo.SAIDA,
            quantidade=3,
            motivo="Venda de mercadorias"
        )

        self.produto.refresh_from_db()

        self.assertEqual(self.produto.quantidade_estoque, 7)

    # TESTE 3: Bloqueio de estoque insuficiente

    def test_bloqueia_saida_com_estoque_insuficiente(self):

        with self.assertRaises(ValidationError):
            MovimentacaoEstoque.objects.create(
                produto=self.produto,
                tipo=MovimentacaoEstoque.Tipo.SAIDA,
                quantidade=20,
                motivo="Teste de estoque insuficiente"
            )

        self.produto.refresh_from_db()

        self.assertEqual(self.produto.quantidade_estoque, 10)
        self.assertEqual(
            MovimentacaoEstoque.objects.count(), 0
        )

    # TESTE 4: Bloqueio de quantidade zero

    def test_bloqueia_quantidade_zero(self):

        with self.assertRaises(ValidationError):
            MovimentacaoEstoque.objects.create(
                produto=self.produto,
                tipo=MovimentacaoEstoque.Tipo.ENTRADA,
                quantidade=0,
                motivo="Teste de quantidade zero"
            )

        self.produto.refresh_from_db()

        self.assertEqual(self.produto.quantidade_estoque, 10)
        self.assertEqual(
            MovimentacaoEstoque.objects.count(), 0
        )

    # TESTE 5: Impede edição de movimentações registradas

    def test_movimentacao_nao_pode_ser_editada(self):

        movimentacao = MovimentacaoEstoque.objects.create(
            produto=self.produto,
            tipo=MovimentacaoEstoque.Tipo.ENTRADA,
            quantidade=5,
            motivo="Compra inicial"
        )

        movimentacao.motivo = "Tentativa de alteração"

        with self.assertRaises(ValidationError):
            movimentacao.save()

        self.produto.refresh_from_db()

        self.assertEqual(self.produto.quantidade_estoque, 15)

        self.assertEqual(
            MovimentacaoEstoque.objects.count(), 1
        )
