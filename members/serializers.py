from rest_framework import serializers
from .models import Member


class MemberListSerializer(serializers.ModelSerializer):
    degree = serializers.CharField(source='application.degree_program.name')
    year_graduated = serializers.CharField(source='application.year_graduated')
    
    class Meta:
        model = Member
        fields = ['id', 'full_name', 'email', 'degree', 'year_graduated', 'member_since', 'is_active']


class MemberDetailSerializer(serializers.ModelSerializer):
    application_details = serializers.SerializerMethodField()
    
    class Meta:
        model = Member
        fields = ['id', 'full_name', 'email', 'member_since', 'is_active', 'application_details']
    
    def get_application_details(self, obj):
        app = obj.application
        return {
            'personalDetails': {
                'title': app.title,
                'firstName': app.first_name,
                'lastName': app.last_name,
                'suffix': app.suffix,
                'dateOfBirth': app.date_of_birth,
                'mobileNumber': app.mobile_number,
                'currentAddress': app.current_address,
            },
            'academicStatus': {
                'degreeProgram': app.degree_program.name,
                'yearGraduated': app.year_graduated,
                'studentNumber': app.student_number,
            },
            'professional': {
                'currentEmployer': app.current_employer,
                'jobTitle': app.job_title,
                'industry': app.industry,
            }
        }