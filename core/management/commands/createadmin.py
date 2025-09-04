from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()

class Command(BaseCommand):
    help = 'Create a superuser'

    def handle(self, *args, **options):
        if not User.objects.filter(is_superuser=True).exists():
            User.objects.create_superuser(
                username='Mohsen',
                email='abdull.11@outlook.com',  # CHANGE THIS TO YOUR EMAIL
                password='Moh*123321'  # CHANGE THIS TO YOUR PASSWORD
            )
            self.stdout.write(
                self.style.SUCCESS('Superuser "admin" created successfully!')
            )
            self.stdout.write('You can now login at /admin/')
        else:
            existing_admin = User.objects.filter(is_superuser=True).first()
            self.stdout.write(
                self.style.WARNING(f'Superuser already exists: {existing_admin.username}')
            )