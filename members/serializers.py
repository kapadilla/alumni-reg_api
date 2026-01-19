from rest_framework import serializers
from .models import Member
from applications.serializers import VerificationHistorySerializer


class MemberListSerializer(serializers.ModelSerializer):
    degreeProgram = serializers.CharField(source='application.degree_program')
    yearGraduated = serializers.CharField(source='application.year_graduated')
    
    class Meta:
        model = Member
        fields = ['id', 'full_name', 'email', 'degreeProgram', 'yearGraduated', 'member_since', 'is_active']


class MemberDetailSerializer(serializers.ModelSerializer):
    personalDetails = serializers.SerializerMethodField()
    academicStatus = serializers.SerializerMethodField()
    professional = serializers.SerializerMethodField()
    membership = serializers.SerializerMethodField()
    history = serializers.SerializerMethodField()
    
    class Meta:
        model = Member
        fields = ['id', 'member_since', 'is_active', 'personalDetails', 'academicStatus', 'professional', 'membership', 'history']
    
    def get_personalDetails(self, obj):
        app = obj.application
        return {
            'title': app.title,
            'firstName': app.first_name,
            'lastName': app.last_name,
            'suffix': app.suffix,
            'email': app.email,
            'mobileNumber': app.mobile_number,
            'dateOfBirth': str(app.date_of_birth) if app.date_of_birth else None,
            'currentAddress': app.current_address,
            'province': app.province,
            'city': app.city,
            'barangay': app.barangay,
        }
    
    def get_academicStatus(self, obj):
        app = obj.application
        return {
            'degreeProgram': app.degree_program,
            'campus': app.campus,
            'yearGraduated': app.year_graduated,
            'studentNumber': app.student_number,
        }
    
    def get_professional(self, obj):
        app = obj.application
        return {
            'currentEmployer': app.current_employer,
            'jobTitle': app.job_title,
            'industry': app.industry,
        }
    
    def get_membership(self, obj):
        app = obj.application
        return {
            'paymentMethod': app.payment_method,
        }
    
    def get_history(self, obj):
        history_entries = obj.application.history.all().order_by('-timestamp')
        return VerificationHistorySerializer(history_entries, many=True).data