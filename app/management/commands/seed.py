from django.core.management.base import BaseCommand
from app.models import Election, Party
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User, Group, Permission
from app.encryption import Encryption
from datetime import datetime, timezone


class Command(BaseCommand):
    help = "Sets up a dummy election and candidates"

    def handle(self, *args, **options):

        try:
            # Create groups and assign permissions
            officials = Group.objects.create(name="Officials")
            content_types = ContentType.objects.filter(
                app_label="app", model__in=["Election", "Party"]
            )
            permissions = Permission.objects.filter(content_type__in=content_types)
            officials.permissions.set(list(permissions))
            officials.save()
            self.stdout.write(self.style.SUCCESS('Group created with permissions: "%s"' % officials.name))
            
            candidates = Group.objects.create(name="Candidates")
            content_types = ContentType.objects.filter(
                app_label="app", model__in=["Candidate"]
            )
            permissions = Permission.objects.filter(content_type__in=content_types)
            candidates.permissions.set(list(permissions))
            candidates.save()
            self.stdout.write(self.style.SUCCESS('Group created with permissions: "%s"' % candidates.name))

            citizens = Group.objects.create(name="Citizens")

            # Create superuser
            admin = User.objects.create_superuser(
                username="admin",
                email="admin@example.org",
                password="admin"
            )
            self.stdout.write(self.style.SUCCESS('User created: "%s"' % admin.username))

            # Create officials, candidates and citizens
            official = User.objects.create_user(
                username="official",
                email="official@example.org",
                password="official"
            )
            official.groups.add(officials)
            official.save()
            self.stdout.write(self.style.SUCCESS('User created: "%s"' % official.username))

            # Create multiple candidate users
            candidate1 = User.objects.create_user(
                username="candidate1",
                email="candidate1@example.org",
                password="candidate1",
                first_name="John",
                last_name="Smith"
            )
            candidate1.groups.add(candidates)
            candidate1.save()
            self.stdout.write(self.style.SUCCESS('User created: "%s"' % candidate1.username))

            candidate2 = User.objects.create_user(
                username="candidate2",
                email="candidate2@example.org",
                password="candidate2",
                first_name="Jane",
                last_name="Doe"
            )
            candidate2.groups.add(candidates)
            candidate2.save()
            self.stdout.write(self.style.SUCCESS('User created: "%s"' % candidate2.username))

            candidate3 = User.objects.create_user(
                username="candidate3",
                email="candidate3@example.org",
                password="candidate3",
                first_name="Mike",
                last_name="Johnson"
            )
            candidate3.groups.add(candidates)
            candidate3.save()
            self.stdout.write(self.style.SUCCESS('User created: "%s"' % candidate3.username))
            
            citizen = User.objects.create_superuser(
                username="citizen",
                email="citizen@example.org",
                password="citizen"
            )
            citizen.groups.add(citizens)
            citizen.save()
            self.stdout.write(self.style.SUCCESS('User created: "%s"' % citizen.username))

        except:
            pass

        # Create encryption keys (moved outside try-except block)
        encryption = Encryption()
        public_key = encryption.paillier.keys['public_key']
        private_key = encryption.paillier.keys['private_key']

        election = Election.objects.create(
            name="Presidential Election",
            start_date=datetime.now(timezone.utc),
            end_date=datetime.now(timezone.utc),
            description="This is a dummy election",
            public_key=public_key,
            private_key=private_key,
            active=True,
        )
        self.stdout.write(self.style.SUCCESS("Successfully created dummy election"))
        self.stdout.write(self.style.SUCCESS(f"Private key: {private_key}"))


        rnc = Party.objects.create(
            name="Republican Party",
            symbol="uploads/republican.jpg",
        )

        dnc = Party.objects.create(
            name="Democratic Party",
            symbol="uploads/democrats.jpg",
        )


        self.stdout.write(self.style.SUCCESS("Successfully created parties"))