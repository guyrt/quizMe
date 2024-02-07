from django.core.management.base import BaseCommand

from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    help = "Create a regular user from the command line"

    def handle(self, *args, **options):
        username = input("Enter email: ")
        password = input("Enter password: ")

        user = User.objects.create_user(password=password, email=username)
        self.stdout.write(self.style.SUCCESS(f"Successfully created user: {user.email}"))
