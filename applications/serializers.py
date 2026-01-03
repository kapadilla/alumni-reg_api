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
    provinceName = serializers.CharField(source='province.name', read_only=True)
    
    class Meta:
        model = City
        fields = ['id', 'name', 'provinceName']


class BarangaySerializer(serializers.ModelSerializer):
    cityName = serializers.CharField(source='city.name', read_only=True)
    
    class Meta:
        model = Barangay
        fields = ['id', 'name', 'cityName']


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
    degree = serializers.CharField(source='degree_program.name')
    yearGraduated = serializers.CharField(source='year_graduated')
    studentNumber = serializers.CharField(source='student_number')
    dateApplied = serializers.DateTimeField(source='date_applied')
    
    class Meta:
        model = MembershipApplication
        fields = [
            'id', 'name', 'email', 'degree', 'yearGraduated',
            'studentNumber', 'status', 'dateApplied'
        ]
    
    def get_name(self, obj):
        return obj.full_name


class MembershipApplicationDetailSerializer(serializers.ModelSerializer):
    provinceName = serializers.CharField(source='province.name', read_only=True)
    cityName = serializers.CharField(source='city.name', read_only=True)
    barangayName = serializers.CharField(source='barangay.name', read_only=True)
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
            'provinceName', 'cityName', 'barangayName', 'degreeProgramName',
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
            'province': obj.province.name,
            'city': obj.city.name,
            'barangay': obj.barangay.name,
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
    personalDetails = serializers.DictField(required=False) 
    academicStatus = serializers.DictField(required=False)
    
    professional = serializers.DictField(required=False)
    membership = serializers.DictField(required=False)
    
    def validate(self, data):
        # Handle both naming conventions (prefer camelCase)
        personal = data.get('personalDetails') or data.get('personal_details')
        academic = data.get('academicStatus') or data.get('academic_status')
        professional = data.get('professional', {})
        membership = data.get('membership')
        
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
        if membership['paymentMethod'] not in valid_payment_methods:
            raise serializers.ValidationError({
                'membership': {'paymentMethod': f'Must be one of: {", ".join(valid_payment_methods)}'}
            })
        
        return {
            'personal_details': personal,
            'academic_status': academic,
            'professional': professional,
            'membership': membership
        }
    
    def create(self, validated_data):
        personal = validated_data['personal_details']
        academic = validated_data['academic_status']
        professional = validated_data.get('professional', {})
        membership = validated_data['membership']
        
        try:
            # Get related objects by name
            province = Province.objects.get(name=personal['province'])
            city = City.objects.get(name=personal['city'], province=province)
            barangay = Barangay.objects.get(name=personal['barangay'], city=city)
            degree_program = DegreeProgram.objects.get(name=academic['degreeProgram'])
        except Province.DoesNotExist:
            raise serializers.ValidationError({'personalDetails': {'province': 'Invalid province'}})
        except City.DoesNotExist:
            raise serializers.ValidationError({'personalDetails': {'city': 'Invalid city'}})
        except Barangay.DoesNotExist:
            raise serializers.ValidationError({'personalDetails': {'barangay': 'Invalid barangay'}})
        except DegreeProgram.DoesNotExist:
            raise serializers.ValidationError({'academicStatus': {'degreeProgram': 'Invalid degree program'}})
        
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