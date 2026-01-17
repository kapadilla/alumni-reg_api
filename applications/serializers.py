from rest_framework import serializers
from .models import (
    MembershipApplication, DegreeProgram, VerificationHistory
)


class DegreeProgramSerializer(serializers.ModelSerializer):
    class Meta:
        model = DegreeProgram
        fields = ['id', 'name', 'college']


class VerificationHistorySerializer(serializers.ModelSerializer):
    performedByName = serializers.SerializerMethodField()
    
    class Meta:
        model = VerificationHistory
        fields = ['id', 'action', 'performedByName', 'notes', 'timestamp']
    
    def get_performedByName(self, obj):
        return obj.performed_by.get_full_name() if obj.performed_by else 'System'


class MembershipApplicationListSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    degreeProgram = serializers.CharField(source='degree_program.name')
    yearGraduated = serializers.CharField(source='year_graduated')
    studentNumber = serializers.CharField(source='student_number')
    dateApplied = serializers.DateTimeField(source='date_applied')
    
    class Meta:
        model = MembershipApplication
        fields = [
            'id', 'name', 'email', 'degreeProgram', 'yearGraduated',
            'studentNumber', 'status', 'dateApplied'
        ]
    
    def get_name(self, obj):
        return obj.full_name


class MembershipApplicationDetailSerializer(serializers.ModelSerializer):
    degreeProgramName = serializers.CharField(source='degree_program.name', read_only=True)
    
    personalDetails = serializers.SerializerMethodField()
    academicStatus = serializers.SerializerMethodField()
    professional = serializers.SerializerMethodField()
    membership = serializers.SerializerMethodField()
    
    dateApplied = serializers.DateTimeField(source='date_applied')
    alumniVerifiedAt = serializers.DateTimeField(source='alumni_verified_at')
    approvedAt = serializers.DateTimeField(source='approved_at')
    rejectedAt = serializers.DateTimeField(source='rejected_at')
    rejectionStage = serializers.CharField(source='rejection_stage')
    rejectionReason = serializers.CharField(source='rejection_reason')
    adminNotes = serializers.CharField(source='admin_notes')
    
    class Meta:
        model = MembershipApplication
        fields = [
            'id', 'status', 'dateApplied',
            'personalDetails', 'academicStatus', 'professional', 'membership',
            'degreeProgramName',
            'alumniVerifiedAt', 'approvedAt', 'rejectedAt',
            'rejectionStage', 'rejectionReason', 'adminNotes', 'history'
        ]
    
    history = VerificationHistorySerializer(many=True, read_only=True)
    
    def get_personalDetails(self, obj):
        return {
            'title': obj.title,
            'firstName': obj.first_name,
            'lastName': obj.last_name,
            'suffix': obj.suffix,
            'maidenName': obj.maiden_name,
            'dateOfBirth': str(obj.date_of_birth),
            'email': obj.email,
            'mobileNumber': obj.mobile_number,
            'currentAddress': obj.current_address,
            'province': obj.province,
            'city': obj.city,
            'barangay': obj.barangay,
        }
    
    def get_academicStatus(self, obj):
        return {
            'degreeProgram': obj.degree_program.name,
            'yearGraduated': obj.year_graduated,
            'studentNumber': obj.student_number,
        }
    
    def get_professional(self, obj):
        return {
            'currentEmployer': obj.current_employer,
            'jobTitle': obj.job_title,
            'industry': obj.industry,
        }
    
    def get_membership(self, obj):
        return {
            'paymentMethod': obj.payment_method,
        }


