import random
from datetime import timedelta
from django.utils import timezone
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from applications.models import (
    MembershipApplication, DegreeProgram, VerificationHistory
)
from members.models import Member

class Command(BaseCommand):
    help = 'Seeds the database with mock data for testing (NOT FOR PRODUCTION)'

    def handle(self, *args, **kwargs):
        self.stdout.write('Starting mock data generation...')
        
        # Ensure reference data exists
        if not DegreeProgram.objects.exists():
            self.stdout.write(self.style.WARNING('No degree programs found. Please run "python manage.py seed_data" first.'))
            return

        # Create Admin/Staff users for history tracking
        admin_user, _ = User.objects.get_or_create(username='admin_mock', defaults={'email': 'admin_mock@example.com', 'is_staff': True})
        staff_user, _ = User.objects.get_or_create(username='staff_mock', defaults={'email': 'staff_mock@example.com', 'is_staff': True})
        
        # Sample Data Pools
        first_names = ['Juan', 'Maria', 'Jose', 'Ana', 'Pedro', 'Sofia', 'Miguel', 'Isabella', 'Ramon', 'Carmen', 'Luis', 'Elena', 'Antonio', 'Patricia', 'Carlo']
        last_names = ['Dela Cruz', 'Santos', 'Reyes', 'Garcia', 'Bautista', 'Ocampo', 'Gonzales', 'Lopez', 'Tan', 'Lim', 'Yap', 'Sy', 'Castillo', 'Villanueva']
        addresses = ['123 Main St', '456 Rizal Ave', '789 Mabini St', 'Block 1 Lot 2', 'Unit 101 Condo', 'Village East', 'Poblacion']
        employers = ['Acme Corp', 'Tech Solutions', 'Global Ventures', 'Freelance', 'DepEd', 'Gov Office', 'StartUp Inc', 'BPO Prime']
        job_titles = ['Software Engineer', 'Accountant', 'Teacher', 'Manager', 'Analyst', 'Clerk', 'Supervisor', 'Consultant']
        provinces = ['Cebu', 'Metro Manila', 'Davao', 'Laguna', 'Pampanga']
        cities = ['Cebu City', 'Manila', 'Quezon City', 'Davao City', 'Makati']
        barangays = ['Lahug', 'Kamputhaw', 'Guadalupe', 'Banilad', 'Talamban', 'Poblacion']
        
        # Fetch Reference Data
        degrees = list(DegreeProgram.objects.all())

        if not degrees:
            self.stdout.write(self.style.ERROR('No degree programs found. Run seed_data.'))
            return

        # Generators
        def get_random_date(days_back=365):
            return timezone.now() - timedelta(days=random.randint(1, days_back))

        def create_application(status, rejection_stage=None):
            f_name = random.choice(first_names)
            l_name = random.choice(last_names)
            email = f"{f_name.lower()}.{l_name.lower()}{random.randint(1, 9999)}@example.com"
            
            # Ensure uniqueness
            if MembershipApplication.objects.filter(email=email).exists():
                return None

            app = MembershipApplication(
                title=random.choice(['Mr', 'Ms', 'Mrs']),
                first_name=f_name,
                last_name=l_name,
                date_of_birth=get_random_date(days_back=10000).date(),
                email=email,
                mobile_number=f"09{random.randint(100000000, 999999999)}",
                current_address=random.choice(addresses),
                province=random.choice(provinces),
                city=random.choice(cities),
                barangay=random.choice(barangays),
                degree_program=random.choice(degrees),
                year_graduated=str(random.randint(2000, 2024)),
                student_number=f"20{random.randint(10, 20)}-{random.randint(10000, 99999)}",
                current_employer=random.choice(employers),
                job_title=random.choice(job_titles),
                industry='Professional Services',
                payment_method=random.choice(['gcash', 'bank', 'cash']),
                status=status,
                date_applied=get_random_date(days_back=60)
            )

            # Rejection logic
            if status == 'rejected':
                app.rejection_stage = rejection_stage
                app.rejection_reason = "Mock rejection reason: Data mismatch or invalid document."
                app.rejected_at = timezone.now()
                app.rejected_by = admin_user
            
            app.save()

            # Create History Logs
            # 1. Submitted
            VerificationHistory.objects.create(
                application=app,
                action='submitted',
                timestamp=app.date_applied,
                notes='Application submitted via web form.'
            )

            # 2. Alumni Verified (if passed step 1)
            is_alumni_verified = status in ['pending_payment_verification', 'approved'] or (status == 'rejected' and rejection_stage == 'payment_verification')
            
            if is_alumni_verified:
                app.alumni_verified_at = app.date_applied + timedelta(days=1)
                app.alumni_verified_by = staff_user
                app.save()
                
                VerificationHistory.objects.create(
                    application=app,
                    action='alumni_verified',
                    performed_by=staff_user,
                    timestamp=app.alumni_verified_at,
                    notes='Verified against alumni records.'
                )

            # 3. Payment Confirmed / Approved (if passed step 2)
            if status == 'approved':
                app.approved_at = app.alumni_verified_at + timedelta(days=1)
                app.approved_by = admin_user
                app.save()
                
                VerificationHistory.objects.create(
                    application=app,
                    action='payment_confirmed',
                    performed_by=admin_user,
                    timestamp=app.approved_at,
                    notes='Payment received and confirmed.'
                )
                
                # Auto-create member (signal or manual)
                # Since we are mocking, let's ensure it exists if the signal didn't catch it, 
                # but usually the app logic might rely on views. Let's force create it here to be safe.
                Member.objects.get_or_create(application=app)

            # 4. Rejected Log
            if status == 'rejected':
                VerificationHistory.objects.create(
                    application=app,
                    action='rejected',
                    performed_by=admin_user,
                    timestamp=app.rejected_at,
                    notes=f"Rejected during {rejection_stage}. Reason: {app.rejection_reason}"
                )
                
            return app

        # Generate Records
        self.stdout.write('Generating Pending Alumni Verifications...')
        for _ in range(15):
            create_application('pending_alumni_verification')

        self.stdout.write('Generating Pending Payment Verifications...')
        for _ in range(10):
            create_application('pending_payment_verification')

        self.stdout.write('Generating Approved Members...')
        for _ in range(15):
            create_application('approved')

        self.stdout.write('Generating Rejected Applications...')
        for _ in range(5):
            create_application('rejected', rejection_stage='alumni_verification')
        for _ in range(5):
            create_application('rejected', rejection_stage='payment_verification')

        self.stdout.write(self.style.SUCCESS(f'Mock data generation complete. Total applications: {MembershipApplication.objects.count()}'))
