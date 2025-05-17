from rest_framework_simplejwt.authentication import JWTAuthentication

class CustomCookieJWTAuthentication(JWTAuthentication):
    """
    Tenta obter o token de autenticação primeiro do cookie 'access'.
    Se não existir, utiliza o método padrão (busca no cabeçalho Authorization).
    """
    def get_header(self, request):
        token = request.COOKIES.get('access')
        if token:
            return f"Bearer {token}"
        return super().get_header(request)

    def authenticate(self, request):
        header = self.get_header(request)
        if not header:
            return None

        parts = header.split(" ")
        if len(parts) != 2:
            return None

        token_str = parts[1]
        try:
            validated_token = self.get_validated_token(token_str)
            user = self.get_user(validated_token)
            return (user, validated_token)
        except Exception as e:
            return None