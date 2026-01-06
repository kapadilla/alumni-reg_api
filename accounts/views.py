from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import User
from .serializers import (
    LoginSerializer, UserSerializer,
    AdminCreateSerializer, AdminUpdateSerializer,
    AdminListSerializer, AdminDetailSerializer
)


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    """Admin login endpoint"""
    serializer = LoginSerializer(data=request.data)
    
    if serializer.is_valid():
        user = serializer.validated_data['user']
        tokens = get_tokens_for_user(user)
        
        return Response({
            'success': True,
            'message': 'Login successful',
            'data': {
                'token': tokens['access'],
                'refresh': tokens['refresh'],
                'user': {
                    'id': user.id,
                    'email': user.email,
                    'firstName': user.first_name,
                    'lastName': user.last_name,
                }
            }
        }, status=status.HTTP_200_OK)
    
    return Response({
        'success': False,
        'message': 'Invalid credentials',
        'errors': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    """Admin logout endpoint"""
    try:
        refresh_token = request.data.get('refresh')
        if refresh_token:
            token = RefreshToken(refresh_token)
            token.blacklist()
        
        return Response({
            'success': True,
            'message': 'Logged out successfully'
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({
            'success': False,
            'message': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def verify_token(request):
    """Verify JWT token"""
    return Response({
        'success': True,
        'data': {
            'valid': True,
            'user': UserSerializer(request.user).data
        }
    }, status=status.HTTP_200_OK)


# ============================================
# ADMIN MANAGEMENT VIEWS
# ============================================

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def admin_list_create(request):
    """List all admins or create a new admin"""
    if request.method == 'GET':
        admins = User.objects.all().order_by('-date_joined')
        serializer = AdminListSerializer(admins, many=True)
        return Response({
            'success': True,
            'data': {
                'admins': serializer.data,
                'total': admins.count()
            }
        }, status=status.HTTP_200_OK)
    
    elif request.method == 'POST':
        serializer = AdminCreateSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({
                'success': True,
                'message': 'Admin created successfully',
                'data': AdminDetailSerializer(user).data
            }, status=status.HTTP_201_CREATED)
        
        return Response({
            'success': False,
            'message': 'Validation failed',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def admin_detail(request, pk):
    """Get, update, or soft-delete an admin"""
    try:
        admin = User.objects.get(pk=pk)
    except User.DoesNotExist:
        return Response({
            'success': False,
            'message': 'Admin not found'
        }, status=status.HTTP_404_NOT_FOUND)
    
    if request.method == 'GET':
        serializer = AdminDetailSerializer(admin)
        return Response({
            'success': True,
            'data': serializer.data
        }, status=status.HTTP_200_OK)
    
    elif request.method == 'PUT':
        serializer = AdminUpdateSerializer(admin, data=request.data, partial=True)
        if serializer.is_valid():
            user = serializer.save()
            return Response({
                'success': True,
                'message': 'Admin updated successfully',
                'data': AdminDetailSerializer(user).data
            }, status=status.HTTP_200_OK)
        
        return Response({
            'success': False,
            'message': 'Validation failed',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        # Soft delete - set is_active to False
        admin.is_active = False
        admin.save()
        return Response({
            'success': True,
            'message': 'Admin deactivated successfully',
            'data': {
                'id': admin.id,
                'email': admin.email,
                'isActive': False
            }
        }, status=status.HTTP_200_OK)