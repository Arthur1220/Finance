from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken

from .models import User
from .serializers import UserSerializer
from core.authentication import CookieJWTAuthentication


class UserViewSet(viewsets.GenericViewSet):
    """
    ViewSet para registro, login, refresh, logout, perfil e atualização de usuário.
    Usa autenticação via JWT em cookie (CookieJWTAuthentication).
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    authentication_classes = [CookieJWTAuthentication]

    @action(detail=False, methods=['post'], permission_classes=[AllowAny], url_path='register')
    def register(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(
            {'status': 'Usuário criado com sucesso.', 'user': UserSerializer(user).data},
            status=status.HTTP_201_CREATED
        )

    @action(detail=False, methods=['post'], permission_classes=[AllowAny], url_path='login')
    def login(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        if not username or not password:
            return Response(
                {'error': 'Username e password são necessários.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Se vier email, busca o usuário e extrai o username
        if '@' in username:
            try:
                user_obj = User.objects.get(email=username)
                username = user_obj.username
            except User.DoesNotExist:
                return Response({'error': 'Credenciais inválidas.'}, status=status.HTTP_400_BAD_REQUEST)

        user = authenticate(username=username, password=password)
        if not user:
            return Response({'error': 'Credenciais inválidas.'}, status=status.HTTP_400_BAD_REQUEST)

        # Gera tokens
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        refresh_token = str(refresh)

        # Prepara resposta e cookies
        response = Response({'message': 'Login realizado com sucesso.'}, status=status.HTTP_200_OK)
        response.set_cookie('access', access_token, httponly=True, secure=True, samesite='Lax', path='/')
        response.set_cookie('refresh', refresh_token, httponly=True, secure=True, samesite='Lax', path='/')

        # Payload com dados do usuário
        response.data = {
            'access': access_token,
            'refresh': refresh_token,
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'phone': user.phone,
                'timezone': user.timezone,
                'currency': user.currency,
            }
        }
        return response

    @action(detail=False, methods=['post'], permission_classes=[AllowAny], url_path='refresh')
    def refresh(self, request):
        refresh_token = request.COOKIES.get('refresh')
        if not refresh_token:
            resp = Response({'error': 'Refresh token ausente.'}, status=status.HTTP_400_BAD_REQUEST)
            resp.delete_cookie('access', path='/')
            resp.delete_cookie('refresh', path='/')
            return resp

        try:
            refresh = RefreshToken(refresh_token)
            new_access = str(refresh.access_token)
            resp = Response({'message': 'Token atualizado com sucesso.'}, status=status.HTTP_200_OK)
            resp.set_cookie('access', new_access, httponly=True, secure=True, samesite='Lax', path='/')
            return resp
        except Exception as e:
            resp = Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
            resp.delete_cookie('access', path='/')
            resp.delete_cookie('refresh', path='/')
            return resp

    @action(detail=False, methods=['post'], permission_classes=[AllowAny], url_path='logout')
    def logout(self, request):
        refresh_token = request.COOKIES.get('refresh')
        if refresh_token:
            try:
                token = RefreshToken(refresh_token)
                token.blacklist()
            except Exception:
                pass

        resp = Response({'message': 'Logout realizado com sucesso.'}, status=status.HTTP_200_OK)
        resp.delete_cookie('access', path='/')
        resp.delete_cookie('refresh', path='/')
        return resp

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated], url_path='profile')
    def profile(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['put'], permission_classes=[IsAuthenticated], url_path='update')
    def update_profile(self, request):
        serializer = self.get_serializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)