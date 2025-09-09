#!/bin/bash

# Keycloak setup script
KEYCLOAK_URL="http://localhost:8080"
ADMIN_USER="admin"
ADMIN_PASSWORD="admin"
REALM_NAME="mfinance"
CLIENT_ID="mfinance-web"

echo "Setting up Keycloak for MFinance..."

# Wait for Keycloak to be ready
echo "Waiting for Keycloak to be ready..."
until curl -f -s "$KEYCLOAK_URL/realms/master" > /dev/null; do
    echo "Waiting for Keycloak..."
    sleep 5
done

echo "Keycloak is ready!"

# Get admin token
echo "Getting admin token..."
ADMIN_TOKEN=$(curl -s -X POST "$KEYCLOAK_URL/realms/master/protocol/openid-connect/token" \
    -H "Content-Type: application/x-www-form-urlencoded" \
    -d "username=$ADMIN_USER" \
    -d "password=$ADMIN_PASSWORD" \
    -d "grant_type=password" \
    -d "client_id=admin-cli" | jq -r '.access_token')

if [ "$ADMIN_TOKEN" = "null" ] || [ -z "$ADMIN_TOKEN" ]; then
    echo "Failed to get admin token"
    exit 1
fi

echo "Admin token obtained!"

# Create realm
echo "Creating realm: $REALM_NAME"
curl -s -X POST "$KEYCLOAK_URL/admin/realms" \
    -H "Authorization: Bearer $ADMIN_TOKEN" \
    -H "Content-Type: application/json" \
    -d '{
        "realm": "'$REALM_NAME'",
        "enabled": true,
        "displayName": "MFinance",
        "loginWithEmailAllowed": true,
        "duplicateEmailsAllowed": false,
        "resetPasswordAllowed": true,
        "editUsernameAllowed": true,
        "bruteForceProtected": true
    }'

# Create client
echo "Creating client: $CLIENT_ID"
curl -s -X POST "$KEYCLOAK_URL/admin/realms/$REALM_NAME/clients" \
    -H "Authorization: Bearer $ADMIN_TOKEN" \
    -H "Content-Type: application/json" \
    -d '{
        "clientId": "'$CLIENT_ID'",
        "enabled": true,
        "publicClient": true,
        "standardFlowEnabled": true,
        "implicitFlowEnabled": false,
        "directAccessGrantsEnabled": false,
        "serviceAccountsEnabled": false,
        "redirectUris": [
            "http://localhost:3000/api/auth/callback/keycloak",
            "http://localhost:3000/*"
        ],
        "webOrigins": [
            "http://localhost:3000"
        ],
        "protocol": "openid-connect",
        "attributes": {
            "access.token.lifespan": "300",
            "client.session.idle.timeout": "1800",
            "client.session.max.lifespan": "36000"
        }
    }'

# Create test user
echo "Creating test user..."
curl -s -X POST "$KEYCLOAK_URL/admin/realms/$REALM_NAME/users" \
    -H "Authorization: Bearer $ADMIN_TOKEN" \
    -H "Content-Type: application/json" \
    -d '{
        "username": "testuser",
        "email": "test@mfinance.com",
        "firstName": "Test",
        "lastName": "User",
        "enabled": true,
        "emailVerified": true,
        "credentials": [{
            "type": "password",
            "value": "testpass123",
            "temporary": false
        }]
    }'

echo "Keycloak setup completed!"
echo "Realm: $REALM_NAME"
echo "Client ID: $CLIENT_ID"
echo "Test user: testuser / testpass123"
echo "Keycloak URL: $KEYCLOAK_URL/realms/$REALM_NAME"
