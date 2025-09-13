from django.core.management.base import BaseCommand
from app.models import Election, Party, Candidate, Profile
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User, Group, Permission
from app.encryption import Encryption
from datetime import datetime, timezone, timedelta
import random
from faker import Faker


class Command(BaseCommand):
    help = "Sets up comprehensive demo data with multiple elections, candidates, and users using realistic fake data"

    def handle(self, *args, **options):
        fake = Faker()
        
        self.stdout.write(self.style.WARNING("Clearing existing data..."))
        # Clear existing data in proper order to handle foreign key constraints
        Candidate.objects.all().delete()
        Profile.objects.all().delete()
        Election.objects.all().delete()
        Party.objects.all().delete()
        User.objects.filter(is_superuser=False).delete()
        Group.objects.all().delete()

        try:
            # Create groups and assign permissions
            self.stdout.write(self.style.SUCCESS("Creating user groups..."))
            officials_group = Group.objects.create(name="Officials")
            candidates_group = Group.objects.create(name="Candidates")
            citizens_group = Group.objects.create(name="Citizens")
            
            # Assign permissions to groups
            content_types = ContentType.objects.filter(app_label="app")
            permissions = Permission.objects.filter(content_type__in=content_types)
            officials_group.permissions.set(permissions)
            
            self.stdout.write(self.style.SUCCESS("✅ Created user groups with permissions"))

            # Create admin user if doesn't exist
            admin, created = User.objects.get_or_create(
                username="admin",
                defaults={
                    "email": "admin@intikhab.org",
                    "first_name": "System",
                    "last_name": "Administrator",
                    "is_superuser": True,
                    "is_staff": True
                }
            )
            if created:
                admin.set_password("admin123")
                admin.save()
                self.stdout.write(self.style.SUCCESS(f"✅ Created admin user: {admin.username}"))
            else:
                self.stdout.write(self.style.WARNING(f"⚠️  Admin user already exists: {admin.username}"))

            # Create diverse political parties
            self.stdout.write(self.style.SUCCESS("Creating political parties..."))
            parties_data = [
                {"name": "Progressive Alliance", "description": "Forward-thinking policies for sustainable development"},
                {"name": "Conservative Coalition", "description": "Traditional values and fiscal responsibility"},
                {"name": "Green Movement", "description": "Environmental protection and renewable energy"},
                {"name": "Labor Unity Party", "description": "Workers' rights and social justice"},
                {"name": "Liberal Democrats", "description": "Individual freedoms and democratic reforms"},
                {"name": "National Security Party", "description": "Strong defense and border security"},
                {"name": "Tech Innovation Party", "description": "Digital transformation and innovation"},
                {"name": "Rural Development Party", "description": "Agricultural and rural community focus"},
            ]
            
            parties = []
            for party_data in parties_data:
                party = Party.objects.create(
                    name=party_data["name"],
                    symbol=f"uploads/{fake.file_name(extension='jpg')}"
                )
                parties.append(party)
            
            self.stdout.write(self.style.SUCCESS(f"✅ Created {len(parties)} political parties"))

            # Create many users with realistic data
            self.stdout.write(self.style.SUCCESS("Creating users with realistic data..."))
            
            # Create officials (5-8 users)
            officials = []
            for i in range(random.randint(5, 8)):
                username = f"official_{fake.random_int(1000, 9999)}_{i+1}"
                official = User.objects.create_user(
                    username=username,
                    email=fake.email(),
                    password="password123",
                    first_name=fake.first_name(),
                    last_name=fake.last_name()
                )
                official.groups.add(officials_group)
                officials.append(official)
            
            # Create potential candidates (20-30 users)
            candidate_users = []
            for i in range(random.randint(20, 30)):
                username = f"candidate_{fake.random_int(1000, 9999)}_{i+1}"
                candidate = User.objects.create_user(
                    username=username,
                    email=fake.email(),
                    password="password123",
                    first_name=fake.first_name(),
                    last_name=fake.last_name()
                )
                candidate.groups.add(candidates_group)
                candidate_users.append(candidate)
                
                # Create profile for each candidate
                Profile.objects.create(
                    user=candidate,
                    profile=fake.text(max_nb_chars=300),
                    manifesto=fake.text(max_nb_chars=500),
                    location=f"{fake.city()}, {fake.state_abbr()}",
                    gender=random.choice(['M', 'F', 'O'])
                )
            
            # Create regular citizens (15-25 users)
            citizens = []
            for i in range(random.randint(15, 25)):
                username = f"citizen_{fake.random_int(1000, 9999)}_{i+1}"
                citizen = User.objects.create_user(
                    username=username,
                    email=fake.email(),
                    password="password123",
                    first_name=fake.first_name(),
                    last_name=fake.last_name()
                )
                citizen.groups.add(citizens_group)
                citizens.append(citizen)
            
            self.stdout.write(self.style.SUCCESS(f"✅ Created {len(officials)} officials, {len(candidate_users)} candidates, {len(citizens)} citizens"))

            # Create diverse elections with varying dates
            self.stdout.write(self.style.SUCCESS("Creating elections with varying timeframes..."))
            
            now = datetime.now(timezone.utc)
            elections = []
            
            # Election templates with realistic data
            election_templates = [
                {
                    "name": "Presidential Election 2025",
                    "description": "National presidential election to elect the next president for a four-year term.",
                    "type": "completed"
                },
                {
                    "name": "Congressional Midterm Elections",
                    "description": "Election for House of Representatives and Senate seats in various districts.",
                    "type": "ongoing"
                },
                {
                    "name": "State Governor Election",
                    "description": "Gubernatorial election to choose the state's chief executive officer.",
                    "type": "upcoming"
                },
                {
                    "name": "Municipal Mayor Election",
                    "description": "Local election for city mayor and municipal council positions.",
                    "type": "completed"
                },
                {
                    "name": "School Board Elections",
                    "description": "Educational district elections for school board member positions.",
                    "type": "ongoing"
                },
                {
                    "name": "County Commissioner Race",
                    "description": "County-level election for commissioner positions and local measures.",
                    "type": "upcoming"
                },
                {
                    "name": "Special Senate Election",
                    "description": "Special election to fill vacant Senate seat following resignation.",
                    "type": "completed"
                },
                {
                    "name": "Judicial Elections",
                    "description": "Non-partisan election for local and state judicial positions.",
                    "type": "upcoming"
                },
                {
                    "name": "Ballot Measures Referendum",
                    "description": "Referendum on various local and state ballot measures and propositions.",
                    "type": "ongoing"
                }
            ]
            
            for template in election_templates:
                # Generate encryption keys for each election
                encryption = Encryption()
                public_key = encryption.paillier.keys['public_key']
                private_key = encryption.paillier.keys['private_key']
                
                # Set dates based on election type
                if template["type"] == "completed":
                    # Elections that ended 1-90 days ago
                    end_date = now - timedelta(days=random.randint(1, 90))
                    start_date = end_date - timedelta(days=random.randint(7, 30))
                    active = False
                elif template["type"] == "ongoing":
                    # Elections that started 1-7 days ago and end 1-14 days from now
                    start_date = now - timedelta(days=random.randint(1, 7))
                    end_date = now + timedelta(days=random.randint(1, 14))
                    active = True
                else:  # upcoming
                    # Elections that start 1-60 days from now
                    start_date = now + timedelta(days=random.randint(1, 60))
                    end_date = start_date + timedelta(days=random.randint(7, 30))
                    active = False
                
                election = Election.objects.create(
                    name=template["name"],
                    description=template["description"],
                    start_date=start_date,
                    end_date=end_date,
                    created_by=random.choice(officials),
                    public_key=public_key,
                    private_key=private_key,
                    active=active
                )
                elections.append(election)
                
                # Add candidates to each election (2-6 candidates per election)
                num_candidates = random.randint(2, 6)
                selected_candidates = random.sample(candidate_users, min(num_candidates, len(candidate_users)))
                
                for i, candidate_user in enumerate(selected_candidates):
                    # Some candidates have party affiliation, some are independent
                    party = random.choice(parties) if random.random() > 0.3 else None
                    
                    Candidate.objects.create(
                        user=candidate_user,
                        party=party,
                        election=election,
                        symbol=f"uploads/{fake.file_name(extension='jpg')}" if random.random() > 0.5 else None
                    )
            
            self.stdout.write(self.style.SUCCESS(f"✅ Created {len(elections)} elections with candidates"))
            
            # Summary
            completed_elections = len([e for e in elections if e.end_date < now])
            ongoing_elections = len([e for e in elections if e.start_date <= now <= e.end_date])
            upcoming_elections = len([e for e in elections if e.start_date > now])
            
            self.stdout.write(self.style.SUCCESS("=" * 50))
            self.stdout.write(self.style.SUCCESS("🗳️  SEED DATA SUMMARY"))
            self.stdout.write(self.style.SUCCESS("=" * 50))
            self.stdout.write(self.style.SUCCESS(f"👥 Users: {User.objects.count()} total"))
            self.stdout.write(self.style.SUCCESS("   - Admins: 1"))
            self.stdout.write(self.style.SUCCESS(f"   - Officials: {len(officials)}"))
            self.stdout.write(self.style.SUCCESS(f"   - Candidates: {len(candidate_users)}"))
            self.stdout.write(self.style.SUCCESS(f"   - Citizens: {len(citizens)}"))
            self.stdout.write(self.style.SUCCESS(f"🏛️  Parties: {len(parties)}"))
            self.stdout.write(self.style.SUCCESS(f"🗳️  Elections: {len(elections)} total"))
            self.stdout.write(self.style.SUCCESS(f"   - Completed: {completed_elections}"))
            self.stdout.write(self.style.SUCCESS(f"   - Ongoing: {ongoing_elections}"))
            self.stdout.write(self.style.SUCCESS(f"   - Upcoming: {upcoming_elections}"))
            self.stdout.write(self.style.SUCCESS(f"🏃 Candidates: {Candidate.objects.count()} total"))
            self.stdout.write(self.style.SUCCESS("=" * 50))
            self.stdout.write(self.style.SUCCESS("Login credentials:"))
            self.stdout.write(self.style.SUCCESS("  Admin: admin / admin123"))
            self.stdout.write(self.style.SUCCESS(f"  Officials: {officials[0].username} / password123"))
            self.stdout.write(self.style.SUCCESS(f"  Candidates: {candidate_users[0].username} / password123"))
            self.stdout.write(self.style.SUCCESS(f"  Citizens: {citizens[0].username} / password123"))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Error creating seed data: {e}"))