from rest_framework import status, generics
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.response import Response
from rest_framework.filters import OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db.models import Q, Count
from django.http import HttpResponse
import csv

from .models import (
    MembershipApplication, VerificationHistory
)
from members.models import Member
from .serializers import (
    MembershipApplicationListSerializer,
    MembershipApplicationDetailSerializer,
    MembershipApplicationCreateSerializer,
    VerifyAlumniSerializer,
    RejectApplicationSerializer,
)
from .pagination import ApplicantPagination
from .filters import MembershipApplicationFilter, RejectedApplicationFilter


# ============================================
# REGISTRATION ENDPOINTS
# ============================================

@api_view(['POST'])
@parser_classes([MultiPartParser, FormParser, JSONParser])
@permission_classes([AllowAny])
def submit_registration(request):
    """Submit a new alumni registration"""
    serializer = MembershipApplicationCreateSerializer(data=request.data)
    
    if serializer.is_valid():
        application = serializer.save()
        
        return Response({
            'success': True,
            'message': 'Registration submitted successfully',
            'data': {
                'applicationId': application.id,
                'status': application.status,
                'submittedAt': application.date_applied
            }
        }, status=status.HTTP_201_CREATED)
    
    return Response({
        'success': False,
        'message': 'Validation failed',
        'errors': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([AllowAny])
def check_email_availability(request):
    """Check if email is available"""
    email = request.GET.get('email')
    
    if not email:
        return Response({
            'success': False,
            'message': 'Email parameter is required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    exists = MembershipApplication.objects.filter(email=email).exists()
    
    return Response({
        'success': True,
        'data': {
            'available': not exists,
            'message': 'Email is available' if not exists else 'Email already registered'
        }
    }, status=status.HTTP_200_OK)


# ============================================
# ALUMNI VERIFICATION ENDPOINTS (Step 1)
# ============================================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_pending_alumni_verification(request):
    """List all applications pending alumni verification
    
    Query Parameters:
    - search: Search by name or email
    - ordering: Sort by field (prefix - for descending). Options: date_applied, first_name, last_name, email
    - date_from: Filter from date (YYYY-MM-DD)
    - date_to: Filter to date (YYYY-MM-DD)
    - degree_program: Filter by degree program
    - year_graduated: Filter by graduation year
    - page: Page number
    - limit: Items per page (default 20, max 100)
    """
    queryset = MembershipApplication.objects.filter(
        status='pending_alumni_verification'
    )
    
    # Apply filters
    filterset = MembershipApplicationFilter(request.GET, queryset=queryset)
    queryset = filterset.qs
    
    # Apply ordering
    ordering = request.GET.get('ordering', '-date_applied')
    allowed_ordering = ['date_applied', '-date_applied', 'first_name', '-first_name', 
                        'last_name', '-last_name', 'email', '-email']
    if ordering in allowed_ordering:
        queryset = queryset.order_by(ordering)
    else:
        queryset = queryset.order_by('-date_applied')
    
    paginator = ApplicantPagination()
    paginated_queryset = paginator.paginate_queryset(queryset, request)
    serializer = MembershipApplicationListSerializer(paginated_queryset, many=True)
    
    return paginator.get_paginated_response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_alumni_verification_detail(request, pk):
    """Get detailed information for alumni verification"""
    application = get_object_or_404(
        MembershipApplication,
        pk=pk,
        status='pending_alumni_verification'
    )
    
    serializer = MembershipApplicationDetailSerializer(application)
    
    return Response({
        'success': True,
        'data': serializer.data
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def verify_alumni(request, pk):
    """Verify applicant as UP Cebu alumni"""
    from accounts.models import AdminActivityLog
    
    application = get_object_or_404(
        MembershipApplication,
        pk=pk,
        status='pending_alumni_verification'
    )
    
    serializer = VerifyAlumniSerializer(data=request.data)
    
    if serializer.is_valid():
        # Update application
        application.status = 'pending_payment_verification'
        application.alumni_verified_at = timezone.now()
        application.alumni_verified_by = request.user
        
        if serializer.validated_data.get('notes'):
            application.admin_notes = serializer.validated_data['notes']
        
        application.save()
        
        # Create history entry
        VerificationHistory.objects.create(
            application=application,
            action='alumni_verified',
            performed_by=request.user,
            notes=serializer.validated_data.get('notes', '')
        )
        
        # Log admin activity
        AdminActivityLog.objects.create(
            admin=request.user,
            action='verify_alumni',
            target_type='application',
            target_id=application.id,
            target_name=application.full_name,
            notes=serializer.validated_data.get('notes', '')
        )
        
        return Response({
            'success': True,
            'message': 'Applicant verified as alumni',
            'data': {
                'applicationId': application.id,
                'status': application.status,
                'verifiedAt': application.alumni_verified_at,
                'verifiedBy': request.user.email
            }
        }, status=status.HTTP_200_OK)
    
    return Response({
        'success': False,
        'message': 'Validation failed',
        'errors': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def reject_alumni_verification(request, pk):
    """Reject application during alumni verification"""
    from accounts.models import AdminActivityLog
    
    application = get_object_or_404(
        MembershipApplication,
        pk=pk,
        status='pending_alumni_verification'
    )
    
    serializer = RejectApplicationSerializer(data=request.data)
    
    if serializer.is_valid():
        # Update application
        application.status = 'rejected'
        application.rejection_stage = 'alumni_verification'
        application.rejection_reason = serializer.validated_data['reason']
        application.rejected_at = timezone.now()
        application.rejected_by = request.user
        application.save()
        
        # Create history entry
        VerificationHistory.objects.create(
            application=application,
            action='rejected',
            performed_by=request.user,
            notes=f"Rejected: {serializer.validated_data['reason']}"
        )
        
        # Log admin activity
        AdminActivityLog.objects.create(
            admin=request.user,
            action='reject_alumni',
            target_type='application',
            target_id=application.id,
            target_name=application.full_name,
            notes=serializer.validated_data['reason']
        )
        
        return Response({
            'success': True,
            'message': 'Application rejected',
            'data': {
                'applicationId': application.id,
                'status': application.status,
                'rejectionStage': application.rejection_stage,
                'rejectedAt': application.rejected_at,
                'reason': application.rejection_reason
            }
        }, status=status.HTTP_200_OK)
    
    return Response({
        'success': False,
        'message': 'Validation failed',
        'errors': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def export_alumni_verification(request):
    """Export pending alumni verification list as CSV"""
    applications = MembershipApplication.objects.filter(
        status='pending_alumni_verification'
    )
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="pending_alumni_verification.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['ID', 'Name', 'Email', 'Degree Program', 'Year Graduated', 'Student Number', 'Date Applied'])
    
    for app in applications:
        writer.writerow([
            app.id,
            app.full_name,
            app.email,
            app.degree_program,
            app.year_graduated,
            app.student_number or 'N/A',
            app.date_applied.strftime('%Y-%m-%d')
        ])
    
    return response


# ============================================
# PAYMENT VERIFICATION ENDPOINTS (Step 2)
# ============================================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_pending_payment_verification(request):
    """List all applications pending payment verification
    
    Query Parameters:
    - search: Search by name or email
    - ordering: Sort by field (prefix - for descending). Options: alumni_verified_at, first_name, last_name, email
    - date_from: Filter from date (YYYY-MM-DD) on alumni_verified_at
    - date_to: Filter to date (YYYY-MM-DD) on alumni_verified_at
    - degree_program: Filter by degree program
    - year_graduated: Filter by graduation year
    - page: Page number
    - limit: Items per page (default 20, max 100)
    """
    queryset = MembershipApplication.objects.filter(
        status='pending_payment_verification'
    )
    
    # Apply filters
    filterset = MembershipApplicationFilter(request.GET, queryset=queryset)
    queryset = filterset.qs
    
    # Apply ordering
    ordering = request.GET.get('ordering', '-alumni_verified_at')
    allowed_ordering = ['alumni_verified_at', '-alumni_verified_at', 'first_name', '-first_name', 
                        'last_name', '-last_name', 'email', '-email']
    if ordering in allowed_ordering:
        queryset = queryset.order_by(ordering)
    else:
        queryset = queryset.order_by('-alumni_verified_at')
    
    paginator = ApplicantPagination()
    paginated_queryset = paginator.paginate_queryset(queryset, request)
    
    # Custom serialization for payment verification view
    data = []
    for app in paginated_queryset:
        data.append({
            'id': app.id,
            'name': app.full_name,
            'email': app.email,
            'paymentMethod': app.payment_method,
            'amount': 5000,
            'alumniVerifiedDate': app.alumni_verified_at.strftime('%Y-%m-%d') if app.alumni_verified_at else None
        })
    
    return paginator.get_paginated_response(data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_payment_verification_detail(request, pk):
    """Get detailed information for payment verification"""
    application = get_object_or_404(
        MembershipApplication,
        pk=pk,
        status='pending_payment_verification'
    )
    
    serializer = MembershipApplicationDetailSerializer(application)
    data = serializer.data
    data['amount'] = 5000  # Add payment amount
    
    return Response({
        'success': True,
        'data': data
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def confirm_payment(request, pk):
    """Confirm payment and approve member"""
    from accounts.models import AdminActivityLog
    
    application = get_object_or_404(
        MembershipApplication,
        pk=pk,
        status='pending_payment_verification'
    )
    
    serializer = VerifyAlumniSerializer(data=request.data)
    
    if serializer.is_valid():
        # Update application
        application.status = 'approved'
        application.approved_at = timezone.now()
        application.approved_by = request.user
        
        if serializer.validated_data.get('notes'):
            application.admin_notes += f"\n{serializer.validated_data['notes']}"
        
        application.save()
        
        # Create member record
        member = Member.objects.create(
            application=application
        )
        
        # Create history entry
        VerificationHistory.objects.create(
            application=application,
            action='payment_confirmed',
            performed_by=request.user,
            notes=serializer.validated_data.get('notes', '')
        )
        
        # Log admin activity
        AdminActivityLog.objects.create(
            admin=request.user,
            action='approve_member',
            target_type='member',
            target_id=member.id,
            target_name=application.full_name,
            notes=serializer.validated_data.get('notes', '')
        )
        
        return Response({
            'success': True,
            'message': 'Payment confirmed. Member approved.',
            'data': {
                'applicationId': application.id,
                'memberId': member.id,
                'status': application.status,
                'memberSince': member.member_since,
                'approvedAt': application.approved_at
            }
        }, status=status.HTTP_200_OK)
    
    return Response({
        'success': False,
        'message': 'Validation failed',
        'errors': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def reject_payment_verification(request, pk):
    """Reject application during payment verification"""
    from accounts.models import AdminActivityLog
    
    application = get_object_or_404(
        MembershipApplication,
        pk=pk,
        status='pending_payment_verification'
    )
    
    serializer = RejectApplicationSerializer(data=request.data)
    
    if serializer.is_valid():
        # Update application
        application.status = 'rejected'
        application.rejection_stage = 'payment_verification'
        application.rejection_reason = serializer.validated_data['reason']
        application.rejected_at = timezone.now()
        application.rejected_by = request.user
        application.save()
        
        # Create history entry
        VerificationHistory.objects.create(
            application=application,
            action='rejected',
            performed_by=request.user,
            notes=f"Rejected: {serializer.validated_data['reason']}"
        )
        
        # Log admin activity
        AdminActivityLog.objects.create(
            admin=request.user,
            action='reject_payment',
            target_type='application',
            target_id=application.id,
            target_name=application.full_name,
            notes=serializer.validated_data['reason']
        )
        
        return Response({
            'success': True,
            'message': 'Application rejected',
            'data': {
                'applicationId': application.id,
                'status': application.status,
                'rejectionStage': application.rejection_stage,
                'rejectedAt': application.rejected_at,
                'reason': application.rejection_reason
            }
        }, status=status.HTTP_200_OK)
    
    return Response({
        'success': False,
        'message': 'Validation failed',
        'errors': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def export_payment_verification(request):
    """Export pending payment verification list as CSV"""
    applications = MembershipApplication.objects.filter(
        status='pending_payment_verification'
    )
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="pending_payment_verification.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['ID', 'Name', 'Email', 'Payment Method', 'Alumni Verified Date'])
    
    for app in applications:
        writer.writerow([
            app.id,
            app.full_name,
            app.email,
            app.payment_method,
            app.alumni_verified_at.strftime('%Y-%m-%d') if app.alumni_verified_at else 'N/A'
        ])
    
    return response


# ============================================
# REJECTED APPLICANTS ENDPOINTS
# ============================================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_rejected_applicants(request):
    """List all rejected applicants
    
    Query Parameters:
    - search: Search by name or email
    - rejection_stage: Filter by rejection stage (alumni_verification, payment_verification)
    - ordering: Sort by field (prefix - for descending). Options: rejected_at, first_name, last_name, email
    - date_from: Filter from date (YYYY-MM-DD) on date_applied
    - date_to: Filter to date (YYYY-MM-DD) on date_applied
    - rejected_from: Filter from date (YYYY-MM-DD) on rejected_at
    - rejected_to: Filter to date (YYYY-MM-DD) on rejected_at
    - degree_program: Filter by degree program
    - year_graduated: Filter by graduation year
    - page: Page number
    - limit: Items per page (default 20, max 100)
    """
    queryset = MembershipApplication.objects.filter(status='rejected')
    
    # Apply filters (RejectedApplicationFilter includes rejection_stage)
    filterset = RejectedApplicationFilter(request.GET, queryset=queryset)
    queryset = filterset.qs
    
    # Apply ordering
    ordering = request.GET.get('ordering', '-rejected_at')
    allowed_ordering = ['rejected_at', '-rejected_at', 'first_name', '-first_name', 
                        'last_name', '-last_name', 'email', '-email']
    if ordering in allowed_ordering:
        queryset = queryset.order_by(ordering)
    else:
        queryset = queryset.order_by('-rejected_at')
    
    paginator = ApplicantPagination()
    paginated_queryset = paginator.paginate_queryset(queryset, request)
    
    data = []
    for app in paginated_queryset:
        data.append({
            'id': app.id,
            'name': app.full_name,
            'email': app.email,
            'rejectedAt': app.rejected_at.strftime('%Y-%m-%d') if app.rejected_at else None,
            'rejectionStage': app.get_rejection_stage_display() if app.rejection_stage else 'N/A',
            'reason': app.rejection_reason
        })
    
    return paginator.get_paginated_response(data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_rejected_applicant_detail(request, pk):
    """Get rejected applicant details"""
    application = get_object_or_404(
        MembershipApplication,
        pk=pk,
        status='rejected'
    )
    
    serializer = MembershipApplicationDetailSerializer(application)
    
    return Response({
        'success': True,
        'data': serializer.data
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def export_rejected_applicants(request):
    """Export rejected applicants list as CSV"""
    applications = MembershipApplication.objects.filter(status='rejected')
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="rejected_applicants.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['ID', 'Name', 'Email', 'Rejection Stage', 'Reason', 'Rejected Date'])
    
    for app in applications:
        writer.writerow([
            app.id,
            app.full_name,
            app.email,
            app.get_rejection_stage_display() if app.rejection_stage else 'N/A',
            app.rejection_reason,
            app.rejected_at.strftime('%Y-%m-%d') if app.rejected_at else 'N/A'
        ])
    
    return response


# ============================================
# DASHBOARD ENDPOINTS
# ============================================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_stats(request):
    """Get dashboard statistics"""
    stats = [
        {
            'label': 'Pending Alumni Verification',
            'count': MembershipApplication.objects.filter(status='pending_alumni_verification').count()
        },
        {
            'label': 'Pending Payment Verification',
            'count': MembershipApplication.objects.filter(status='pending_payment_verification').count()
        },
        {
            'label': 'Approved Members',
            'count': Member.objects.filter(is_active=True).count()
        }
    ]
    
    return Response({
        'success': True,
        'data': {
            'stats': stats
        }
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_activity(request):
    """Get recent activity from all sources
    
    Combines:
    - VerificationHistory (submissions, approvals, rejections, revocations, reinstatements)
    - AdminActivityLog (admin login, logout, deactivation, reactivation)
    """
    from accounts.models import AdminActivityLog
    from itertools import chain
    from operator import attrgetter
    
    limit = int(request.GET.get('limit', 10))
    
    # Get recent verification history
    verification_activities = VerificationHistory.objects.select_related(
        'application', 'performed_by'
    ).all()[:limit * 2]  # Get extra to ensure we have enough after combining
    
    # Get recent admin activity logs
    admin_activities = AdminActivityLog.objects.select_related('admin').all()[:limit * 2]
    
    # Convert to unified format
    activities = []
    
    # Add verification history activities
    for vh in verification_activities:
        action_map = {
            'submitted': 'Application Submitted',
            'alumni_verified': 'Alumni Verified',
            'payment_confirmed': 'Member Approved',
            'rejected': 'Application Rejected',
            'membership_revoked': 'Membership Revoked',
            'membership_reinstated': 'Membership Reinstated',
        }
        
        activities.append({
            'id': f'vh-{vh.id}',
            'type': action_map.get(vh.action, vh.get_action_display()),
            'description': f"{vh.application.full_name}",
            'performedBy': vh.performed_by.email if vh.performed_by else 'System',
            'timestamp': vh.timestamp,
            'notes': vh.notes
        })
    
    # Add admin activity log activities
    for al in admin_activities:
        # Skip login/logout and actions already shown via VerificationHistory
        exclude_actions = [
            'login', 'logout',
            'verify_alumni', 'reject_alumni', 
            'approve_member', 'reject_payment',
            'revoke_member', 'reinstate_member'
        ]
        if al.action in exclude_actions:
            continue
            
        action_map = {
            'verify_alumni': 'Verified Alumni',
            'reject_alumni': 'Rejected Alumni',
            'approve_member': 'Approved Member',
            'reject_payment': 'Rejected Payment',
            'revoke_member': 'Revoked Membership',
            'reinstate_member': 'Reinstated Membership',
            'deactivate_admin': 'Deactivated Admin',
            'reactivate_admin': 'Reactivated Admin',
        }
        
        description = al.target_name if al.target_name else f"{al.get_target_type_display()} ID {al.target_id}"
        
        activities.append({
            'id': f'al-{al.id}',
            'type': action_map.get(al.action, al.get_action_display()),
            'description': description,
            'performedBy': al.admin.email,
            'timestamp': al.timestamp,
            'notes': al.notes
        })
    
    # Sort by timestamp (most recent first) and limit
    activities.sort(key=lambda x: x['timestamp'], reverse=True)
    activities = activities[:limit]
    
    # Format timestamps
    for activity in activities:
        activity['timestamp'] = activity['timestamp'].strftime('%Y-%m-%d %H:%M:%S')
    
    return Response({
        'success': True,
        'data': {
            'activities': activities
        }
    }, status=status.HTTP_200_OK)

# ============================================
# REFERENCE DATA ENDPOINTS
# ============================================


@api_view(['GET'])
@permission_classes([AllowAny])
def list_degree_programs(request):
    """List all degree programs"""
    programs = list(
        MembershipApplication.objects.values_list('degree_program', flat=True)
        .distinct()
        .order_by('degree_program')
    )
    return Response({
        'success': True,
        'data': programs
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def filter_options(request):
    """Get filter options for dropdowns
    
    Returns available degree programs, graduation years, and rejection stages.
    """
    # Get distinct degree programs (from stored applications)
    degree_programs = list(
        MembershipApplication.objects.values_list('degree_program', flat=True)
        .distinct()
        .order_by('degree_program')
    )
    # Get distinct campuses
    campuses = list(
        MembershipApplication.objects.values_list('campus', flat=True)
        .distinct()
        .order_by('campus')
    )
    
    # Get distinct graduation years
    years = list(
        MembershipApplication.objects.values_list('year_graduated', flat=True)
        .distinct()
        .order_by('-year_graduated')
    )
    
    return Response({
        'success': True,
        'data': {
            'degreePrograms': degree_programs,
            'campuses': [c for c in campuses if c],
            'years': [y for y in years if y],
            'rejectionStages': [
                {'value': 'alumni_verification', 'label': 'Alumni Verification'},
                {'value': 'payment_verification', 'label': 'Payment Verification'},
            ]
        }
    }, status=status.HTTP_200_OK)