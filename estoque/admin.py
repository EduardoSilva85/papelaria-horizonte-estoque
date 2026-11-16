
from django.contrib import admin
from .models import Categoria, Produto, MovimentacaoEstoque


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
        "estoque_baixo",
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

    @admin.display(
        boolean=True,
        description="Estoque baixo"
    )
    def estoque_baixo(self, obj):
        return obj.estoque_baixo

@admin.register(MovimentacaoEstoque)
class MovimentacaoEstoqueAdmin(admin.ModelAdmin):

    list_display = (
        "produto",
        "tipo",
        "quantidade",
        "motivo",
        "criado_em",
    )

    search_fields = (
        "produto__sku",
        "produto__nome",
        "motivo",
    )

    list_filter = (
        "tipo",
        "criado_em",
    )

    readonly_fields = ("criado_em",)

    list_select_related = ("produto",)

    list_display_links = None

    ordering = ("-criado_em",)

    def has_change_permission(self, request, obj=None):
        if obj is not None:
            return False

        return super().has_change_permission(request, obj)

    def has_delete_permission(self, request, obj=None):
        return False
