ADMIN_PASSWORD = "Admin123"


def check_admin_password(request):
    """Verifica se o header X-Admin-Password está correto."""
    senha = request.headers.get('X-Admin-Password', '')
    return senha == ADMIN_PASSWORD
