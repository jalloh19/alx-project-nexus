"""User views and viewsets."""
from rest_framework import viewsets, status, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from .models import User, UserProfile
from .serializers import (
    UserSerializer,
    UserRegistrationSerializer,
    UserProfileSerializer,
    ChangePasswordSerializer
)


class UserViewSet(viewsets.ModelViewSet):
    """ViewSet for user management."""
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_permissions(self):
        if self.action in ['create', 'login']:
            return [AllowAny()]
        return [IsAuthenticated()]

    def get_serializer_class(self):
        if self.action == 'create':
            return UserRegistrationSerializer
        return UserSerializer

    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def login(self, request):
        """User login endpoint."""
        email = request.data.get('email')
        password = request.data.get('password')

        user = authenticate(request, username=email, password=password)

        if user is None:
            return Response(
                {'error': 'Invalid credentials'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        refresh = RefreshToken.for_user(user)
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': UserSerializer(user).data
        })

    @action(detail=False, methods=['get', 'patch'], permission_classes=[IsAuthenticated])
    def me(self, request):
        """Get or update current user details."""
        if request.method == 'GET':
            serializer = UserSerializer(request.user)
            return Response(serializer.data)

        serializer = UserSerializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def change_password(self, request):
        """Change user password."""
        serializer = ChangePasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = request.user
        if not user.check_password(serializer.validated_data['old_password']):
            return Response(
                {'error': 'Old password is incorrect'},
                status=status.HTTP_400_BAD_REQUEST
            )

        user.set_password(serializer.validated_data['new_password'])
        user.save()
        return Response({'message': 'Password changed successfully'})


class UserProfileViewSet(viewsets.ModelViewSet):
    """ViewSet for user profile management."""
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return UserProfile.objects.filter(user=self.request.user)

    @action(detail=False, methods=['get', 'patch'])
    def my_profile(self, request):
        """Get or update current user's profile."""
        profile, created = UserProfile.objects.get_or_create(user=request.user)

        if request.method == 'GET':
            serializer = UserProfileSerializer(profile)
            return Response(serializer.data)

        serializer = UserProfileSerializer(profile, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
