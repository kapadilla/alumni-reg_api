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
    
    return Response({
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


@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def update_member(request, pk):
    """Update member information"""
    member = get_object_or_404(Member, pk=pk)
    application = member.application
    
    # Update fields from request
    data = request.data
    
    if 'personalDetails' in data:
        personal = data['personalDetails']
        if 'email' in personal:
            application.email = personal['email']
            member.email = personal['email']
        if 'mobileNumber' in personal:
            application.mobile_number = personal['mobileNumber']
        if 'currentAddress' in personal:
            application.current_address = personal['currentAddress']
    
    if 'professional' in data:
        professional = data['professional']
        if 'currentEmployer' in professional:
            application.current_employer = professional['currentEmployer']
        if 'jobTitle' in professional:
            application.job_title = professional['jobTitle']
        if 'industry' in professional:
            application.industry = professional['industry']
    
    application.save()
    member.save()
    
    return Response({
        'success': True,
        'message': 'Member updated successfully',
        'data': MemberDetailSerializer(member).data
    }, status=status.HTTP_200_OK)


@api_view(['DELETE', 'POST'])
@permission_classes([IsAuthenticated])
def revoke_membership(request, pk):
    """Revoke member's membership"""
    member = get_object_or_404(Member, pk=pk)
    member.is_active = False
    member.save()
    
    return Response({
        'success': True,
        'message': 'Membership revoked successfully',
        'data': {
            'memberId': member.id,
            'isActive': member.is_active
        }
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def export_members(request):
    """Export members list as CSV"""
    members = Member.objects.filter(is_active=True)
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="members.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['ID', 'Name', 'Email', 'Degree Program', 'Year Graduated', 'Member Since', 'Active'])
    
    for member in members:
        writer.writerow([
            member.id,
            member.full_name,
            member.email,
            member.application.degree_program.name,
            member.application.year_graduated,
            member.member_since.strftime('%Y-%m-%d'),
            'Yes' if member.is_active else 'No'
        ])
    
    return response