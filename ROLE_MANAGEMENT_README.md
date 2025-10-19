# Role Management System

This document describes the comprehensive role management system implemented for the admin panel, following the JSON prompt specifications.

## Overview

The role management system provides a complete RBAC (Role-Based Access Control) solution with:
- Role creation and management
- User role assignment and revocation
- Permission-based access control
- Comprehensive audit logging
- Persian language support

## Features

### 1. Role Management
- **Create Roles**: Define new roles with specific permissions
- **Edit Roles**: Modify role permissions and descriptions
- **Delete Roles**: Remove roles (with immutability protection for core roles)
- **View Role Details**: Comprehensive role information display

### 2. User Role Assignment
- **Assign Roles**: Grant roles to users with audit trail
- **Revoke Roles**: Remove roles from users
- **Scope Management**: Support for site, tenant, and store scopes
- **Bulk Operations**: Manage multiple user roles efficiently

### 3. Permission System
- **Granular Permissions**: Fine-grained access control
- **Permission Inheritance**: Support for wildcard permissions (e.g., `site.*`)
- **Role Hierarchy**: Different permission levels for different roles
- **Dynamic Checking**: Real-time permission validation

### 4. Audit Logging
- **Complete Trail**: All role operations are logged
- **Request Tracking**: Unique request IDs for operation tracking
- **Detailed Information**: IP addresses, user agents, and operation details
- **Search and Filter**: Advanced filtering capabilities

## Default Roles

The system comes with pre-configured roles:

### 1. ادمین_سایت (Site Admin)
- **Permissions**: Full system access (`site.*`, `user.manage`, `role.manage`, etc.)
- **Scope**: Site-wide
- **Immutable**: Yes (cannot be deleted)

### 2. کلربر_عمده (Bulk Buyer)
- **Permissions**: Order management, inventory viewing
- **Scope**: Site-wide
- **Immutable**: No

### 3. کاربر_عادی (Regular User)
- **Permissions**: Basic order creation and product viewing
- **Scope**: Site-wide
- **Immutable**: No

### 4. مدیر_محصولات (Product Manager)
- **Permissions**: Product and brand management
- **Scope**: Site-wide
- **Immutable**: No

### 5. مدیر_سفارشات (Order Manager)
- **Permissions**: Order and invoice management
- **Scope**: Site-wide
- **Immutable**: No

## API Endpoints

### Role Management
- `GET /api/v1/roles` - List all roles
- `POST /api/v1/roles` - Create new role
- `PUT /api/v1/roles/<role_id>` - Update role (planned)
- `DELETE /api/v1/roles/<role_id>` - Delete role (planned)

### User Role Management
- `GET /api/v1/users/<user_id>/roles` - Get user's roles
- `POST /api/v1/users/<user_id>/roles` - Assign role to user
- `DELETE /api/v1/users/<user_id>/roles/<role_slug>` - Revoke role from user

### Audit Logs
- `GET /api/v1/audit-logs` - Get audit logs with pagination

### User Management
- `GET /api/v1/users` - List users for role assignment

## Permission System

### Permission Categories
1. **Role Management**: `role.read`, `role.create`, `role.update`, `role.delete`, `role.assign`, `role.revoke`
2. **User Management**: `user.read`, `user.create`, `user.update`, `user.delete`, `user.manage`
3. **Site Management**: `site.*`, `site.read`, `site.update`
4. **Order Management**: `order.read`, `order.create`, `order.update`, `order.delete`, `order.bulk_create`
5. **Inventory Management**: `inventory.view`, `inventory.update`, `inventory.manage`
6. **Product Management**: `product.read`, `product.create`, `product.update`, `product.delete`
7. **Brand Management**: `brand.read`, `brand.create`, `brand.update`, `brand.delete`
8. **Audit Management**: `audit.view`, `audit.read`

### Permission Checking
- **Decorators**: `@role_required(permission)` for API routes
- **Web Routes**: `@permission_required(permission)` for web pages
- **Dynamic Checking**: `current_user.has_permission(permission)`
- **Role Checking**: `current_user.has_role(role_slug)`

## Database Models

### Role Model
```python
class Role(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    slug = db.Column(db.String(50), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    permissions = db.Column(db.Text)  # JSON string
    scope = db.Column(db.String(20), default='site')
    is_active = db.Column(db.Boolean, default=True)
    is_immutable = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
```

### UserRole Model
```python
class UserRole(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey('role.id'), nullable=False)
    scope = db.Column(db.String(20), default='site')
    assigned_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    assigned_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
```

### AuditLog Model
```python
class AuditLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    actor_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    action = db.Column(db.String(50), nullable=False)
    target_type = db.Column(db.String(20), nullable=False)
    target_id = db.Column(db.Integer, nullable=False)
    details = db.Column(db.Text)  # JSON string
    request_id = db.Column(db.String(100))
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
```

