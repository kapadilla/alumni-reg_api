from rest_framework import serializers
from .models import Member
from applications.serializers import VerificationHistorySerializer


class MemberListSerializer(serializers.ModelSerializer):
    degreeProgram = serializers.CharField(source="application.degree_program")
    yearGraduated = serializers.CharField(source="application.year_graduated")

    class Meta:
        model = Member
        fields = [
            "id",
            "full_name",
            "email",
            "degreeProgram",
            "yearGraduated",
            "member_since",
            "is_active",
        ]


class MemberDetailSerializer(serializers.ModelSerializer):
    personalDetails = serializers.SerializerMethodField()
    academicStatus = serializers.SerializerMethodField()
    professional = serializers.SerializerMethodField()
    mentorship = serializers.SerializerMethodField()
    membership = serializers.SerializerMethodField()
    history = serializers.SerializerMethodField()

    class Meta:
        model = Member
        fields = [
            "id",
            "member_since",
            "is_active",
            "personalDetails",
            "academicStatus",
            "professional",
            "mentorship",
            "membership",
            "history",
        ]

    def get_personalDetails(self, obj):
        app = obj.application
        return {
            "firstName": app.first_name,
            "middleName": app.middle_name,
            "lastName": app.last_name,
            "suffix": app.suffix,
            "maidenName": app.maiden_name,
            "email": app.email,
            "mobileNumber": app.mobile_number,
            "dateOfBirth": str(app.date_of_birth) if app.date_of_birth else None,
            "currentAddress": app.current_address,
            "province": app.province,
            "city": app.city,
            "barangay": app.barangay,
            "zipCode": app.zip_code,
        }

    def get_academicStatus(self, obj):
        app = obj.application
        return {
            "degreeProgram": app.degree_program,
            "campus": app.campus,
            "yearGraduated": app.year_graduated,
            "studentNumber": app.student_number,
        }

    def get_professional(self, obj):
        app = obj.application
        return {
            "currentEmployer": app.current_employer,
            "jobTitle": app.job_title,
            "industry": app.industry,
            "yearsOfExperience": app.years_of_experience,
        }

    def get_mentorship(self, obj):
        app = obj.application
        return {
            "joinMentorshipProgram": app.join_mentorship_program,
            "mentorshipAreas": app.mentorship_areas or [],
            "mentorshipAreasOther": app.mentorship_areas_other,
            "mentorshipIndustryTracks": app.mentorship_industry_tracks or [],
            "mentorshipIndustryTracksOther": app.mentorship_industry_tracks_other,
            "mentorshipFormat": app.mentorship_format,
            "mentorshipAvailability": app.mentorship_availability,
        }

    def get_membership(self, obj):
        app = obj.application
        return {
            "paymentMethod": app.payment_method,
            "gcashReferenceNumber": app.gcash_reference_number,
            "gcashProofOfPayment": (
                app.gcash_proof_of_payment.url if app.gcash_proof_of_payment else None
            ),
            "bankSenderName": app.bank_sender_name,
            "bankName": app.bank_name,
            "bankAccountNumber": app.bank_account_number,
            "bankReferenceNumber": app.bank_reference_number,
            "bankProofOfPayment": (
                app.bank_proof_of_payment.url if app.bank_proof_of_payment else None
            ),
            "cashPaymentDate": (
                str(app.cash_payment_date) if app.cash_payment_date else None
            ),
            "cashReceivedBy": app.cash_received_by,
            "paymentNotes": app.payment_notes,
        }

    def get_history(self, obj):
        history_entries = obj.application.verification_history.all().order_by(
            "-timestamp"
        )
        return VerificationHistorySerializer(history_entries, many=True).data
