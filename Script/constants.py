normal_realms = [    
    'bosch',
    'telekom'
    ]

    # Standard Clients in Keycloak
clients = [
        'account',               # Benutzer Account Management UI
        'admin-cli',             # CLI für Admins
        'broker',                # Identity Broker Client
        'realm-management',      # Realm Management Console Client
        'security-admin-console' # Keycloak Admin UI
    ]

    # Realm Roles (Beispiele aus Keycloak realm-level roles)
realm_roles = [
        'admin',
        'realm-admin',
        'create-realm',
        'impersonation',
        'manage-users',
        'manage-realm',
        'manage-clients',
        'view-users',
        'manage-events',
        'query-users',
        'manage-authorization',
        'admin-cli',
        'offline_access',
        'uma_authorization',
    ]

    # Client Roles (Beispiele aus Keycloak client-level roles)
client_roles = [
        'manage-account',
        'view-profile',
        'manage-account-links',
        'view-consent',
        'manage-consent',
        'view-realm',
        'manage-realm',
        'view-users',
        'manage-users',
        'manage-clients',
        'view-clients',
        'manage-events',
        'manage-authorization',
        'create-client',
        'manage-account:manage-account',
        'account:view-profile',
    ]

    # Client Scopes (Keycloak Standard Scopes)
client_scopes = [
        'profile',
        'email',
        'roles',
        'web-origins',
        'offline_access',
        'microprofile-jwt',  # wenn aktiviert
    ]


    # Auth Protocols (Keycloak unterstützt vor allem)
protocols = [
        'openid-connect',
        'saml',
        'oauth2-client-credentials',
        'password',
        'otp',
        'browser',
        'code',
    ]

    # Connections (User Federation Providers & Identity Providers)
connections = [
        'default',
        'ldap',
        'kerberos',
        'saml',
        'github',
        'google',
        'facebook',
        'twitter',
        'openid-connect',
    ]

user_event_types = [
    "LOGIN",
    "LOGIN_ERROR",
    "LOGOUT",
    "REGISTER",
    "REGISTER_ERROR",
    "UPDATE_PASSWORD",
    "UPDATE_PROFILE",
    "UPDATE_EMAIL",
    "VERIFY_EMAIL",
    "FORGOT_PASSWORD",
    "RESET_PASSWORD",
    "CODE_TO_TOKEN",
    "CODE_TO_TOKEN_ERROR",
    "CLIENT_LOGIN",
    "CLIENT_LOGIN_ERROR",
    "REVOKE_GRANT",
    "IMPERSONATE",
    "IMPERSONATE_ERROR",
    "BRUTE_FORCE_ERROR",
    "BRUTE_FORCE_RESET",
    "TOKEN_REFRESH"
]

log_levels = [
    "trace",
    "debug",
    "info",
    "warn",
    "error",
    "fatal"
]


admin_operations = ["CREATE", "UPDATE", "DELETE", "GET"]
resource_types = ["users", "clients", "roles", "groups", "authentication"]

#with open("names.json") as f:
#    names = json.load(f)
#    user_pool = names[:50]

names = [
        'Anna', 'Bob', 'Carlos', 'Diana', 'Elena', 'Faisal', 'Gina', 'Hiroshi', 'Isabel',
        'Jamal', 'Klara', 'Luca', 'Maya', 'Nina', 'Omar', 'Priya', 'Quentin', 'Rina',
        'Sofia', 'Tom', 'Usha', 'Victor', 'Wei', 'Yara', 'Zane', 'Ivan', 'Zara',
        'Mikhail', 'Layla', 'Rashid', 'Svetlana', 'Oleg', 'Nadia', 'Kenji', 'Farah'
    ]

user_pool = names[:25]

