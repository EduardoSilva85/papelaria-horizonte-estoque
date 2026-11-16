
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models, transaction


class Categoria(models.Model):
    nome = models.CharField(max_length=100, unique=True)
    descricao = models.TextField(blank=True)
    ativa = models.BooleanField(default=True)

    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Categoria"
        verbose_name_plural = "Categorias"
        ordering = ["nome"]

    def __str__(self):
        return self.nome


class Produto(models.Model):
    categoria = models.ForeignKey(
        Categoria,
        on_delete=models.PROTECT,
        related_name="produtos"
    )

    sku = models.CharField(max_length=30, unique=True)
    nome = models.CharField(max_length=150)
    descricao = models.TextField(blank=True)

    preco_compra = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    preco_venda = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    quantidade_estoque = models.PositiveIntegerField(default=0)
    estoque_minimo = models.PositiveIntegerField(default=0)

    ativo = models.BooleanField(default=True)

    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Produto"
        verbose_name_plural = "Produtos"
        ordering = ["nome"]

    def __str__(self):
        return f"{self.sku} - {self.nome}"


class MovimentacaoEstoque(models.Model):

    class Tipo(models.TextChoices):
        ENTRADA = "ENTRADA", "Entrada"
        SAIDA = "SAIDA", "Saída"

    produto = models.ForeignKey(
        Produto,
        on_delete=models.PROTECT,
        related_name="movimentacoes"
    )

    tipo = models.CharField(
        max_length=7,
        choices=Tipo.choices
    )

    quantidade = models.PositiveIntegerField(
        validators=[MinValueValidator(1)]
    )

    motivo = models.CharField(max_length=200)

    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Movimentação de Estoque"
        verbose_name_plural = "Movimentações de Estoque"
        ordering = ["-criado_em"]

    def __str__(self):
        return (
            f"{self.get_tipo_display()} - "
            f"{self.produto.nome} - {self.quantidade}"
        )

    def save(self, *args, **kwargs):

        if self.pk is not None:
            raise ValidationError(
                "Movimentações não podem ser editadas. "
                "Registre uma nova movimentação para corrigir."
            )

        if self.quantidade is None or self.quantidade < 1:
            raise ValidationError({
                "quantidade": "A quantidade deve ser maior que zero."
            })

        with transaction.atomic():

            produto = Produto.objects.select_for_update().get(
                pk=self.produto_id
            )

            if self.tipo == self.Tipo.ENTRADA:
                produto.quantidade_estoque += self.quantidade

            elif self.tipo == self.Tipo.SAIDA:

                if produto.quantidade_estoque < self.quantidade:
                    raise ValidationError({
                        "quantidade": (
                            f"Estoque insuficiente. "
                            f"Disponível: {produto.quantidade_estoque}."
                        )
                    })

                produto.quantidade_estoque -= self.quantidade

            else:
                raise ValidationError({
                    "tipo": "Selecione um tipo de movimentação válido."
                })

            produto.save(
                update_fields=[
                    "quantidade_estoque",
                    "atualizado_em"
                ]
            )

            super().save(*args, **kwargs)
