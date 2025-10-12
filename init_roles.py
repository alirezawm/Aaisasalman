#!/usr/bin/env python3
"""
Initialize default roles and permissions for the system
"""

from app import app, db
import models
from datetime import datetime

def init_default_roles():
    """Initialize default roles and permissions"""
    
    with app.app_context():
        # Check if roles already exist
        if models.Role.query.count() > 0:
            print("Roles already exist. Skipping initialization.")
            return
        
        # Define default roles
        default_roles = [
            {
                'slug': 'ادمین_سایت',
                'name': 'ادمین سایت',
                'description': 'مدیر کل سیستم با دسترسی کامل',
                'permissions': [
                    'site.*',
                    'user.manage',
                    'role.manage',
                    'role.read', 'role.create', 'role.update', 'role.delete', 'role.assign', 'role.revoke',
                    'assign_privileged_role',
                    'audit.view', 'audit.read',
                    'product.read', 'product.create', 'product.update', 'product.delete',
                    'brand.read', 'brand.create', 'brand.update', 'brand.delete',
                    'order.read', 'order.create', 'order.update', 'order.delete', 'order.bulk_create',
                    'inventory.view', 'inventory.update', 'inventory.manage'
                ],
                'scope': 'site',
                'is_immutable': True
            },
            {
                'slug': 'کلربر_عمده',
                'name': 'کلربِر عمده',
                'description': 'نقش برای کاربران کلِرِبار که می‌توانند سفارشات عمده را مدیریت کنند',
                'permissions': [
                    'order.read', 'order.bulk_create', 'order.read_own',
                    'inventory.view',
                    'product.read',
                    'brand.read'
                ],
                'scope': 'site',
                'is_immutable': False
            },
            {
                'slug': 'کاربر_عادی',
                'name': 'کاربر عادی',
                'description': 'کاربر معمولی با دسترسی محدود',
                'permissions': [
                    'order.create', 'order.read_own',
                    'product.read',
                    'brand.read'
                ],
                'scope': 'site',
                'is_immutable': False
            },
            {
                'slug': 'مدیر_محصولات',
                'name': 'مدیر محصولات',
                'description': 'مدیریت محصولات و موجودی',
                'permissions': [
                    'product.read', 'product.create', 'product.update', 'product.delete',
                    'brand.read', 'brand.create', 'brand.update', 'brand.delete',
                    'inventory.view', 'inventory.update', 'inventory.manage',
                    'order.read'
                ],
                'scope': 'site',
                'is_immutable': False
            },
            {
                'slug': 'مدیر_سفارشات',
                'name': 'مدیر سفارشات',
                'description': 'مدیریت سفارشات و فاکتورها',
                'permissions': [
                    'order.read', 'order.create', 'order.update', 'order.delete',
                    'user.read',
                    'product.read',
                    'inventory.view'
                ],
                'scope': 'site',
                'is_immutable': False
            }
        ]
        
        # Create roles
        created_roles = []
        for role_data in default_roles:
            role = models.Role(
                slug=role_data['slug'],
                name=role_data['name'],
                description=role_data['description'],
                scope=role_data['scope'],
                is_immutable=role_data['is_immutable']
            )
            role.set_permissions(role_data['permissions'])
            
            db.session.add(role)
            created_roles.append(role)
        
        # Commit roles
        db.session.commit()
        
        print(f"Successfully created {len(created_roles)} default roles:")
        for role in created_roles:
            print(f"  - {role.slug}: {len(role.get_permissions())} permissions")
        
        # Assign admin role to existing admin users
        admin_users = models.User.query.filter_by(is_admin=True).all()
        admin_role = models.Role.query.filter_by(slug='ادمین_سایت').first()
        
        if admin_role and admin_users:
            for user in admin_users:
                # Check if user already has the role
                existing_role = models.UserRole.query.filter_by(
                    user_id=user.id,
                    role_id=admin_role.id,
                    scope='site'
                ).first()
                
                if not existing_role:
                    user_role = models.UserRole(
                        user_id=user.id,
                        role_id=admin_role.id,
                        scope='site',
                        assigned_by=user.id  # Self-assigned for initial setup
                    )
                    db.session.add(user_role)
                    print(f"  - Assigned admin role to user: {user.username}")
        
        db.session.commit()
        print("Role initialization completed successfully!")

def create_sample_audit_log():
    """Create a sample audit log entry"""
    
    with app.app_context():
        # Get the first admin user
        admin_user = models.User.query.filter_by(is_admin=True).first()
        if not admin_user:
            print("No admin user found for audit log creation")
            return
        
        # Create sample audit log
        audit_log = models.AuditLog(
            actor_id=admin_user.id,
            action='create_role',
            target_type='role',
            target_id=1,
            request_id='init_' + str(int(datetime.now().timestamp())),
            ip_address='127.0.0.1',
            user_agent='System Initialization'
        )
        
        audit_log.set_details({
            'role_slug': 'ادمین_سایت',
            'role_name': 'ادمین سایت',
            'permissions': ['site.*', 'user.manage', 'role.manage'],
            'scope': 'site',
            'audit_reason': 'Initial system setup'
        })
        
        db.session.add(audit_log)
        db.session.commit()
        
        print("Sample audit log created successfully!")

if __name__ == '__main__':
    print("Initializing default roles and permissions...")
    init_default_roles()
    create_sample_audit_log()
    print("Initialization completed!")
