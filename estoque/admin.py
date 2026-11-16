
from django.contrib import admin
from .models import Categoria, Produto


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):

    list_display = (
        "nome",
        "ativa",
        "criado_em",
        "atualizado_em",
    )

    search_fields = ("nome", "descricao")

    list_filter = ("ativa",)

    readonly_fields = (
        "criado_em",
        "atualizado_em",
    )

    ordering = ("nome",)


@admin.register(Produto)
class ProdutoAdmin(admin.ModelAdmin):

    list_display = (
        "sku",
        "nome",
        "categoria",
        "preco_compra",
        "preco_venda",
        "quantidade_estoque",
        "estoque_minimo",
        "ativo",
    )

    search_fields = (
        "sku",
        "nome",
        "descricao",
    )

    list_filter = (
        "categoria",
        "ativo",
    )

    readonly_fields = (
        "criado_em",
        "atualizado_em",
    )

    list_select_related = ("categoria",)

    ordering = ("nome",)
