from rest_framework import status, generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db.models import Q, Count
from django.http import HttpResponse
import csv

from .models import (
    MembershipApplication, Province, City, Barangay,
    DegreeProgram, VerificationHistory
)
from members.models import Member
from .serializers import (
    MembershipApplicationListSerializer,
    MembershipApplicationDetailSerializer,
    MembershipApplicationCreateSerializer,
    VerifyAlumniSerializer,
    RejectApplicationSerializer,
    ProvinceSerializer,
    CitySerializer,
    BarangaySerializer,
    DegreeProgramSerializer,
)


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'limit'
    max_page_size = 100

    def get_paginated_response(self, data):
        # Return custom format matching the spec
        return Response({
            'success': True,
            'data': {
                'applicants': data.get('applicants') or data.get('members') or data,
                'pagination': {
                    'currentPage': self.page.number,
                    'totalPages': self.page.paginator.num_pages,
                    'totalItems': self.page.paginator.count
                }
            }
        })

# ============================================
# REGISTRATION ENDPOINTS
# ============================================

@api_view(['POST'])
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
    """List all applications pending alumni verification"""
    search = request.GET.get('search', '')
    
    queryset = MembershipApplication.objects.filter(
        status='pending_alumni_verification'
    )
    
    if search:
        queryset = queryset.filter(
            Q(first_name__icontains=search) |
            Q(last_name__icontains=search) |
            Q(email__icontains=search)
        )
    
    paginator = StandardResultsSetPagination()
    paginated_queryset = paginator.paginate_queryset(queryset, request)
    serializer = MembershipApplicationListSerializer(paginated_queryset, many=True)
    
    # Format to match spec
    return Response({
        'success': True,
        'data': {
            'applicants': serializer.data,
            'pagination': {
                'currentPage': paginator.page.number,
                'totalPages': paginator.page.paginator.num_pages,
                'totalItems': paginator.page.paginator.count
            }
        }
    })


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
            app.degree_program.name,
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
    """List all applications pending payment verification"""
    search = request.GET.get('search', '')
    
    queryset = MembershipApplication.objects.filter(
        status='pending_payment_verification'
    )
    
    if search:
        queryset = queryset.filter(
            Q(first_name__icontains=search) |
            Q(last_name__icontains=search) |
            Q(email__icontains=search)
        )
    
    paginator = StandardResultsSetPagination()
    paginated_queryset = paginator.paginate_queryset(queryset, request)
    
    # Custom serialization for payment verification view
    data = []
    for app in paginated_queryset:
        data.append({
            'id': app.id,
            'name': app.full_name,
            'email': app.email,
            'paymentMethod': app.payment_method,
            'amount': 5000,  # You can make this dynamic
            'alumniVerifiedDate': app.alumni_verified_at.strftime('%Y-%m-%d') if app.alumni_verified_at else None
        })
    
    return paginator.get_paginated_response({
        'success': True,
        'data': {
            'applicants': data,
            'pagination': {
                'currentPage': paginator.page.number,
                'totalPages': paginator.page.paginator.num_pages,
                'totalItems': paginator.page.paginator.count
            }
        }
    })


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
    """List all rejected applicants"""
    search = request.GET.get('search', '')
    rejection_stage = request.GET.get('rejectionStage', '')
    
    queryset = MembershipApplication.objects.filter(status='rejected')
    
    if search:
        queryset = queryset.filter(
            Q(first_name__icontains=search) |
            Q(last_name__icontains=search) |
            Q(email__icontains=search)
        )
    
    if rejection_stage:
        queryset = queryset.filter(rejection_stage=rejection_stage)
    
    paginator = StandardResultsSetPagination()
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
    
    return paginator.get_paginated_response({
        'success': True,
        'data': {
            'applicants': data,
            'pagination': {
                'currentPage': paginator.page.number,
                'totalPages': paginator.page.paginator.num_pages,
                'totalItems': paginator.page.paginator.count
            }
        }
    })


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
    """Get recent activity"""
    limit = int(request.GET.get('limit', 5))
    
    # Get recent applications
    recent_applications = MembershipApplication.objects.all().order_by('-date_applied')[:limit]
    activities = []
    for app in recent_applications:
        status_display = {
            'pending_alumni_verification': ('Pending', 'Alumni Verification'),
            'pending_payment_verification': ('Verified', 'Payment Verification'),
            'approved': ('Approved', 'Member'),
            'rejected': ('Rejected', app.get_rejection_stage_display() if app.rejection_stage else 'Unknown')
        }
    
        status_info = status_display.get(app.status, ('Unknown', 'Unknown'))
        
        activities.append({
            'id': app.id,
            'name': app.full_name,
            'email': app.email,
            'status': status_info[0],
            'type': status_info[1],
            'date': app.date_applied.strftime('%Y-%m-%d')
        })

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
def list_provinces(request):
    """List all provinces"""
    provinces = Province.objects.all()
    serializer = ProvinceSerializer(provinces, many=True)
    return Response({
        'success': True,
        'data': serializer.data
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([AllowAny])
def list_cities(request):
    """List cities by province"""
    province_name = request.GET.get('province')
    
    if province_name:
        cities = City.objects.filter(province__name=province_name)
    else:
        cities = City.objects.all()
    
    serializer = CitySerializer(cities, many=True)
    return Response({
        'success': True,
        'data': serializer.data
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([AllowAny])
def list_barangays(request):
    """List barangays by city"""
    city_name = request.GET.get('city')
    
    if city_name:
        barangays = Barangay.objects.filter(city__name=city_name)
    else:
        barangays = Barangay.objects.all()
    
    serializer = BarangaySerializer(barangays, many=True)
    return Response({
        'success': True,
        'data': serializer.data
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([AllowAny])
def list_degree_programs(request):
    """List all degree programs"""
    programs = DegreeProgram.objects.filter(is_active=True)
    serializer = DegreeProgramSerializer(programs, many=True)
    return Response({
        'success': True,
        'data': serializer.data
    }, status=status.HTTP_200_OK)