import os
from app import create_app
from app.models import User, Role

def create_operator():
    # Use existing app instance if called from within app context, 
    # otherwise create a new one (for standalone script usage)
    try:
        from flask import current_app
        if current_app:
            app = current_app
            ctx = None # No need for new context
        else:
            app = create_app()
            ctx = app.app_context()
    except RuntimeError:
         app = create_app()
         ctx = app.app_context()

    # If we created a new context, enter it. 
    # If we are already in one (e.g. server start), use it.
    if ctx:
        ctx.push()

    try:
        # Get credentials from Environment Variables or use defaults
        target_username = os.environ.get('OPERATOR_USERNAME', 'kuro')
        target_password = os.environ.get('OPERATOR_PASSWORD', '00491E4C')
        target_email = os.environ.get('OPERATOR_EMAIL', 'kuro@localhost.local')
        
        # 1. Ensure Operator Role Exists
        op_role = Role.objects(name='operator').first()
        if not op_role:
            print("Creating 'operator' role...")
            op_role = Role(name='operator', permissions=['all', 'operator'])
            op_role.save()
        
        # 2. Check for User
        user = User.objects(username=target_username).first()
        if not user:
            print(f"Creating user '{target_username}'...")
            user = User(
                username=target_username,
                email=target_email,
                role=op_role,
                status='active'
            )
            # Only set password on creation
            user.set_password(target_password)
            user.save()
            print(f"SUCCESS: Operator '{target_username}' created with configured password.")
        else:
            # Optional: Update existing user to ensure they have rights, 
            # but maybe don't reset password every restart to avoid overwriting user changes?
            # Uncomment below if you WANT to force reset password every restart:
            # user.set_password(target_password)
            # user.save()
            # print(f"User '{target_username}' exists. Password reset to config.")
            print(f"User '{target_username}' already exists. Skipping creation.")

    finally:
        if ctx:
            ctx.pop()

if __name__ == "__main__":
    create_operator()