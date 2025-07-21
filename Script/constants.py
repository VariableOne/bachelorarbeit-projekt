import random


normal_realms = [    
    'bosch',
    'telekom',
    'aws'
    ]


# response_types = ["code", "token", "id_token", "code token"]
# redirect_uris = [
#     "http://localhost:8080/admin/master/console/#/master/events",
#     "https://myapp.example.com/callback",
#     "https://anotherapp.example.com/auth/callback"
# ]


# Beispiel für bekannte Keycloak Scopes
keycloak_scopes = ["openid", "email", "profile", "offline_access", "roles", "phone"]

# Mögliche Grant Types
grant_types = ["authorization_code", "refresh_token", "client_credentials", "password", "implicit"]


    # Standard Clients in Keycloak
clients = [
        'account',               # Benutzer Account Management UI
        'admin-cli',             # CLI für Admins
        'broker',                # Identity Broker Client
        'realm-management',      # Realm Management Console Client
        'security-admin-console' # Keycloak Admin UI
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

event_types = [
    "LOGIN",
    "LOGIN_ERROR",
    "LOGOUT",
    "REGISTER",
    "UPDATE_PASSWORD",
    "UPDATE_PROFILE",
    "UPDATE_EMAIL",
    "VERIFY_EMAIL",
    "RESET_PASSWORD",
    "CODE_TO_TOKEN",
    "REVOKE_GRANT",
    "REFRESH_TOKEN",
    "CLIENT_LOGIN"
]

user_event_weights = [
    0.2,  # LOGIN
    0.15, # LOGIN_ERROR
    0.1,  # LOGOUT
    0.05, # REGISTER
    0.05, # UPDATE_PASSWORD
    0.05, # UPDATE_PROFILE
    0.02, # UPDATE_EMAIL
    0.03, # VERIFY_EMAIL
    0.03, # RESET_PASSWORD
    0.1,  # CODE_TO_TOKEN
    0.02, # REVOKE_GRANT
    0.15, # REFRESH_TOKEN
    0.05  # CLIENT_LOGIN
]


user_event_types = random.choices(event_types, weights=user_event_weights, k=1)[0]

log_levels = [
    "trace",
    "debug",
    "info",
    "warn",
    "error",
    "fatal"
]


admin_operations = ["CREATE", "UPDATE", "DELETE", "ACTION"]
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

