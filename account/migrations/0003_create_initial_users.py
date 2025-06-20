from django.db import migrations
from django.contrib.auth.hashers import make_password

def create_initial_users(apps, schema_editor):
    UserModel = apps.get_model('account', 'UserModel')
    AuthorityModel = apps.get_model('account', 'AuthorityModel')
    UserAuthorityModel = apps.get_model('account', 'UserAuthorityModel')

    # Définition des rôles à partir des choix du modèle AuthorityModel
    # Assurez-vous que ces choix correspondent à ceux dans AuthorityModel.AUTHORITY_CHOICES au moment de l'exécution de la migration
    AUTHORITY_CHOICES_TUPLE = [
        ('Administrateur', 'Administrateur'),
        ('Responsable Régional', 'Responsable Régional'),
        ('Agent Terrain', 'Agent Terrain'),
        ('Agent Technique', 'Agent Technique'),
        ('Agent Analyste', 'Agent Analyste'),
    ]

    roles = {}
    for role_value, role_display_name in AUTHORITY_CHOICES_TUPLE:
        roles[role_value] = AuthorityModel.objects.get_or_create(name=role_value)[0]

    # Données des utilisateurs à créer
    users_data = [
        # Superutilisateur (Admin)
        {
            'email': 'admin@example.com',
            'password': 'admin123',  # À changer en prod !
            'first_name': 'Admin',
            'last_name': 'System',
            'is_staff': True,
            'is_superuser': True,
            'authority': roles['Administrateur'],
            'is_primary': True,
        },
        # Responsable Régional
        {
            'email': 'responsable@example.com',
            'password': 'password123',
            'first_name': 'Jean',
            'last_name': 'Dupont',
            'authority': roles['Responsable Régional'],
            'is_primary': True,
        },
        # Agents de Terrain
        {
            'email': 'agent1@example.com',
            'password': 'password123',
            'first_name': 'Marie',
            'last_name': 'Martin',
            'authority': roles['Agent Terrain'],
            'is_primary': True,
        },
        {
            'email': 'agent2@example.com',
            'password': 'password123',
            'first_name': 'Pierre',
            'last_name': 'Durand',
            'authority': roles['Agent Terrain'],
            'is_primary': True,
        },
        # Agent Analyste
        {
            'email': 'analyste@example.com',
            'password': 'password123',
            'first_name': 'Analyste',
            'last_name': 'Expert',
            'authority': roles['Agent Analyste'],
            'is_primary': True,
        },
        # Agent Technique
        {
            'email': 'tech@example.com',
            'password': 'password123',
            'first_name': 'Technicien',
            'last_name': 'Support',
            'authority': roles['Agent Technique'],
            'is_primary': True,
        },
    ]

    for user_data in users_data:
        # Créer l'utilisateur
        user = UserModel.objects.create(
            email=user_data['email'],
            first_name=user_data['first_name'],
            last_name=user_data['last_name'],
            is_staff=user_data.get('is_staff', False),
            is_superuser=user_data.get('is_superuser', False),
            password=make_password(user_data['password']),  # Hachage du mot de passe
        )
        
        # Lier l'utilisateur à son rôle (sauf si superadmin a déjà tous les droits)
        if not user_data.get('is_superuser', False):
            UserAuthorityModel.objects.create(
                user=user,
                authority=user_data['authority'],
                is_primary=user_data['is_primary'],
            )

class Migration(migrations.Migration):
    dependencies = [
        ('account', '0002_remove_usermodel_access_level_and_more'),  # À adapter selon votre dernière migration
    ]

    operations = [
        migrations.RunPython(create_initial_users),
    ]