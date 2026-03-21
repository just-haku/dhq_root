import click
import os
from flask.cli import with_appcontext
from app.models import Role
# Import the shared logic so we don't duplicate code
# Ensure create_operator.py is in the python path or move the function to app/utils.py
from create_operator import create_operator 

@click.command('init-db')
@with_appcontext
def init_db():
    """
    Initializes the database structure and ensures default roles exist.
    Also triggers the environment-aware operator creation.
    """
    click.echo('Initializing Database Defaults...')

    # --- 1. Ensure Roles Exist ---
    roles_to_create = [
        {'name': 'admin', 'permissions': ['all']},
        {'name': 'operator', 'permissions': ['manage_orders', 'view_reports']},
        {'name': 'user', 'permissions': []}
    ]

    for role_data in roles_to_create:
        role = Role.objects(name=role_data['name']).first()
        if not role:
            role = Role(name=role_data['name'], permissions=role_data['permissions'])
            role.save()
            click.echo(f'- Created Role: {role_data["name"]}')
        else:
            # Optional: Ensure permissions match code definitions
            if set(role.permissions) != set(role_data['permissions']):
                role.permissions = role_data['permissions']
                role.save()
                click.echo(f'- Updated Role permissions: {role_data["name"]}')

    # --- 2. Create/Update Operator Account (Using Shared Logic) ---
    click.echo('Checking Operator Account...')
    try:
        # This function now handles env vars: OPERATOR_USERNAME / OPERATOR_PASSWORD
        create_operator() 
        click.echo('- Operator check complete (Created/Updated from Env).')
    except Exception as e:
        click.echo(f'Error creating operator: {e}')

    click.echo('Database initialization complete.')