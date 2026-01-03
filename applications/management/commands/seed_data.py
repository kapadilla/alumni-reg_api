from django.core.management.base import BaseCommand
from applications.models import Province, City, Barangay, DegreeProgram


class Command(BaseCommand):
    help = 'Seeds the database with reference data'

    def handle(self, *args, **kwargs):
        self.stdout.write('Seeding provinces...')
        self.seed_provinces()
        
        self.stdout.write('Seeding cities...')
        self.seed_cities()
        
        self.stdout.write('Seeding barangays...')
        self.seed_barangays()
        
        self.stdout.write('Seeding degree programs...')
        self.seed_degree_programs()
        
        self.stdout.write(self.style.SUCCESS('Successfully seeded database!'))

    def seed_provinces(self):
        provinces = ['Cebu', 'Metro Manila', 'Davao']
        
        for prov_name in provinces:
            Province.objects.get_or_create(name=prov_name)

    def seed_cities(self):
        cebu = Province.objects.get(name='Cebu')
        manila = Province.objects.get(name='Metro Manila')
        
        cities = [
            {'name': 'Cebu City', 'province': cebu},
            {'name': 'Mandaue City', 'province': cebu},
            {'name': 'Lapu-Lapu City', 'province': cebu},
            {'name': 'Manila', 'province': manila},
            {'name': 'Quezon City', 'province': manila},
        ]
        
        for city in cities:
            City.objects.get_or_create(
                name=city['name'],
                province=city['province']
            )

    def seed_barangays(self):
        cebu_city = City.objects.get(name='Cebu City')
        
        barangays = [
            'Lahug', 'Kamputhaw', 'Guadalupe', 'Banilad', 'Talamban'
        ]
        
        for brgy_name in barangays:
            Barangay.objects.get_or_create(
                name=brgy_name,
                city=cebu_city
            )

    def seed_degree_programs(self):
        programs = [
            {'name': 'Bachelor of Science in Computer Science', 'college': 'College of Science'},
            {'name': 'Bachelor of Arts in Communication', 'college': 'College of Arts and Humanities'},
            {'name': 'Bachelor of Science in Accountancy', 'college': 'College of Management'},
        ]
        
        for prog in programs:
            DegreeProgram.objects.get_or_create(
                name=prog['name'],
                defaults={
                    'college': prog['college'],
                    'is_active': True
                }
            )