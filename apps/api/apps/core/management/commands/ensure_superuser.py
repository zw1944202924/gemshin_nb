import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Create or normalize the production superuser from environment variables."

    def handle(self, *args, **options):
        username = os.getenv("DJANGO_SUPERUSER_USERNAME")
        email = os.getenv("DJANGO_SUPERUSER_EMAIL")
        password = os.getenv("DJANGO_SUPERUSER_PASSWORD")
        reset_password = os.getenv("DJANGO_SUPERUSER_RESET_PASSWORD", "0") == "1"

        if not username or not email or not password:
            self.stdout.write(
                "Skipped superuser setup: DJANGO_SUPERUSER_USERNAME, "
                "DJANGO_SUPERUSER_EMAIL, or DJANGO_SUPERUSER_PASSWORD is missing."
            )
            return

        User = get_user_model()
        user = User.objects.filter(username=username).first()

        if user is None:
            User.objects.create_superuser(username=username, email=email, password=password)
            self.stdout.write(f"Created superuser: {username}")
            return

        changed = False
        if user.email != email:
            user.email = email
            changed = True
        if not user.is_staff:
            user.is_staff = True
            changed = True
        if not user.is_superuser:
            user.is_superuser = True
            changed = True
        if reset_password:
            user.set_password(password)
            changed = True

        if changed:
            user.save()
            self.stdout.write(f"Updated superuser: {username}")
        else:
            self.stdout.write(f"Superuser already exists: {username}")