## Setup Instructions

### 1. Initialize Roles
```bash
python init_roles.py
```

### 2. Access Admin Panel
- Navigate to `/admin/roles` for role management
- Navigate to `/admin/user_roles` for user role assignment
- Navigate to `/admin/audit_logs` for audit trail viewing

### 3. API Usage Examples

#### Create a Role
```bash
curl -X POST /api/v1/roles \
  -H "Content-Type: application/json" \
  -H "X-Request-ID: req_123" \
  -d '{
    "role": {
      "slug": "test_role",
      "name": "Test Role",
      "description": "A test role",
      "permissions": ["order.read", "product.read"],
      "scope": "site"
    },
    "audit_reason": "Creating test role"
  }'
```

#### Assign Role to User
```bash
curl -X POST /api/v1/users/1/roles \
  -H "Content-Type: application/json" \
  -H "X-Request-ID: req_124" \
  -d '{
    "role_slug": "test_role",
    "scope": "site",
    "audit_reason": "Assigning test role to user"
  }'
```

## Security Features

### 1. Immutable Core Roles
- Core roles like `ادمین_سایت` cannot be deleted
- Protected against accidental removal

### 2. Privileged Role Assignment
- Special permission required for assigning privileged roles
- Additional validation for sensitive operations

### 3. Audit Trail
- All operations are logged with complete details
- Request tracking for debugging and compliance
- IP address and user agent logging

### 4. Permission Validation
- Real-time permission checking
- Granular access control
- Role-based restrictions

## UI Features

### 1. Role Management Interface
- **Search and Filter**: Find roles quickly
- **Permission Management**: Visual permission selection
- **Role Details**: Comprehensive role information
- **Bulk Operations**: Manage multiple roles

### 2. User Role Assignment
- **User Selection**: Easy user picker
- **Role Assignment**: Simple role assignment interface
- **Audit Reason**: Required reason for all operations
- **Scope Management**: Multi-scope support

### 3. Audit Log Viewer
- **Advanced Filtering**: Filter by action, user, date
- **Detailed View**: Complete operation details
- **Export Capabilities**: Export logs for analysis
- **Real-time Updates**: Live log monitoring

## Error Handling

### Standard Error Responses
```json
{
  "success": false,
  "status": 400,
  "message": "Error description",
  "data": null,
  "request_id": "req_123"
}
```

### Common Error Codes
- **400**: Bad Request - Validation errors
- **401**: Unauthorized - Authentication required
- **403**: Forbidden - Insufficient permissions
- **404**: Not Found - Resource not found
- **409**: Conflict - Duplicate or constraint violation
- **500**: Internal Server Error - Server errors

## Best Practices

### 1. Role Design
- Use descriptive role names and slugs
- Group related permissions logically
- Avoid overly broad permissions
- Document role purposes

### 2. Permission Management
- Use specific permissions over wildcards when possible
- Regularly review and audit permissions
- Implement least privilege principle
- Monitor permission usage

### 3. Audit Compliance
- Always provide audit reasons
- Use meaningful request IDs
- Regularly review audit logs
- Implement log retention policies

### 4. Security
- Regularly update role assignments
- Monitor for privilege escalation
- Implement role expiration if needed
- Use secure communication channels

## Troubleshooting

### Common Issues

1. **Permission Denied Errors**
   - Check user's role assignments
   - Verify permission requirements
   - Ensure proper authentication

2. **Role Assignment Failures**
   - Check if role exists and is active
   - Verify user is active
   - Ensure proper permissions for assignment

3. **Audit Log Issues**
   - Check database connectivity
   - Verify audit logging is enabled
   - Review error logs for details

### Debug Mode
Enable debug logging by setting appropriate log levels in the application configuration.

## Future Enhancements

### Planned Features
1. **Role Templates**: Pre-defined role templates
2. **Role Inheritance**: Hierarchical role relationships
3. **Time-based Roles**: Temporary role assignments
4. **API Rate Limiting**: Enhanced API security
5. **Role Analytics**: Usage statistics and insights
6. **Bulk Operations**: Mass role assignments
7. **Role Approval Workflow**: Multi-step role assignment process

### Integration Points
1. **LDAP/Active Directory**: External user management
2. **SSO Integration**: Single sign-on support
3. **Notification System**: Role change notifications
4. **Reporting System**: Advanced reporting capabilities

## Support

For technical support or questions about the role management system:
1. Check the audit logs for operation details
2. Review the API documentation
3. Consult the troubleshooting guide
4. Contact the system administrator

---

*This role management system is designed to be secure, scalable, and user-friendly while maintaining comprehensive audit trails and flexible permission management.*
