import datetime
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.hashers import make_password
from django.db import IntegrityError, transaction

from account.models import UserModel, AuthorityModel, UserAuthorityModel
from image.models import ImageModel
from detection.models import DetectionModel, InvestigationModel
from region.models.region_model import RegionModel # Adjusted import

class Command(BaseCommand):
    help = 'Creates default users, authorities, and optionally demo data. Also creates/updates a default region for demo.'

    AUTHORITY_CHOICES_TUPLE = [
        ('Administrateur', 'Administrateur'),
        ('Responsable Régional', 'Responsable Régional'),
        ('Agent Terrain', 'Agent Terrain'),
        ('Agent Technique', 'Agent Technique'),
        ('Agent Analyste', 'Agent Analyste'),
    ]

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Delete existing users (except superusers), their authorities, and related demo data before creating new ones.'
        )
        parser.add_argument(
            '--demo',
            action='store_true',
            help='Create additional demo data (image, detection, investigation, and ensure Bondoukou region exists).'
        )

    @transaction.atomic
    def handle(self, *args, **options):
        force = options['force']
        create_demo = options['demo']

        if force:
            self.stdout.write(self.style.WARNING('Force option selected. Deleting existing data...'))
            # Order of deletion matters due to foreign key constraints
            InvestigationModel.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('Successfully deleted all InvestigationModel objects.'))
            DetectionModel.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('Successfully deleted all DetectionModel objects.'))
            ImageModel.objects.filter(name__icontains='Demo').delete() # Delete only demo images
            self.stdout.write(self.style.SUCCESS('Successfully deleted demo ImageModel objects.'))

            UserAuthorityModel.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('Successfully deleted all UserAuthorityModel objects.'))

            # Keep superusers by default, delete others if force is used
            UserModel.objects.filter(is_superuser=False).delete()
            self.stdout.write(self.style.SUCCESS('Successfully deleted all non-superuser UserModel objects.'))
            # Optionally, delete specific authorities if they were managed by this script,
            # but get_or_create handles existing ones well. For a full reset of authorities:
            # AuthorityModel.objects.filter(name__in=[choice[0] for choice in self.AUTHORITY_CHOICES_TUPLE]).delete()
            # self.stdout.write(self.style.SUCCESS('Successfully deleted managed AuthorityModel objects.'))

        self.stdout.write(self.style.HTTP_INFO('Creating/Verifying Authorities...'))
        roles = {}
        for role_value, role_display_name in self.AUTHORITY_CHOICES_TUPLE:
            try:
                authority, created = AuthorityModel.objects.get_or_create(name=role_value)
                roles[role_value] = authority
                if created:
                    self.stdout.write(self.style.SUCCESS(f'Authority "{role_display_name}" created.'))
                else:
                    self.stdout.write(self.style.NOTICE(f'Authority "{role_display_name}" already exists.'))
            except Exception as e:
                self.stderr.write(self.style.ERROR(f'Error creating authority "{role_display_name}": {e}'))
                return # Stop if authorities can't be set up

        self.stdout.write(self.style.HTTP_INFO('Creating Default Users...'))
        users_data = [
            {
                'email': 'admin@example.com', 'password': 'adminpassword', 'first_name': 'Admin', 'last_name': 'System',
                'is_staff': True, 'is_superuser': True, 'authority_name': 'Administrateur', 'is_primary': True
            },
            {
                'email': 'responsable@example.com', 'password': 'respopassword', 'first_name': 'Jean', 'last_name': 'Dupont',
                'authority_name': 'Responsable Régional', 'is_primary': True
            },
            {
                'email': 'agent.terrain1@example.com', 'password': 'agentpassword', 'first_name': 'Marie', 'last_name': 'Martin',
                'authority_name': 'Agent Terrain', 'is_primary': True
            },
            {
                'email': 'agent.terrain2@example.com', 'password': 'agentpassword', 'first_name': 'Pierre', 'last_name': 'Durand',
                'authority_name': 'Agent Terrain', 'is_primary': True
            },
            {
                'email': 'analyste@example.com', 'password': 'analystpassword', 'first_name': 'Analyste', 'last_name': 'Expert',
                'authority_name': 'Agent Analyste', 'is_primary': True
            },
            {
                'email': 'tech@example.com', 'password': 'techpassword', 'first_name': 'Technicien', 'last_name': 'Support',
                'authority_name': 'Agent Technique', 'is_primary': True
            },
        ]

        agent_terrain_user_for_demo = None

        for user_data in users_data:
            try:
                user, created = UserModel.objects.get_or_create(
                    email=user_data['email'],
                    defaults={
                        'first_name': user_data['first_name'],
                        'last_name': user_data['last_name'],
                        'is_staff': user_data.get('is_staff', False),
                        'is_superuser': user_data.get('is_superuser', False),
                        'password': make_password(user_data['password']),
                    }
                )
                if created:
                     # For existing users (if --force not used), update password if needed, or other fields
                    self.stdout.write(self.style.SUCCESS(f'User {user.email} created.'))
                elif user_data.get('is_superuser') and not user.is_superuser :
                    # if admin@example.com exists but is not superuser, make it superuser
                    user.is_superuser = True
                    user.is_staff = True # Superusers must be staff
                    user.set_password(user_data['password']) # reset password
                    user.save()
                    self.stdout.write(self.style.WARNING(f'User {user.email} already existed and was updated to be a superuser.'))
                else:
                    self.stdout.write(self.style.NOTICE(f'User {user.email} already exists. Skipping creation.'))

                # Link authority
                authority = roles.get(user_data['authority_name'])
                if authority:
                    ua, ua_created = UserAuthorityModel.objects.get_or_create(
                        user=user, authority=authority,
                        defaults={'is_primary': user_data.get('is_primary', False)}
                    )
                    if ua_created:
                        self.stdout.write(self.style.SUCCESS(f'Linked {user.email} to {authority.name} authority.'))
                    else:
                         # If link exists, ensure is_primary is correctly set
                        if ua.is_primary != user_data.get('is_primary', False):
                            ua.is_primary = user_data.get('is_primary', False)
                            ua.save()
                            self.stdout.write(self.style.NOTICE(f'Updated primary status for {user.email} with {authority.name} authority.'))
                        else:
                            self.stdout.write(self.style.NOTICE(f'{user.email} already linked to {authority.name} authority.'))


                if user_data['authority_name'] == 'Agent Terrain' and not agent_terrain_user_for_demo:
                    agent_terrain_user_for_demo = user

            except IntegrityError as e:
                self.stderr.write(self.style.ERROR(f'Error creating user {user_data["email"]}: {e}. This might happen if email exists with different casing and DB collation is case-sensitive.'))
            except Exception as e:
                self.stderr.write(self.style.ERROR(f'An unexpected error occurred for user {user_data["email"]}: {e}'))


        if create_demo:
            self.stdout.write(self.style.HTTP_INFO('Creating Demo Data...'))
            try:
                # 1. Get/Create Region
                bondoukou_region, region_created = RegionModel.objects.get_or_create(
                    name='BONDOUKOU',
                    defaults={'code': 'BKO', 'area_km2': 12500, 'center_lat': 8.0402, 'center_lon': -2.8000}
                )
                if region_created:
                    self.stdout.write(self.style.SUCCESS(f'Region "{bondoukou_region.name}" created.'))
                else:
                    self.stdout.write(self.style.NOTICE(f'Region "{bondoukou_region.name}" already exists.'))

                # 2. Create Demo Image
                demo_image_name = 'Demo Sentinel-2 Image Bondoukou - Default Users'
                demo_image, image_created = ImageModel.objects.get_or_create(
                    name=demo_image_name,
                    region=bondoukou_region,
                    defaults={
                        'capture_date': datetime.date.today() - datetime.timedelta(days=10),
                        'satellite_source': 'SENTINEL2',
                        'cloud_coverage': 5.0,
                        'gee_asset_id': 'projects/default-gcp-project/assets/demo_image_bondoukou_default',
                        'center_lat': 8.0402,
                        'center_lon': -2.8000,
                        'processing_status': ImageModel.ProcessingStatus.COMPLETED
                    }
                )
                if image_created:
                    self.stdout.write(self.style.SUCCESS(f'Demo Image "{demo_image.name}" created.'))
                else:
                    self.stdout.write(self.style.NOTICE(f'Demo Image "{demo_image.name}" already exists.'))

                # 3. Create Demo Detection
                demo_detection, detection_created = DetectionModel.objects.get_or_create(
                    image=demo_image,
                    region=bondoukou_region,
                    latitude=8.0500,
                    longitude=-2.8500,
                    defaults={
                        'detection_type': DetectionModel.DetectionType.MINING_SITE,
                        'confidence_score': 0.88,
                        'area_hectares': 2.1,
                        'ndvi_anomaly_score': 0.72,
                        'ndwi_anomaly_score': 0.63,
                        'ndti_anomaly_score': 0.51,
                        'validated': False, # Default, can be updated by analyst
                    }
                )
                if detection_created:
                    self.stdout.write(self.style.SUCCESS('Demo Detection created.'))
                else:
                    self.stdout.write(self.style.NOTICE('Demo Detection already exists.'))

                # 4. Create Demo Investigation
                if not agent_terrain_user_for_demo:
                    # Fallback if no agent terrain was specifically captured (e.g., if all users existed)
                    agent_terrain_user_for_demo = UserModel.objects.filter(user_authorities__authority__name='Agent Terrain').first()

                if agent_terrain_user_for_demo:
                    demo_investigation, inv_created = InvestigationModel.objects.get_or_create(
                        detection=demo_detection,
                        defaults={
                             'assigned_to': agent_terrain_user_for_demo,
                             'target_coordinates': f"{demo_detection.latitude}, {demo_detection.longitude}",
                             'status': InvestigationModel.StatusChoices.ASSIGNED,
                             'priority': InvestigationModel.PriorityChoices.MEDIUM,
                             'notes': "Automated investigation for demo detection."
                        }
                    )
                    if inv_created:
                        self.stdout.write(self.style.SUCCESS(f'Demo Investigation created and assigned to {agent_terrain_user_for_demo.email}.'))
                    else:
                        self.stdout.write(self.style.NOTICE('Demo Investigation for this detection already exists.'))
                else:
                    self.stdout.write(self.style.WARNING('Could not create demo investigation: No "Agent Terrain" user found.'))

                self.stdout.write(self.style.SUCCESS('Demo data creation process finished.'))

            except ImportError as ie:
                 self.stderr.write(self.style.ERROR(f"Failed to import a model for demo data, skipping: {ie}"))
            except Exception as e:
                self.stderr.write(self.style.ERROR(f'Error creating demo data: {e}'))

        self.stdout.write(self.style.SUCCESS('Default user and authority creation process finished.'))
