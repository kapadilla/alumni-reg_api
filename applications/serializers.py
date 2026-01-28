import logging
from rest_framework import serializers
from .models import MembershipApplication, VerificationHistory

logger = logging.getLogger(__name__)


class VerificationHistorySerializer(serializers.ModelSerializer):
    performedByName = serializers.SerializerMethodField()

    class Meta:
        model = VerificationHistory
        fields = ["id", "action", "performedByName", "notes", "timestamp"]

    def get_performedByName(self, obj):
        return obj.performed_by.get_full_name() if obj.performed_by else "System"


class MembershipApplicationListSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    degreeProgram = serializers.CharField(source="degree_program")
    yearGraduated = serializers.CharField(source="year_graduated")
    studentNumber = serializers.CharField(source="student_number")
    dateApplied = serializers.DateTimeField(source="date_applied")

    class Meta:
        model = MembershipApplication
        fields = [
            "id",
            "name",
            "email",
            "degreeProgram",
            "yearGraduated",
            "studentNumber",
            "status",
            "dateApplied",
        ]

    def get_name(self, obj):
        full_name = f"{obj.first_name} {obj.last_name}"
        if obj.middle_name:
            full_name = f"{obj.first_name} {obj.middle_name} {obj.last_name}"
        if obj.suffix:
            full_name = f"{full_name} {obj.suffix}"
        return full_name


class MembershipApplicationDetailSerializer(serializers.ModelSerializer):
    degreeProgramName = serializers.CharField(source="degree_program", read_only=True)

    personalDetails = serializers.SerializerMethodField()
    academicStatus = serializers.SerializerMethodField()
    professional = serializers.SerializerMethodField()
    mentorship = serializers.SerializerMethodField()
    membership = serializers.SerializerMethodField()

    dateApplied = serializers.DateTimeField(source="date_applied")
    alumniVerifiedAt = serializers.DateTimeField(source="alumni_verified_at")
    approvedAt = serializers.DateTimeField(source="approved_at")
    rejectedAt = serializers.DateTimeField(source="rejected_at")
    rejectionStage = serializers.CharField(source="rejection_stage")
    rejectionReason = serializers.CharField(source="rejection_reason")

    history = VerificationHistorySerializer(
        source="verification_history", many=True, read_only=True
    )

    class Meta:
        model = MembershipApplication
        fields = [
            "id",
            "status",
            "dateApplied",
            "personalDetails",
            "academicStatus",
            "professional",
            "mentorship",
            "membership",
            "degreeProgramName",
            "alumniVerifiedAt",
            "approvedAt",
            "rejectedAt",
            "rejectionStage",
            "rejectionReason",
            "history",
        ]

    def get_personalDetails(self, obj):
        return {
            "firstName": obj.first_name,
            "middleName": obj.middle_name,
            "lastName": obj.last_name,
            "suffix": obj.suffix,
            "maidenName": obj.maiden_name,
            "dateOfBirth": str(obj.date_of_birth),
            "email": obj.email,
            "mobileNumber": obj.mobile_number,
            "currentAddress": obj.current_address,
            "province": obj.province,
            "city": obj.city,
            "barangay": obj.barangay,
            "zipCode": obj.zip_code,
            "idPhoto": obj.id_photo.url if obj.id_photo else None,
        }

    def get_academicStatus(self, obj):
        return {
            "campus": obj.campus,
            "degreeProgram": obj.degree_program,
            "yearGraduated": obj.year_graduated,
            "studentNumber": obj.student_number,
            "torAttachment": obj.tor_attachment.url if obj.tor_attachment else None,
        }

    def get_professional(self, obj):
        return {
            "currentEmployer": obj.current_employer,
            "jobTitle": obj.job_title,
            "industry": obj.industry,
            "yearsOfExperience": obj.years_of_experience,
        }

    def get_mentorship(self, obj):
        return {
            "joinMentorshipProgram": obj.join_mentorship_program,
            "mentorshipAreas": obj.mentorship_areas or [],
            "mentorshipAreasOther": obj.mentorship_areas_other,
            "mentorshipIndustryTracks": obj.mentorship_industry_tracks or [],
            "mentorshipIndustryTracksOther": obj.mentorship_industry_tracks_other,
            "mentorshipFormat": obj.mentorship_format,
            "mentorshipAvailability": obj.mentorship_availability,
        }

    def get_membership(self, obj):
        return {
            "paymentMethod": obj.payment_method,
            "gcashReferenceNumber": obj.gcash_reference_number,
            "gcashProofOfPayment": (
                obj.gcash_proof_of_payment.url if obj.gcash_proof_of_payment else None
            ),
            "bankSenderName": obj.bank_sender_name,
            "bankName": obj.bank_name,
            "bankAccountNumber": obj.bank_account_number,
            "bankReferenceNumber": obj.bank_reference_number,
            "bankProofOfPayment": (
                obj.bank_proof_of_payment.url if obj.bank_proof_of_payment else None
            ),
            "cashPaymentDate": (
                str(obj.cash_payment_date) if obj.cash_payment_date else None
            ),
            "cashReceivedBy": obj.cash_received_by,
            "paymentNotes": obj.payment_notes,
        }


