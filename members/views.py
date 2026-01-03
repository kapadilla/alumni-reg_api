from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.http import HttpResponse
import csv

from .models import Member
from .serializers import MemberListSerializer, MemberDetailSerializer
from applications.views import StandardResultsSetPagination


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_members(request):
    """List all approved members"""
    search = request.GET.get('search', '')
    
    queryset = Member.objects.filter(is_active=True)
    
    if search:
        queryset = queryset.filter(
            Q(full_name__icontains=search) |
            Q(email__icontains=search)
        )
    
    paginator = StandardResultsSetPagination()
    paginated_queryset = paginator.paginate_queryset(queryset, request)
    serializer = MemberListSerializer(paginated_queryset, many=True)
    
    return paginator.get_paginated_response({
        'success': True,
        'data': {
            'members': serializer.data,
            'pagination': {
                'currentPage': paginator.page.number,
                'totalPages': paginator.page.paginator.num_pages,
                'totalItems': paginator.page.paginator.count
            }
        }
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_member_detail(request, pk):
    """Get member details"""
    member = get_object_or_404(Member, pk=pk)
    serializer = MemberDetailSerializer(member)
    
    return Response({
        'success': True,
        'data': serializer.data
    }, status=status.HTTP_200_OK)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_member(request, pk):
    """Update member information"""
    member = get_object_or_404(Member, pk=pk)
    
    # You can add update logic here
    # For now, just a placeholder
    
    return Response({
        'success': True,
        'message': 'Member updated successfully'
    }, status=status.HTTP_200_OK)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def revoke_membership(request, pk):
    """Revoke member's membership"""
    member = get_object_or_404(Member, pk=pk)
    member.is_active = False
    member.save()
    
    return Response({
        'success': True,
        'message': 'Membership revoked successfully'
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def export_members(request):
    """Export members list as CSV"""
    members = Member.objects.filter(is_active=True)
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="members.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['ID', 'Name', 'Email', 'Degree Program', 'Year Graduated', 'Member Since'])
    
    for member in members:
        writer.writerow([
            member.id,
            member.full_name,
            member.email,
            member.application.degree_program.name,
            member.application.year_graduated,
            member.member_since.strftime('%Y-%m-%d')
        ])
    
    return response