from rest_framework_simplejwt.authentication import JWTAuthentication

class CookieJWTAuthentication(JWTAuthentication):
    """
    Autenticação via JWT buscando primeiro no header Authorization,
    e em seguida no cookie 'access'.
    """
    def authenticate(self, request):
        # Primeiro tenta o header padrão
        header = self.get_header(request)
        if header:
            raw_token = self.get_raw_token(header)
        else:
            # Cai no cookie se não tiver header
            raw_token = request.COOKIES.get('access')

        if raw_token is None:
            return None

        validated = self.get_validated_token(raw_token)
        user = self.get_user(validated)
        return user, validated
