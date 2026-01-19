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
from .filters import MemberFilter
from applications.pagination import MemberPagination


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_members(request):
    """List all members
    
    Query Parameters:
    - search: Search by name or email
    - ordering: Sort by field (prefix - for descending). Options: member_since, full_name, email
    - date_from: Filter from date (YYYY-MM-DD) on member_since
    - date_to: Filter to date (YYYY-MM-DD) on member_since
    - degree_program: Filter by degree program
    - year_graduated: Filter by graduation year
    - status: Filter by status (active, revoked, all). Default: all
    - page: Page number
    - limit: Items per page (default 20, max 100)
    """
    # Default to all members if no status filter provided
    status_param = request.GET.get('status', 'all')
    if status_param.lower() == 'all':
        queryset = Member.objects.all()
    elif status_param.lower() == 'revoked':
        queryset = Member.objects.filter(is_active=False)
    elif status_param.lower() == 'active':
        queryset = Member.objects.filter(is_active=True)
    else:  # default to all for any other value
        queryset = Member.objects.all()
    
    # Apply filters
    filterset = MemberFilter(request.GET, queryset=queryset)
    queryset = filterset.qs
    
    # Apply ordering
    ordering = request.GET.get('ordering', '-member_since')
    allowed_ordering = ['member_since', '-member_since', 'full_name', '-full_name', 'email', '-email']
    if ordering in allowed_ordering:
        queryset = queryset.order_by(ordering)
    else:
        queryset = queryset.order_by('-member_since')
    
    paginator = MemberPagination()
    paginated_queryset = paginator.paginate_queryset(queryset, request)
    serializer = MemberListSerializer(paginated_queryset, many=True)
    
    return paginator.get_paginated_response(serializer.data)



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
    """Revoke member's membership
    
    Request Body:
    - reason: Reason for revocation (required)
    - notes: Additional admin notes (optional)
    """
    from django.utils import timezone
    from applications.models import VerificationHistory
    from accounts.models import AdminActivityLog
    
    member = get_object_or_404(Member, pk=pk, is_active=True)
    
    reason = request.data.get('reason', '')
    if not reason:
        return Response({
            'success': False,
            'message': 'Revocation reason is required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    notes = request.data.get('notes', '')
    
    # Update member
    member.is_active = False
    member.revoked_at = timezone.now()
    member.revoked_by = request.user
    member.revocation_reason = reason
    member.save()
    
    # Update application status
    member.application.status = 'revoked'
    member.application.save()
    
    # Add audit trail
    VerificationHistory.objects.create(
        application=member.application,
        action='membership_revoked',
        performed_by=request.user,
        notes=f"Reason: {reason}" + (f"\nNotes: {notes}" if notes else "")
    )
    
    # Log admin activity
    AdminActivityLog.objects.create(
        admin=request.user,
        action='revoke_member',
        target_type='member',
        target_id=member.id,
        target_name=member.full_name,
        notes=f"Reason: {reason}" + (f"\nNotes: {notes}" if notes else "")
    )
    
    return Response({
        'success': True,
        'message': 'Membership revoked successfully',
        'data': {
            'memberId': member.id,
            'isActive': member.is_active,
            'revokedAt': member.revoked_at,
            'revokedBy': request.user.email,
            'reason': reason
        }
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def reinstate_membership(request, pk):
    """Reinstate a revoked member's membership
    
    Request Body:
    - notes: Admin notes for reinstatement (optional)
    """
    from django.utils import timezone
    from applications.models import VerificationHistory
    from accounts.models import AdminActivityLog
    
    member = get_object_or_404(Member, pk=pk, is_active=False)
    
    notes = request.data.get('notes', '')
    
    # Reactivate member
    member.is_active = True
    member.reinstated_at = timezone.now()
    member.reinstated_by = request.user
    member.save()
    
    # Update application status back to approved
    member.application.status = 'approved'
    member.application.save()
    
    # Add audit trail
    VerificationHistory.objects.create(
        application=member.application,
        action='membership_reinstated',
        performed_by=request.user,
        notes=notes or "Membership reinstated"
    )
    
    # Log admin activity
    AdminActivityLog.objects.create(
        admin=request.user,
        action='reinstate_member',
        target_type='member',
        target_id=member.id,
        target_name=member.full_name,
        notes=notes or "Membership reinstated"
    )
    
    return Response({
        'success': True,
        'message': 'Membership reinstated successfully',
        'data': {
            'memberId': member.id,
            'isActive': member.is_active,
            'reinstatedAt': member.reinstated_at,
            'reinstatedBy': request.user.email
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
            member.application.degree_program,
            member.application.year_graduated,
            member.member_since.strftime('%Y-%m-%d'),
            'Yes' if member.is_active else 'No'
        ])
    
    return response