class MembershipApplicationCreateSerializer(serializers.Serializer):
    personalDetails = serializers.JSONField(required=False, allow_null=True)
    academicStatus = serializers.JSONField(required=False, allow_null=True)
    professional = serializers.JSONField(required=False, allow_null=True)
    membership = serializers.JSONField(required=False, allow_null=True)
    mentorship = serializers.JSONField(required=False, allow_null=True)
    
    # File uploads
    gcashProofOfPayment = serializers.FileField(required=False, allow_null=True)
    bankProofOfPayment = serializers.FileField(required=False, allow_null=True)
    
    def validate(self, data):
        # Parse JSON strings from FormData (they come as strings, not dicts)
        personal = data.get('personalDetails')
        academic = data.get('academicStatus')
        professional = data.get('professional') or {}
        membership = data.get('membership')
        mentorship = data.get('mentorship') or {}
        
        if not personal:
            raise serializers.ValidationError({
                'personalDetails': 'This field is required'
            })
        
        if not academic:
            raise serializers.ValidationError({
                'academicStatus': 'This field is required'
            })
        
        if not membership:
            raise serializers.ValidationError({
                'membership': 'This field is required'
            })
        
        # Validate personal details fields
        required_personal_fields = {
            'title': 'Title',
            'firstName': 'First Name',
            'lastName': 'Last Name',
            'dateOfBirth': 'Date of Birth',
            'email': 'Email',
            'mobileNumber': 'Mobile Number',
            'currentAddress': 'Current Address',
            'province': 'Province',
            'city': 'City',
            'barangay': 'Barangay'
        }
        
        for field, label in required_personal_fields.items():
            if field not in personal:
                raise serializers.ValidationError({
                    'personalDetails': {field: f'{label} is required'}
                })
        
        # Validate email
        email = personal.get('email')
        if email:
            if email.endswith('@up.edu.ph'):
                raise serializers.ValidationError({
                    'personalDetails': {'email': 'Email must not end with @up.edu.ph'}
                })
            
            if MembershipApplication.objects.filter(email=email).exists():
                raise serializers.ValidationError({
                    'personalDetails': {'email': 'Email already registered'}
                })
        
        # Validate academic status
        if 'degreeProgram' not in academic:
            raise serializers.ValidationError({
                'academicStatus': {'degreeProgram': 'Degree Program is required'}
            })
        
        if 'yearGraduated' not in academic:
            raise serializers.ValidationError({
                'academicStatus': {'yearGraduated': 'Year Graduated is required'}
            })
        
        # Validate membership
        if 'paymentMethod' not in membership:
            raise serializers.ValidationError({
                'membership': {'paymentMethod': 'Payment Method is required'}
            })
        
        # Validate payment method choice
        valid_payment_methods = ['gcash', 'bank', 'cash']
        payment_method = membership['paymentMethod']
        if payment_method not in valid_payment_methods:
            raise serializers.ValidationError({
                'membership': {'paymentMethod': f'Must be one of: {", ".join(valid_payment_methods)}'}
            })
        
        # Validate payment method specific fields
        if payment_method == 'gcash':
            if 'gcashReferenceNumber' not in membership:
                raise serializers.ValidationError({
                    'membership': {'gcashReferenceNumber': 'GCash reference number is required'}
                })
            if 'gcashProofOfPayment' not in data or data['gcashProofOfPayment'] is None:
                raise serializers.ValidationError({
                    'gcashProofOfPayment': 'Proof of payment is required for GCash'
                })
        
        elif payment_method == 'bank':
            required_bank_fields = ['bankName', 'bankAccountNumber', 'bankReferenceNumber', 'bankSenderName']
            for field in required_bank_fields:
                if field not in membership or not membership[field]:
                    raise serializers.ValidationError({
                        'membership': {field: f'{field} is required for bank transfer'}
                    })
            if 'bankProofOfPayment' not in data or data['bankProofOfPayment'] is None:
                raise serializers.ValidationError({
                    'bankProofOfPayment': 'Proof of payment is required for bank transfer'
                })
        
        elif payment_method == 'cash':
            required_cash_fields = ['cashPaymentDate', 'cashReceivedBy']
            for field in required_cash_fields:
                if field not in membership or not membership[field]:
                    raise serializers.ValidationError({
                        'membership': {field: f'{field} is required for cash payment'}
                    })
        
        # Validate data privacy consent
        if 'dataPrivacyConsent' not in membership or not membership['dataPrivacyConsent']:
            raise serializers.ValidationError({
                'membership': {'dataPrivacyConsent': 'You must consent to data privacy terms'}
            })
        
        return {
            'personal_details': personal,
            'academic_status': academic,
            'professional': professional,
            'membership': membership,
            'mentorship': mentorship,
            'files': {
                'gcash_proof': data.get('gcashProofOfPayment'),
                'bank_proof': data.get('bankProofOfPayment'),
            }
        }
    
    def create(self, validated_data):
        personal = validated_data['personal_details']
        academic = validated_data['academic_status']
        professional = validated_data.get('professional', {})
        membership = validated_data['membership']
        mentorship = validated_data.get('mentorship', {})
        files = validated_data.get('files', {})
        
        try:
            degree_program = DegreeProgram.objects.get(name=academic['degreeProgram'])
        except DegreeProgram.DoesNotExist:
            raise serializers.ValidationError({'academicStatus': {'degreeProgram': 'Invalid degree program'}})
        
        payment_method = membership['paymentMethod']
        
        # Helper to convert empty strings to None
        def empty_to_none(value):
            return None if value == '' else value
        
        # Create application
        application = MembershipApplication.objects.create(
            # Personal details
            title=personal['title'],
            first_name=personal['firstName'],
            last_name=personal['lastName'],
            suffix=empty_to_none(personal.get('suffix')),
            maiden_name=empty_to_none(personal.get('maidenName')),
            date_of_birth=personal['dateOfBirth'],
            email=personal['email'],
            mobile_number=personal['mobileNumber'],
            current_address=personal['currentAddress'],
            province=personal['province'],
            city=personal['city'],
            barangay=personal['barangay'],
            
            # Academic status
            degree_program=degree_program,
            year_graduated=academic['yearGraduated'],
            student_number=empty_to_none(academic.get('studentNumber')),
            
            # Professional
            current_employer=empty_to_none(professional.get('currentEmployer')),
            job_title=empty_to_none(professional.get('jobTitle')),
            industry=empty_to_none(professional.get('industry')),
            
            # Membership & Payment
            payment_method=payment_method,
            data_privacy_consent=membership.get('dataPrivacyConsent', False),
            
            # Payment method specific details
            gcash_reference_number=empty_to_none(membership.get('gcashReferenceNumber')),
            gcash_proof_of_payment=files.get('gcash_proof'),
            
            bank_name=empty_to_none(membership.get('bankName')),
            bank_account_number=empty_to_none(membership.get('bankAccountNumber')),
            bank_reference_number=empty_to_none(membership.get('bankReferenceNumber')),
            bank_sender_name=empty_to_none(membership.get('bankSenderName')),
            bank_proof_of_payment=files.get('bank_proof'),
            
            cash_payment_date=empty_to_none(membership.get('cashPaymentDate')),
            cash_received_by=empty_to_none(membership.get('cashReceivedBy')),
            
            # Mentorship program
            join_mentorship_program=mentorship.get('joinMentorshipProgram', False),
            mentorship_areas=mentorship.get('mentorshipAreas', []),
            mentorship_areas_other=empty_to_none(mentorship.get('mentorshipAreasOther')),
            mentorship_availability=empty_to_none(mentorship.get('mentorshipAvailability')),
            mentorship_format=empty_to_none(mentorship.get('mentorshipFormat')),
            mentorship_industry_tracks=mentorship.get('mentorshipIndustryTracks', []),
            mentorship_industry_tracks_other=empty_to_none(mentorship.get('mentorshipIndustryTracksOther')),
            years_of_experience=empty_to_none(personal.get('yearsOfExperience')),
        )
        
        # Create history entry
        VerificationHistory.objects.create(
            application=application,
            action='submitted',
            notes='Application submitted'
        )
        
        return application


class VerifyAlumniSerializer(serializers.Serializer):
    notes = serializers.CharField(required=False, allow_blank=True)


class RejectApplicationSerializer(serializers.Serializer):
    reason = serializers.CharField(required=True)