class MembershipApplicationCreateSerializer(serializers.Serializer):
    personalDetails = serializers.JSONField(required=True)
    academicStatus = serializers.JSONField(required=True)
    professional = serializers.JSONField(required=False, allow_null=True)
    membership = serializers.JSONField(required=True)
    mentorship = serializers.JSONField(required=False, allow_null=True)

    # File uploads
    idPhoto = serializers.FileField(required=True)
    torAttachment = serializers.FileField(required=False, allow_null=True)
    gcashProofOfPayment = serializers.FileField(required=False, allow_null=True)
    bankProofOfPayment = serializers.FileField(required=False, allow_null=True)

    def validate(self, data):
        personal = data.get("personalDetails", {})
        academic = data.get("academicStatus", {})
        professional = data.get("professional") or {}
        membership = data.get("membership", {})
        mentorship = data.get("mentorship") or {}

        # Validate personal details
        required_personal_fields = [
            "firstName",
            "lastName",
            "dateOfBirth",
            "email",
            "mobileNumber",
            "currentAddress",
            "province",
            "city",
            "barangay",
            "zipCode",
        ]

        for field in required_personal_fields:
            if field not in personal or not personal[field]:
                raise serializers.ValidationError(
                    {"personalDetails": {field: f"{field} is required"}}
                )

        # Validate email
        email = personal.get("email")
        if email:
            # Generic error message for security (prevents email enumeration)
            generic_email_error = "We were unable to process your registration. If you believe this is an error, please contact support."

            if email.endswith("@up.edu.ph"):
                logger.info(
                    f"Registration rejected: Email {email} uses @up.edu.ph domain"
                )
                raise serializers.ValidationError(
                    {"personalDetails": {"email": generic_email_error}}
                )

            # Check for existing applications (exclude rejected - they can reapply)
            existing_app = (
                MembershipApplication.objects.filter(email=email)
                .exclude(status="rejected")
                .first()
            )
            if existing_app:
                if existing_app.status == "revoked":
                    logger.info(
                        f"Registration rejected: Email {email} belongs to revoked membership (app_id={existing_app.id})"
                    )
                else:
                    logger.info(
                        f"Registration rejected: Email {email} already registered with status={existing_app.status} (app_id={existing_app.id})"
                    )
                raise serializers.ValidationError(
                    {"personalDetails": {"email": generic_email_error}}
                )

        # Validate academic status
        if "degreeProgram" not in academic or not academic["degreeProgram"]:
            raise serializers.ValidationError(
                {"academicStatus": {"degreeProgram": "Degree Program is required"}}
            )

        if "campus" not in academic or not academic["campus"]:
            raise serializers.ValidationError(
                {"academicStatus": {"campus": "Campus is required"}}
            )

        # Validate idPhoto is provided
        if "idPhoto" not in data or data["idPhoto"] is None:
            raise serializers.ValidationError(
                {"idPhoto": "1x1 ID Photo is required"}
            )

        # Validate yearGraduated and torAttachment
        year_graduated = academic.get("yearGraduated")
        if not year_graduated:
            # If yearGraduated is empty/blank, torAttachment is required
            if "torAttachment" not in data or data["torAttachment"] is None:
                raise serializers.ValidationError(
                    {"torAttachment": "Transcript of Records is required when not graduated yet"}
                )

        # Note: yearGraduated is optional per form specification

        # Validate membership
        if "paymentMethod" not in membership or not membership["paymentMethod"]:
            raise serializers.ValidationError(
                {"membership": {"paymentMethod": "Payment Method is required"}}
            )

        # Validate payment method choice
        valid_payment_methods = ["gcash", "bank", "cash"]
        payment_method = membership["paymentMethod"]
        if payment_method not in valid_payment_methods:
            raise serializers.ValidationError(
                {
                    "membership": {
                        "paymentMethod": f'Must be one of: {", ".join(valid_payment_methods)}'
                    }
                }
            )

        # Validate payment method specific fields
        if payment_method == "gcash":
            if (
                "gcashReferenceNumber" not in membership
                or not membership["gcashReferenceNumber"]
            ):
                raise serializers.ValidationError(
                    {
                        "membership": {
                            "gcashReferenceNumber": "GCash reference number is required"
                        }
                    }
                )
            if "gcashProofOfPayment" not in data or data["gcashProofOfPayment"] is None:
                raise serializers.ValidationError(
                    {"gcashProofOfPayment": "Proof of payment is required for GCash"}
                )

        elif payment_method == "bank":
            required_bank_fields = [
                "bankSenderName",
                "bankName",
                "bankAccountNumber",
                "bankReferenceNumber",
            ]
            for field in required_bank_fields:
                if field not in membership or not membership[field]:
                    raise serializers.ValidationError(
                        {
                            "membership": {
                                field: f"{field} is required for bank transfer"
                            }
                        }
                    )
            if "bankProofOfPayment" not in data or data["bankProofOfPayment"] is None:
                raise serializers.ValidationError(
                    {
                        "bankProofOfPayment": "Proof of payment is required for bank transfer"
                    }
                )

        elif payment_method == "cash":
            required_cash_fields = ["cashPaymentDate", "cashReceivedBy"]
            for field in required_cash_fields:
                if field not in membership or not membership[field]:
                    raise serializers.ValidationError(
                        {"membership": {field: f"{field} is required for cash payment"}}
                    )

        # Note: data privacy consent field removed from model; frontend should enforce consent

        # Validate mentorship if opted in
        if mentorship.get("joinMentorshipProgram", False):
            if "mentorshipAreas" not in mentorship or not mentorship["mentorshipAreas"]:
                raise serializers.ValidationError(
                    {"mentorship": {"mentorshipAreas": "Mentorship areas are required"}}
                )
            if (
                "mentorshipIndustryTracks" not in mentorship
                or not mentorship["mentorshipIndustryTracks"]
            ):
                raise serializers.ValidationError(
                    {
                        "mentorship": {
                            "mentorshipIndustryTracks": "Mentorship industry tracks are required"
                        }
                    }
                )
            if (
                "mentorshipFormat" not in mentorship
                or not mentorship["mentorshipFormat"]
            ):
                raise serializers.ValidationError(
                    {
                        "mentorship": {
                            "mentorshipFormat": "Mentorship format is required"
                        }
                    }
                )
            if (
                "mentorshipAvailability" not in mentorship
                or not mentorship["mentorshipAvailability"]
            ):
                raise serializers.ValidationError(
                    {
                        "mentorship": {
                            "mentorshipAvailability": "Mentorship availability is required"
                        }
                    }
                )

        return {
            "personal_details": personal,
            "academic_status": academic,
            "professional": professional,
            "membership": membership,
            "mentorship": mentorship,
            "files": {
                "id_photo": data.get("idPhoto"),
                "tor_attachment": data.get("torAttachment"),
                "gcash_proof": data.get("gcashProofOfPayment"),
                "bank_proof": data.get("bankProofOfPayment"),
            },
        }

    def create(self, validated_data):
        personal = validated_data["personal_details"]
        academic = validated_data["academic_status"]
        professional = validated_data.get("professional", {})
        membership = validated_data["membership"]
        mentorship = validated_data.get("mentorship", {})
        files = validated_data.get("files", {})

        payment_method = membership["paymentMethod"]

        # Helper to convert empty strings to None
        def empty_to_none(value):
            return None if value == "" else value

        # Create application
        application = MembershipApplication.objects.create(
            # Personal details
            first_name=personal["firstName"],
            middle_name=empty_to_none(personal.get("middleName")),
            last_name=personal["lastName"],
            suffix=empty_to_none(personal.get("suffix")),
            maiden_name=empty_to_none(personal.get("maidenName")),
            date_of_birth=personal["dateOfBirth"],
            id_photo=files.get("id_photo"),
            email=personal["email"],
            mobile_number=personal["mobileNumber"],
            current_address=personal["currentAddress"],
            province=personal["province"],
            city=personal["city"],
            barangay=personal["barangay"],
            zip_code=empty_to_none(personal.get("zipCode")),
            # Academic status
            degree_program=academic["degreeProgram"],
            campus=empty_to_none(academic.get("campus")),
            year_graduated=academic["yearGraduated"],
            student_number=empty_to_none(academic.get("studentNumber")),
            tor_attachment=files.get("tor_attachment"),
            # Professional
            current_employer=empty_to_none(professional.get("currentEmployer")),
            job_title=empty_to_none(professional.get("jobTitle")),
            industry=empty_to_none(professional.get("industry")),
            years_of_experience=empty_to_none(professional.get("yearsOfExperience")),
            # Membership & Payment
            payment_method=payment_method,
            # Payment method specific details
            gcash_reference_number=empty_to_none(
                membership.get("gcashReferenceNumber")
            ),
            gcash_proof_of_payment=files.get("gcash_proof"),
            bank_name=empty_to_none(membership.get("bankName")),
            bank_account_number=empty_to_none(membership.get("bankAccountNumber")),
            bank_reference_number=empty_to_none(membership.get("bankReferenceNumber")),
            bank_sender_name=empty_to_none(membership.get("bankSenderName")),
            bank_proof_of_payment=files.get("bank_proof"),
            cash_payment_date=empty_to_none(membership.get("cashPaymentDate")),
            cash_received_by=empty_to_none(membership.get("cashReceivedBy")),
            payment_notes=empty_to_none(membership.get("paymentNotes")),
            # Mentorship program
            join_mentorship_program=mentorship.get("joinMentorshipProgram", False),
            mentorship_areas=mentorship.get("mentorshipAreas", []),
            mentorship_areas_other=empty_to_none(
                mentorship.get("mentorshipAreasOther")
            ),
            mentorship_availability=empty_to_none(
                mentorship.get("mentorshipAvailability")
            ),
            mentorship_format=empty_to_none(mentorship.get("mentorshipFormat")),
            mentorship_industry_tracks=mentorship.get("mentorshipIndustryTracks", []),
            mentorship_industry_tracks_other=empty_to_none(
                mentorship.get("mentorshipIndustryTracksOther")
            ),
        )

        # Create history entry
        VerificationHistory.objects.create(
            application=application, action="submitted", notes="Application submitted"
        )

        return application


class VerifyAlumniSerializer(serializers.Serializer):
    notes = serializers.CharField(required=False, allow_blank=True)


class RejectApplicationSerializer(serializers.Serializer):
    reason = serializers.CharField(required=True)
