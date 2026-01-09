from django.core.management.base import BaseCommand
from applications.models import DegreeProgram


class Command(BaseCommand):
    help = 'Seeds the database with reference data'

    def handle(self, *args, **kwargs):
        self.stdout.write('Seeding degree programs...')
        self.seed_degree_programs()
        
        self.stdout.write(self.style.SUCCESS('Successfully seeded database!'))

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