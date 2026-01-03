from rest_framework import serializers
from .models import (
    MembershipApplication, Province, City, Barangay,
    DegreeProgram, VerificationHistory
)


class ProvinceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Province
        fields = ['id', 'name']


class CitySerializer(serializers.ModelSerializer):
    province_name = serializers.CharField(source='province.name', read_only=True)
    
    class Meta:
        model = City
        fields = ['id', 'name', 'province_name']


class BarangaySerializer(serializers.ModelSerializer):
    city_name = serializers.CharField(source='city.name', read_only=True)
    
    class Meta:
        model = Barangay
        fields = ['id', 'name', 'city_name']


class DegreeProgramSerializer(serializers.ModelSerializer):
    class Meta:
        model = DegreeProgram
        fields = ['id', 'name', 'college']


class VerificationHistorySerializer(serializers.ModelSerializer):
    performed_by_name = serializers.SerializerMethodField()
    
    class Meta:
        model = VerificationHistory
        fields = ['id', 'action', 'performed_by_name', 'notes', 'timestamp']
    
    def get_performed_by_name(self, obj):
        return obj.performed_by.get_full_name() if obj.performed_by else 'System'


class MembershipApplicationListSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    degree = serializers.CharField(source='degree_program.name')
    
    class Meta:
        model = MembershipApplication
        fields = [
            'id', 'name', 'email', 'degree', 'year_graduated',
            'student_number', 'status', 'date_applied'
        ]
    
    def get_name(self, obj):
        return obj.full_name


class MembershipApplicationDetailSerializer(serializers.ModelSerializer):
    province_name = serializers.CharField(source='province.name', read_only=True)
    city_name = serializers.CharField(source='city.name', read_only=True)
    barangay_name = serializers.CharField(source='barangay.name', read_only=True)
    degree_program_name = serializers.CharField(source='degree_program.name', read_only=True)
    history = VerificationHistorySerializer(many=True, read_only=True)
    
    personal_details = serializers.SerializerMethodField()
    academic_status = serializers.SerializerMethodField()
    professional = serializers.SerializerMethodField()
    membership = serializers.SerializerMethodField()
    
    class Meta:
        model = MembershipApplication
        fields = [
            'id', 'status', 'date_applied',
            'personal_details', 'academic_status', 'professional', 'membership',
            'province_name', 'city_name', 'barangay_name', 'degree_program_name',
            'alumni_verified_at', 'approved_at', 'rejected_at',
            'rejection_stage', 'rejection_reason', 'admin_notes', 'history'
        ]
    
    def get_personal_details(self, obj):
        return {
            'title': obj.title,
            'firstName': obj.first_name,
            'lastName': obj.last_name,
            'suffix': obj.suffix,
            'maidenName': obj.maiden_name,
            'dateOfBirth': obj.date_of_birth,
            'email': obj.email,
            'mobileNumber': obj.mobile_number,
            'currentAddress': obj.current_address,
            'province': obj.province.name,
            'city': obj.city.name,
            'barangay': obj.barangay.name,
        }
    
    def get_academic_status(self, obj):
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
    personal_details = serializers.DictField()
    academic_status = serializers.DictField()
    professional = serializers.DictField(required=False)
    membership = serializers.DictField()
    
    def validate_personal_details(self, value):
        required_fields = [
            'title', 'firstName', 'lastName', 'dateOfBirth',
            'email', 'mobileNumber', 'currentAddress',
            'province', 'city', 'barangay'
        ]
        
        for field in required_fields:
            if field not in value:
                raise serializers.ValidationError(f"{field} is required")
        
        # Validate email
        email = value.get('email')
        if email and email.endswith('@up.edu.ph'):
            raise serializers.ValidationError("Email must not end with @up.edu.ph")
        
        # Check if email already exists
        if MembershipApplication.objects.filter(email=email).exists():
            raise serializers.ValidationError("Email already registered")
        
        return value
    
    def validate_academic_status(self, value):
        required_fields = ['degreeProgram', 'yearGraduated']
        
        for field in required_fields:
            if field not in value:
                raise serializers.ValidationError(f"{field} is required")
        
        return value
    
    def validate_membership(self, value):
        if 'paymentMethod' not in value:
            raise serializers.ValidationError("paymentMethod is required")
        
        return value
    
    def create(self, validated_data):
        personal = validated_data['personal_details']
        academic = validated_data['academic_status']
        professional = validated_data.get('professional', {})
        membership = validated_data['membership']
        
        # Get related objects by name
        province = Province.objects.get(name=personal['province'])
        city = City.objects.get(name=personal['city'], province=province)
        barangay = Barangay.objects.get(name=personal['barangay'], city=city)
        degree_program = DegreeProgram.objects.get(name=academic['degreeProgram'])
        
        # Create application
        application = MembershipApplication.objects.create(
            # Personal details
            title=personal['title'],
            first_name=personal['firstName'],
            last_name=personal['lastName'],
            suffix=personal.get('suffix'),
            maiden_name=personal.get('maidenName'),
            date_of_birth=personal['dateOfBirth'],
            email=personal['email'],
            mobile_number=personal['mobileNumber'],
            current_address=personal['currentAddress'],
            province=province,
            city=city,
            barangay=barangay,
            
            # Academic status
            degree_program=degree_program,
            year_graduated=academic['yearGraduated'],
            student_number=academic.get('studentNumber'),
            
            # Professional
            current_employer=professional.get('currentEmployer'),
            job_title=professional.get('jobTitle'),
            industry=professional.get('industry'),
            
            # Membership
            payment_method=membership['paymentMethod'],
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