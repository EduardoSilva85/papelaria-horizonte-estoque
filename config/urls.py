
import os
import secrets

from django.conf import settings
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password
from django.http import HttpResponse
from django.middleware.csrf import get_token
from django.urls import path
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_http_methods


def setup_page(csrf_token, message=""):
    return f"""
    <!DOCTYPE html>
    <html lang="pt-br">
    <head>
        <meta charset="UTF-8">
        <title>Configuração inicial</title>
        <style>
            body {{ background:#202020; color:white; font-family:Arial;
                   max-width:450px; margin:60px auto; padding:20px; }}
            input {{ width:100%; padding:12px; margin:8px 0 18px;
                     box-sizing:border-box; }}
            button {{ padding:12px 20px; cursor:pointer; }}
        </style>
    </head>
    <body>
        <h2>Criar administrador</h2>
        <p>{message}</p>
        <form method="POST">
            <input type="hidden" name="csrfmiddlewaretoken"
                   value="{csrf_token}">

            <label>Token de configuração</label>
            <input type="password" name="setup_token" required>

            <label>Usuário</label>
            <input name="username" value="eduardo" required>

            <label>E-mail</label>
            <input type="email" name="email" required>

            <label>Senha</label>
            <input type="password" name="password" required>

            <label>Confirmar senha</label>
            <input type="password" name="password2" required>

            <button type="submit">Criar administrador</button>
        </form>
    </body>
    </html>
    """


@csrf_protect
@require_http_methods(["GET", "POST"])
def setup_admin(request):
    setup_token = os.environ.get("DJANGO_SETUP_TOKEN", "")

    if not setup_token:
        return HttpResponse("Configuração indisponível.", status=503)

    if request.method == "GET":
        return HttpResponse(setup_page(get_token(request)))

    token = request.POST.get("setup_token", "")

    if not secrets.compare_digest(token, setup_token):
        return HttpResponse("Token inválido.", status=403)

    username = request.POST.get("username", "").strip()
    email = request.POST.get("email", "").strip()
    password = request.POST.get("password", "")
    password2 = request.POST.get("password2", "")

    if not username or not email or not password:
        return HttpResponse("Preencha todos os campos.", status=400)

    if password != password2:
        return HttpResponse("As senhas não coincidem.", status=400)

    User = get_user_model()
    user, created = User.objects.get_or_create(
        username=username,
        defaults={"email": email}
    )

    try:
        validate_password(password, user)
    except ValidationError:
        if created:
            user.delete()
        return HttpResponse(
            "Senha não atende aos requisitos de segurança. Tente outra.",
            status=400
        )

    user.email = email
    user.is_staff = True
    user.is_superuser = True
    user.is_active = True
    user.set_password(password)
    user.save()

    return HttpResponse(
        "Administrador criado/atualizado com sucesso! "
        "Agora você pode acessar o painel Django."
    )


urlpatterns = [
    path("setup-admin/", setup_admin, name="setup_admin"),
    path("admin/", admin.site.urls),
]
