# Clinks Authentication System - Complete Documentation

**Author:** Bharath Reddy  
**Date:** February 12, 2026  
**Status:** For Review by Sushant Sarvade  
**Deadline:** Saturday (Implementation)

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [System Architecture Overview](#2-system-architecture-overview)
3. [Current Authentication System](#3-current-authentication-system)
4. [Database Schema](#4-database-schema)
5. [API Endpoints](#5-api-endpoints)
6. [Firebase Parallel Integration](#6-firebase-parallel-integration)
7. [Implementation Code](#7-implementation-code)
8. [Data Flow Diagrams](#8-data-flow-diagrams)
9. [Implementation Roadmap](#9-implementation-roadmap)
10. [Security Considerations](#10-security-considerations)

---

## 1. Executive Summary

This document provides a complete overview of the Clinks authentication system, covering both **frontend (React)** and **backend (Django)** components, along with the plan to add **Google Firebase authentication running in parallel** with the existing email/password system.

### Key Points

| Aspect | Current State | After Firebase Integration |
|--------|---------------|----------------------------|
| Login Methods | Email/Password only | Email/Password **AND** Google Sign-In |
| User Choice | Single option | User chooses preferred method |
| Existing Users | Email/password login | Can link Google account OR continue with email/password |
| New Users | Must create password | Can sign up with Google OR create password |

### The Parallel Approach

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    PARALLEL AUTHENTICATION SYSTEM                            │
│                                                                              │
│    ┌───────────────────────────────────────────────────────────────────┐    │
│    │                       LOGIN SCREEN                                 │    │
│    │                                                                    │    │
│    │   ┌─────────────────────────────────────────────────────────┐     │    │
│    │   │  Email: [________________________]                      │     │    │
│    │   │  Password: [____________________]                       │     │    │
│    │   │                                                         │     │    │
│    │   │  [        Sign In with Email         ]  ◄── OPTION 1    │     │    │
│    │   └─────────────────────────────────────────────────────────┘     │    │
│    │                                                                    │    │
│    │                        ────── OR ──────                            │    │
│    │                                                                    │    │
│    │   ┌─────────────────────────────────────────────────────────┐     │    │
│    │   │  [G]  Sign in with Google            ]  ◄── OPTION 2    │     │    │
│    │   └─────────────────────────────────────────────────────────┘     │    │
│    │                                                                    │    │
│    └───────────────────────────────────────────────────────────────────┘    │
│                                                                              │
│    Both options lead to the SAME result:                                     │
│    ✓ JWT tokens (access + refresh)                                           │
│    ✓ User session                                                            │
│    ✓ Access to dashboard                                                     │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. System Architecture Overview

### 2.1 Full Stack Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        CLINKS AUTHENTICATION ARCHITECTURE                    │
└─────────────────────────────────────────────────────────────────────────────┘

                              ┌──────────────────┐
                              │   USER BROWSER   │
                              │   / MOBILE APP   │
                              └────────┬─────────┘
                                       │
                    ┌──────────────────┴──────────────────┐
                    │                                      │
                    ▼                                      ▼
┌───────────────────────────────────┐   ┌───────────────────────────────────┐
│        OPTION 1: EMAIL/PASSWORD    │   │      OPTION 2: GOOGLE FIREBASE    │
│                                    │   │                                    │
│  ┌──────────────────────────────┐  │   │  ┌──────────────────────────────┐  │
│  │        Login.js              │  │   │  │      Firebase SDK            │  │
│  │                              │  │   │  │                              │  │
│  │  - Email input               │  │   │  │  - signInWithPopup()         │  │
│  │  - Password input            │  │   │  │  - GoogleAuthProvider()      │  │
│  │  - Submit to API             │  │   │  │  - Get Firebase ID token     │  │
│  └──────────────┬───────────────┘  │   │  └──────────────┬───────────────┘  │
│                 │                   │   │                 │                   │
│                 ▼                   │   │                 ▼                   │
│  ┌──────────────────────────────┐  │   │  ┌──────────────────────────────┐  │
│  │   POST /user/login           │  │   │  │   POST /user/google-auth     │  │
│  │   {email, password}          │  │   │  │   {firebase_token}           │  │
│  └──────────────┬───────────────┘  │   │  └──────────────┬───────────────┘  │
└─────────────────┼───────────────────┘   └─────────────────┼───────────────────┘
                  │                                          │
                  └────────────────────┬─────────────────────┘
                                       │
                                       ▼
                    ┌──────────────────────────────────────┐
                    │           CLINKS BACKEND API          │
                    │            (Django REST)              │
                    │                                       │
                    │  ┌────────────────────────────────┐   │
                    │  │       SAME USER TABLE          │   │
                    │  │                                │   │
                    │  │  - id                          │   │
                    │  │  - email                       │   │
                    │  │  - password (hashed)           │   │
                    │  │  - google_uid (NEW - nullable) │   │
                    │  │  - role                        │   │
                    │  │  - ...                         │   │
                    │  └────────────────────────────────┘   │
                    │                                       │
                    │  ┌────────────────────────────────┐   │
                    │  │     SAME JWT TOKEN SYSTEM      │   │
                    │  │                                │   │
                    │  │  Token.create(user)            │   │
                    │  │  → {access, refresh}           │   │
                    │  └────────────────────────────────┘   │
                    │                                       │
                    └──────────────────────────────────────┘
                                       │
                                       ▼
                    ┌──────────────────────────────────────┐
                    │          SAME RESPONSE FORMAT         │
                    │                                       │
                    │  {                                    │
                    │    "tokens": {                        │
                    │      "access": "eyJ...",              │
                    │      "refresh": "eyJ..."              │
                    │    },                                 │
                    │    "admin": { user_data }             │
                    │  }                                    │
                    └──────────────────────────────────────┘
```

### 2.2 Project File Structure

```
FRONTEND (clinks-Admin-Web)              BACKEND (clinks-Api)
═══════════════════════════              ═════════════════════

src/                                     clinks-Api/
├── pages/                               ├── clinks/
│   └── Login.js ◄── ADD GOOGLE BTN      │   └── settings.py ◄── JWT CONFIG
│                                        │
├── utils/                               ├── api/
│   ├── AuthManager.js ◄── ADD           │   ├── user/
│   │   googleSignIn() method            │   │   ├── models.py ◄── ADD google_uid
│   ├── FetchHelper.js                   │   │   ├── views.py ◄── ADD GoogleAuth
│   └── AsyncStorage.js                  │   │   ├── urls.py ◄── ADD /google-auth
│                                        │   │   └── serializers.py
├── config/                              │   │
│   └── firebase.js ◄── NEW FILE         │   ├── admin/
│                                        │   ├── customer/
├── constants/                           │   └── utils/
│   └── Api.js ◄── ADD GoogleAuth URL    │       └── Token.py
│                                        │
└── components/                          └── clinks-1f1c7-firebase-adminsdk-*.json
    ├── AuthenticatedRoute.js                ◄── FIREBASE SERVICE ACCOUNT
    └── UnauthenticatedRoute.js                  (already exists!)
```

---

## 3. Current Authentication System

### 3.1 How It Works Today

#### Frontend (React)

| Component | File | Purpose |
|-----------|------|---------|
| Login UI | `src/pages/Login.js` | Form for email/password input |
| Auth Logic | `src/utils/AuthManager.js` | Handles login API calls, token storage |
| HTTP Client | `src/utils/FetchHelper.js` | Makes API requests with auth headers |
| Storage | `src/utils/AsyncStorage.js` | Wrapper for localStorage |

#### Backend (Django)

| Component | File | Purpose |
|-----------|------|---------|
| User Model | `api/user/models.py` | User table definition |
| Auth Views | `api/user/views.py` | Login, Logout, Refresh endpoints |
| Token Creation | `api/utils/Token.py` | JWT token generation |
| Settings | `clinks/settings.py` | JWT configuration |

### 3.2 Current Login Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                     CURRENT EMAIL/PASSWORD LOGIN FLOW                        │
└─────────────────────────────────────────────────────────────────────────────┘

  User              Frontend                    Backend                  Database
   │                   │                           │                        │
   │  Enter email      │                           │                        │
   │  & password       │                           │                        │
   │──────────────────▶│                           │                        │
   │                   │                           │                        │
   │                   │  POST /user/login         │                        │
   │                   │  {email, password}        │                        │
   │                   │──────────────────────────▶│                        │
   │                   │                           │                        │
   │                   │                           │  SELECT * FROM user    │
   │                   │                           │  WHERE email = ?       │
   │                   │                           │───────────────────────▶│
   │                   │                           │◀───────────────────────│
   │                   │                           │                        │
   │                   │                           │  check_password()      │
   │                   │                           │  (bcrypt verify)       │
   │                   │                           │                        │
   │                   │                           │  check_if_user_active()│
   │                   │                           │                        │
   │                   │                           │  Token.create(user)    │
   │                   │                           │  (JWT generation)      │
   │                   │                           │                        │
   │                   │◀──────────────────────────│                        │
   │                   │  {tokens, admin}          │                        │
   │                   │                           │                        │
   │                   │  Store tokens in          │                        │
   │                   │  localStorage             │                        │
   │                   │                           │                        │
   │◀──────────────────│                           │                        │
   │  Redirect to      │                           │                        │
   │  Dashboard        │                           │                        │
```

### 3.3 JWT Token Configuration

```python
# clinks/settings.py

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': datetime.timedelta(weeks=2),    # 14 days
    'REFRESH_TOKEN_LIFETIME': datetime.timedelta(weeks=52),  # 1 year
    'ROTATE_REFRESH_TOKENS': True,                           # New refresh each time
    'BLACKLIST_AFTER_ROTATION': True                         # Old token invalidated
}

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
}
```

---

## 4. Database Schema

### 4.1 Current User Model

```python
# api/user/models.py

class User(AbstractBaseUser, PermissionsMixin):
    id = models.AutoField(primary_key=True)
    role = EnumField(options=['admin', 'customer', 'driver', 'company_member'])
    
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email = models.EmailField(max_length=255, unique=True)
    password = models.CharField(max_length=255)              # Hashed
    
    # Status & Verification
    status = EnumField(default='active')                     # active, suspended, deleted
    verification_code = models.CharField(max_length=5, null=True)
    email_verified = models.BooleanField(default=False)
    
    # Contact
    phone_country_code = models.CharField(max_length=255, null=True)
    phone_number = models.CharField(max_length=255, null=True)
    date_of_birth = models.DateField(null=True)
    
    # Timestamps
    last_seen = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    # ═══════════════════════════════════════════════════════════════
    # NEW FIELD FOR GOOGLE INTEGRATION (to be added)
    # ═══════════════════════════════════════════════════════════════
    # google_uid = models.CharField(max_length=255, null=True, unique=True)
```

### 4.2 Updated Schema with Google UID

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         USER TABLE (Updated)                                 │
└─────────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────────┐
│  api_user                                                                    │
├──────────────────────────────────────────────────────────────────────────────┤
│  id             │ INT          │ PRIMARY KEY, AUTO INCREMENT                 │
│  email          │ VARCHAR(255) │ UNIQUE, NOT NULL                            │
│  password       │ VARCHAR(255) │ NOT NULL (hashed)                           │
│  google_uid     │ VARCHAR(255) │ UNIQUE, NULLABLE  ◄── NEW FIELD             │
│  first_name     │ VARCHAR(255) │ NOT NULL                                    │
│  last_name      │ VARCHAR(255) │ NOT NULL                                    │
│  role           │ ENUM         │ admin/customer/driver/company_member        │
│  status         │ ENUM         │ active/suspended/deleted                    │
│  email_verified │ BOOLEAN      │ DEFAULT FALSE                               │
│  ...            │              │                                             │
└──────────────────────────────────────────────────────────────────────────────┘

                              USER SCENARIOS
                              ══════════════

┌─────────────────────────────────────────────────────────────────────────────┐
│  SCENARIO 1: Email/Password Only User                                        │
│  ─────────────────────────────────────                                       │
│  email: john@example.com                                                     │
│  password: $2b$12$... (hashed)                                               │
│  google_uid: NULL                                                            │
│                                                                              │
│  → Can only login with email/password                                        │
│  → Can link Google account later                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│  SCENARIO 2: Google Only User                                                │
│  ────────────────────────────                                                │
│  email: jane@gmail.com                                                       │
│  password: $2b$12$... (random, not used)                                     │
│  google_uid: "abc123xyz789"                                                  │
│                                                                              │
│  → Can only login with Google                                                │
│  → Can set password later for email login                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│  SCENARIO 3: Both Methods Linked                                             │
│  ───────────────────────────────                                             │
│  email: bob@example.com                                                      │
│  password: $2b$12$... (user's password)                                      │
│  google_uid: "def456uvw012"                                                  │
│                                                                              │
│  → Can login with EITHER method                                              │
│  → Same account, same data                                                   │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 4.3 Role-Based Tables

```
                              ┌─────────────┐
                              │    User     │
                              │   (Base)    │
                              └──────┬──────┘
                                     │ 1:1 relationship
           ┌────────────────┬────────┼────────┬─────────────────┐
           │                │        │        │                 │
           ▼                ▼        ▼        ▼                 ▼
     ┌──────────┐    ┌──────────┐ ┌────────┐ ┌──────────────┐
     │  Admin   │    │ Customer │ │ Driver │ │CompanyMember │
     │          │    │          │ │        │ │              │
     │ role:    │    │ stripe_  │ │ vehicle│ │ company_id   │
     │ admin/   │    │ customer │ │        │ │              │
     │ staff    │    │ _id      │ │ license│ │ role:        │
     │          │    │          │ │        │ │ admin/staff  │
     │          │    │ address  │ │ status │ │              │
     │          │    │          │ │        │ │              │
     └──────────┘    └──────────┘ └────────┘ └──────────────┘
```

---

## 5. API Endpoints

### 5.1 Current Endpoints

| Endpoint | Method | Auth Required | Purpose |
|----------|--------|---------------|---------|
| `/user/login` | POST | No | Email/password login |
| `/user/logout` | POST | Yes | Invalidate tokens |
| `/user/refresh-token` | POST | No | Get new tokens |
| `/user/info` | GET | Yes | Get current user |
| `/user/request-reset-password` | POST | No | Request reset code |
| `/user/reset-password` | POST | No | Reset password |
| `/customers` | POST | No | Customer signup |

### 5.2 New Endpoint for Google Auth

| Endpoint | Method | Auth Required | Purpose |
|----------|--------|---------------|---------|
| `/user/google-auth` | POST | No | **NEW** - Google login/signup |
| `/user/google-auth-customer` | POST | No | **NEW** - Customer Google signup |

### 5.3 Endpoint Specifications

#### POST /user/login (Existing)

```json
// Request
{
  "email": "user@example.com",
  "password": "SecurePass123!"
}

// Response (200 OK)
{
  "tokens": {
    "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
  },
  "admin": {
    "user": {
      "id": 1,
      "first_name": "John",
      "last_name": "Doe",
      "email": "user@example.com",
      "role": "admin"
    },
    "role": "admin"
  }
}
```

#### POST /user/google-auth (NEW)

```json
// Request
{
  "firebase_token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9..."
}

// Response (200 OK) - SAME FORMAT AS /user/login
{
  "tokens": {
    "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
  },
  "admin": {
    "user": {
      "id": 1,
      "first_name": "John",
      "last_name": "Doe",
      "email": "user@gmail.com",
      "role": "admin"
    },
    "role": "admin"
  }
}

// Error Response (401)
{
  "error": "Invalid Firebase token"
}

// Error Response (403)
{
  "error": "Only admin accounts can access this portal"
}
```

---

## 6. Firebase Parallel Integration

### 6.1 How Firebase Works in Parallel

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    PARALLEL AUTH: BOTH METHODS AVAILABLE                     │
└─────────────────────────────────────────────────────────────────────────────┘

                         USER CHOOSES LOGIN METHOD
                                    │
                    ┌───────────────┴───────────────┐
                    │                               │
                    ▼                               ▼
        ┌───────────────────────┐       ┌───────────────────────┐
        │   EMAIL/PASSWORD      │       │   GOOGLE SIGN-IN      │
        │   (Existing Flow)     │       │   (New Flow)          │
        └───────────┬───────────┘       └───────────┬───────────┘
                    │                               │
                    │                               │  1. Firebase SDK
                    │                               │     signInWithPopup()
                    │                               │
                    │                               │  2. Google OAuth
                    │                               │     (handled by Google)
                    │                               │
                    │                               │  3. Get Firebase ID Token
                    │                               │     user.getIdToken()
                    │                               │
                    ▼                               ▼
        ┌───────────────────────┐       ┌───────────────────────┐
        │  POST /user/login     │       │  POST /user/google-   │
        │  {email, password}    │       │  auth                 │
        │                       │       │  {firebase_token}     │
        └───────────┬───────────┘       └───────────┬───────────┘
                    │                               │
                    │                               │  Backend verifies
                    │                               │  token with Firebase
                    │                               │  Admin SDK
                    │                               │
                    └───────────────┬───────────────┘
                                    │
                                    ▼
                    ┌───────────────────────────────┐
                    │      SAME USER TABLE          │
                    │                               │
                    │  - Find user by email         │
                    │  - OR find by google_uid      │
                    │  - Create if not exists       │
                    │  - Link accounts if needed    │
                    │                               │
                    └───────────────┬───────────────┘
                                    │
                                    ▼
                    ┌───────────────────────────────┐
                    │     SAME TOKEN GENERATION     │
                    │                               │
                    │  Token.create(user)           │
                    │  → JWT access + refresh       │
                    │                               │
                    └───────────────┬───────────────┘
                                    │
                                    ▼
                    ┌───────────────────────────────┐
                    │     SAME RESPONSE FORMAT      │
                    │     SAME SESSION HANDLING     │
                    │     SAME DASHBOARD ACCESS     │
                    └───────────────────────────────┘
```

### 6.2 Account Linking Logic

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        ACCOUNT LINKING SCENARIOS                             │
└─────────────────────────────────────────────────────────────────────────────┘

SCENARIO A: New User Signs Up with Google
──────────────────────────────────────────

  Google provides: { email: "new@gmail.com", name: "Jane Doe", uid: "google123" }
  
  1. Check: User with email "new@gmail.com" exists? → NO
  2. Check: User with google_uid "google123" exists? → NO
  3. Action: CREATE new user
     - email = "new@gmail.com"
     - first_name = "Jane"
     - last_name = "Doe"
     - google_uid = "google123"
     - password = random (not used)
     - email_verified = true (Google verified it)


SCENARIO B: Existing Email User Signs In with Google (Same Email)
──────────────────────────────────────────────────────────────────

  Existing user: { email: "john@gmail.com", password: "hashed", google_uid: NULL }
  Google provides: { email: "john@gmail.com", uid: "google456" }
  
  1. Check: User with email "john@gmail.com" exists? → YES
  2. Action: LINK Google account
     - UPDATE google_uid = "google456"
     - User can now login with EITHER method


SCENARIO C: Returning Google User
──────────────────────────────────

  Existing user: { email: "bob@gmail.com", google_uid: "google789" }
  Google provides: { email: "bob@gmail.com", uid: "google789" }
  
  1. Check: User with google_uid "google789" exists? → YES
  2. Action: Just LOG IN (no changes needed)


SCENARIO D: Email Used by Different Account (Edge Case)
────────────────────────────────────────────────────────

  Existing user: { email: "admin@company.com", password: "hashed", google_uid: "googleAAA" }
  New Google login: { email: "admin@company.com", uid: "googleBBB" }
  
  1. Check: email matches but google_uid different
  2. Action: REJECT - Account already linked to different Google account
     OR: Allow re-linking (security decision)
```

### 6.3 Firebase Service Account (Already Exists!)

```
File: clinks-1f1c7-firebase-adminsdk-odhg6-3bf322a88e.json

{
  "type": "service_account",
  "project_id": "clinks-1f1c7",
  "client_email": "firebase-adminsdk-odhg6@clinks-1f1c7.iam.gserviceaccount.com",
  ...
}

⚠️ SECURITY: Move this to environment variable before production!
```

---

## 7. Implementation Code

### 7.1 Backend Changes

#### Step 1: Add google_uid to User Model

```python
# api/user/models.py

class User(AbstractBaseUser, PermissionsMixin):
    # ... existing fields ...
    
    # ADD THIS FIELD
    google_uid = models.CharField(max_length=255, null=True, blank=True, unique=True)
```

#### Step 2: Create Migration

```bash
python manage.py makemigrations --name add_google_uid_to_user
python manage.py migrate
```

#### Step 3: Add GoogleAuth View

```python
# api/user/views.py - ADD this new view

import firebase_admin
from firebase_admin import credentials, auth as firebase_auth
import uuid
import os

# Initialize Firebase Admin SDK (once at module load)
if not firebase_admin._apps:
    # Use the existing service account file
    cred_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
        'clinks-1f1c7-firebase-adminsdk-odhg6-3bf322a88e.json'
    )
    cred = credentials.Certificate(cred_path)
    firebase_admin.initialize_app(cred)


class GoogleAuth(SmartAPIView):
    """
    Google Firebase Authentication - Works PARALLEL to email/password login.
    
    This endpoint:
    1. Accepts a Firebase ID token from the frontend
    2. Verifies it using Firebase Admin SDK
    3. Creates new user OR links existing user
    4. Returns the SAME JWT tokens as /user/login
    """
    
    def post(self, request):
        firebase_token = request.data.get('firebase_token')
        
        if not firebase_token:
            return self.respond_with(
                "Firebase token is required",
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # ═══════════════════════════════════════════════════════════
            # STEP 1: Verify Firebase Token (secure - done on backend)
            # ═══════════════════════════════════════════════════════════
            decoded_token = firebase_auth.verify_id_token(firebase_token)
            
            google_uid = decoded_token['uid']
            email = decoded_token.get('email')
            name = decoded_token.get('name', '')
            email_verified = decoded_token.get('email_verified', False)
            
            if not email:
                return self.respond_with(
                    "Email not provided by Google",
                    status_code=status.HTTP_400_BAD_REQUEST
                )
            
            # Split name into first/last
            name_parts = name.split(' ', 1)
            first_name = name_parts[0] if name_parts else 'User'
            last_name = name_parts[1] if len(name_parts) > 1 else ''
            
            # ═══════════════════════════════════════════════════════════
            # STEP 2: Check if User Exists (by email OR google_uid)
            # ═══════════════════════════════════════════════════════════
            user = User.objects.filter(
                Q(email__iexact=email) | Q(google_uid=google_uid)
            ).first()
            
            if user:
                # ───────────────────────────────────────────────────────
                # EXISTING USER - Link Google if not already linked
                # ───────────────────────────────────────────────────────
                if not user.google_uid:
                    user.google_uid = google_uid
                    print(f"Linked Google account to existing user: {email}")
                
                if not user.email_verified and email_verified:
                    user.email_verified = True
                
                user.save()
                check_if_user_active(user)
                
            else:
                # ───────────────────────────────────────────────────────
                # NEW USER - Create account
                # ───────────────────────────────────────────────────────
                user = User.objects.create(
                    email=email,
                    first_name=first_name,
                    last_name=last_name,
                    google_uid=google_uid,
                    password=make_password(str(uuid.uuid4())),  # Random password
                    role=Constants.USER_ROLE_ADMIN,
                    email_verified=email_verified
                )
                
                # Create Admin record
                Admin.objects.create(
                    user=user,
                    role=Constants.ADMIN_ROLE_STAFF
                )
                print(f"Created new admin user via Google: {email}")
            
            # ═══════════════════════════════════════════════════════════
            # STEP 3: Validate User Role (Admin only for admin portal)
            # ═══════════════════════════════════════════════════════════
            if user.role != Constants.USER_ROLE_ADMIN:
                return self.respond_with(
                    "Only admin accounts can access this portal",
                    status_code=status.HTTP_403_FORBIDDEN
                )
            
            try:
                admin = Admin.objects.get(user=user)
            except Admin.DoesNotExist:
                return self.respond_with(
                    "Admin record not found",
                    status_code=status.HTTP_403_FORBIDDEN
                )
            
            # ═══════════════════════════════════════════════════════════
            # STEP 4: Generate JWT Tokens (SAME as /user/login)
            # ═══════════════════════════════════════════════════════════
            data = {}
            data[Constants.USER_ROLE_ADMIN] = AdminDetailSerializer(admin).data
            data[Constants.USER_AUTH_TOKENS] = Token.create(user)
            
            update_last_login(None, user)
            
            return Response(data, status=status.HTTP_200_OK)
            
        except firebase_auth.InvalidIdTokenError:
            return self.respond_with(
                "Invalid Firebase token",
                status_code=status.HTTP_401_UNAUTHORIZED
            )
        except firebase_auth.ExpiredIdTokenError:
            return self.respond_with(
                "Firebase token has expired",
                status_code=status.HTTP_401_UNAUTHORIZED
            )
        except Exception as e:
            print(f"Google auth error: {e}")
            return self.respond_with(
                f"Authentication failed: {str(e)}",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class GoogleAuthCustomer(SmartAPIView):
    """
    Google Firebase Authentication for Customers (Mobile App).
    Requires date_of_birth for new users (age verification).
    """
    
    def post(self, request):
        firebase_token = request.data.get('firebase_token')
        date_of_birth = request.data.get('date_of_birth')  # Required for new users
        
        if not firebase_token:
            return self.respond_with(
                "Firebase token is required",
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Verify Firebase token
            decoded_token = firebase_auth.verify_id_token(firebase_token)
            
            google_uid = decoded_token['uid']
            email = decoded_token.get('email')
            name = decoded_token.get('name', '')
            email_verified = decoded_token.get('email_verified', False)
            
            # Check if user exists
            user = User.objects.filter(
                Q(email__iexact=email) | Q(google_uid=google_uid)
            ).first()
            
            if user:
                # Existing user - link Google if needed
                if not user.google_uid:
                    user.google_uid = google_uid
                user.save()
                check_if_user_active(user)
                
                customer = Customer.objects.get(user=user)
            else:
                # New user - require date_of_birth
                if not date_of_birth:
                    return self.respond_with(
                        "Date of birth is required for new customers",
                        status_code=status.HTTP_400_BAD_REQUEST
                    )
                
                # Age verification
                from datetime import datetime
                dob = datetime.strptime(date_of_birth, '%Y-%m-%d').date()
                if DateUtils.year_difference_to_now(dob) < 18:
                    return self.respond_with(
                        "You must be at least 18 years old",
                        status_code=status.HTTP_400_BAD_REQUEST
                    )
                
                name_parts = name.split(' ', 1)
                first_name = name_parts[0] if name_parts else 'User'
                last_name = name_parts[1] if len(name_parts) > 1 else ''
                
                # Create user
                user = User.objects.create(
                    email=email,
                    first_name=first_name,
                    last_name=last_name,
                    google_uid=google_uid,
                    password=make_password(str(uuid.uuid4())),
                    role=Constants.USER_ROLE_CUSTOMER,
                    email_verified=email_verified,
                    date_of_birth=dob
                )
                
                # Create customer
                customer = Customer.objects.create(user=user)
                
                # Update stats
                from ..all_time_stat.models import AllTimeStat
                AllTimeStat.update(Constants.ALL_TIME_STAT_TYPE_CUSTOMER_COUNT, 1)
            
            # Generate JWT tokens
            data = {}
            data[Constants.CUSTOMER] = CustomerDetailSerializer(customer).data
            data[Constants.USER_AUTH_TOKENS] = Token.create(user)
            
            return Response(data, status=status.HTTP_200_OK)
            
        except firebase_auth.InvalidIdTokenError:
            return self.respond_with(
                "Invalid Firebase token",
                status_code=status.HTTP_401_UNAUTHORIZED
            )
        except Exception as e:
            return self.respond_with(
                str(e),
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
```

#### Step 4: Update URLs

```python
# api/user/urls.py

from .views import (
    DriverLogin,
    Login,
    Logout,
    Refresh,
    Info,
    RequestPasswordReset,
    ResetPassword,
    RequestVerifyEmail,
    VerifyEmail,
    GoogleAuth,           # ADD
    GoogleAuthCustomer    # ADD
)

urlpatterns = [
    path('/driver-login', DriverLogin.as_view()),
    path('/login', Login.as_view()),
    path('/logout', Logout.as_view()),
    path('/refresh-token', Refresh.as_view()),
    path('/info', Info.as_view()),
    path('/request-reset-password', RequestPasswordReset.as_view()),
    path('/reset-password', ResetPassword.as_view()),
    path("/request-verify-email", RequestVerifyEmail.as_view()),
    path("/verify-email", VerifyEmail.as_view()),
    path('/google-auth', GoogleAuth.as_view()),                    # ADD
    path('/google-auth-customer', GoogleAuthCustomer.as_view()),   # ADD
    path('/device/', include(push_notifications_router.urls)),
]
```

#### Step 5: Install Firebase Admin SDK

```bash
pip install firebase-admin
pip freeze > requirements.txt
```

### 7.2 Frontend Changes

#### Step 1: Install Firebase SDK

```bash
npm install firebase
```

#### Step 2: Create Firebase Config

```javascript
// src/config/firebase.js (NEW FILE)

import { initializeApp } from 'firebase/app';
import { getAuth, GoogleAuthProvider } from 'firebase/auth';

const firebaseConfig = {
  apiKey: process.env.REACT_APP_FIREBASE_API_KEY,
  authDomain: process.env.REACT_APP_FIREBASE_AUTH_DOMAIN,
  projectId: process.env.REACT_APP_FIREBASE_PROJECT_ID,
  storageBucket: process.env.REACT_APP_FIREBASE_STORAGE_BUCKET,
  messagingSenderId: process.env.REACT_APP_FIREBASE_MESSAGING_SENDER_ID,
  appId: process.env.REACT_APP_FIREBASE_APP_ID
};

const app = initializeApp(firebaseConfig);
export const auth = getAuth(app);
export const googleProvider = new GoogleAuthProvider();

// Force account selection each time
googleProvider.setCustomParameters({
  prompt: 'select_account'
});
```

#### Step 3: Update API Constants

```javascript
// src/constants/Api.js - ADD this line

window.Api.User.GoogleAuth = window.Api.User.Base + "/google-auth";
```

#### Step 4: Add googleSignIn to AuthManager

```javascript
// src/utils/AuthManager.js - ADD this method

import { signInWithPopup } from 'firebase/auth';
import { auth, googleProvider } from '../config/firebase';

class AuthManager {
  // ... existing code ...

  /**
   * Google Sign-In - Works PARALLEL to email/password login
   * 
   * Flow:
   * 1. Firebase SDK opens Google popup
   * 2. User selects Google account
   * 3. Firebase returns ID token
   * 4. We send token to /user/google-auth
   * 5. Backend verifies and returns JWT tokens
   * 6. Same result as email/password login!
   */
  static async googleSignIn() {
    try {
      // Step 1: Sign in with Google via Firebase popup
      const result = await signInWithPopup(auth, googleProvider);
      
      // Step 2: Get Firebase ID token
      const firebaseToken = await result.user.getIdToken();
      
      // Step 3: Send to our backend for verification
      const response = await FetchHelper.post(
        window.Api.User.GoogleAuth,
        { firebase_token: firebaseToken },
        false,  // not multipart
        false   // don't validate tokens (user not logged in yet)
      );
      
      // Step 4: Handle response (same as regular login)
      if (this._hasError(response)) {
        throw AuthManager.getError(response);
      }
      
      if (!response.admin) {
        throw { 
          error: "invalid user", 
          message: "Only admin accounts can access this portal" 
        };
      }
      
      // Step 5: Store tokens (same as regular login)
      AuthManager._updateTokens(response.tokens);
      AuthManager._setUser(response);
      
      return response;
      
    } catch (error) {
      // Handle Firebase errors
      if (error.code === 'auth/popup-closed-by-user') {
        throw { message: "Sign-in cancelled" };
      }
      if (error.code === 'auth/network-request-failed') {
        throw { message: "Network error. Please try again." };
      }
      throw AuthManager.getError(error);
    }
  }
}
```

#### Step 5: Update Login.js

```javascript
// src/pages/Login.js - ADD Google button

import AuthManager from '../utils/AuthManager';

class Login extends Component {
  // ... existing code ...

  /**
   * Handle Google Sign-In button click
   */
  _handleGoogleSignIn = async (e) => {
    e.preventDefault();
    
    this.setState({ isLoading: true, error: null });
    
    try {
      await AuthManager.googleSignIn();
      
      // Success - redirect to dashboard
      window.location = "/";
      
    } catch (error) {
      this.setState({
        isLoading: false,
        error: error.message || "Google sign-in failed"
      });
    }
  }

  render() {
    const { isLoading } = this.state;
    
    return (
      <div className="login-container">
        {/* Existing email/password form */}
        <form onSubmit={this._handleLogInClicked}>
          <input 
            type="email" 
            placeholder="Email"
            value={this.state.email}
            onChange={(e) => this.setState({ email: e.target.value })}
          />
          <input 
            type="password" 
            placeholder="Password"
            value={this.state.password}
            onChange={(e) => this.setState({ password: e.target.value })}
          />
          <button type="submit" disabled={isLoading}>
            {isLoading ? "Signing in..." : "Sign In"}
          </button>
        </form>

        {/* ═══════════════════════════════════════════════════════════ */}
        {/* DIVIDER - Shows both options are available */}
        {/* ═══════════════════════════════════════════════════════════ */}
        <div className="divider">
          <span>OR</span>
        </div>

        {/* ═══════════════════════════════════════════════════════════ */}
        {/* GOOGLE SIGN-IN BUTTON - NEW */}
        {/* ═══════════════════════════════════════════════════════════ */}
        <button
          type="button"
          className="google-signin-btn"
          onClick={this._handleGoogleSignIn}
          disabled={isLoading}
        >
          <img 
            src="/assets/media/svg/social/google.svg" 
            alt="Google" 
            height="20" 
          />
          Sign in with Google
        </button>

        {/* Error display */}
        {this.state.error && (
          <div className="error-message">
            {this.state.error}
          </div>
        )}
      </div>
    );
  }
}
```

#### Step 6: Add Environment Variables

```env
# .env (frontend)

REACT_APP_API_BASE=https://api.clinks.ie
REACT_APP_FIREBASE_API_KEY=AIzaSy...
REACT_APP_FIREBASE_AUTH_DOMAIN=clinks-1f1c7.firebaseapp.com
REACT_APP_FIREBASE_PROJECT_ID=clinks-1f1c7
REACT_APP_FIREBASE_STORAGE_BUCKET=clinks-1f1c7.appspot.com
REACT_APP_FIREBASE_MESSAGING_SENDER_ID=123456789
REACT_APP_FIREBASE_APP_ID=1:123456789:web:abcdef
```

---

## 8. Data Flow Diagrams

### 8.1 Parallel Login - Both Options

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    COMPLETE LOGIN FLOW - BOTH OPTIONS                        │
└─────────────────────────────────────────────────────────────────────────────┘

                              USER ON LOGIN PAGE
                                      │
                   ┌──────────────────┴──────────────────┐
                   │                                      │
                   ▼                                      ▼
        ┌─────────────────────┐              ┌─────────────────────┐
        │  OPTION 1           │              │  OPTION 2           │
        │  Email/Password     │              │  Google Sign-In     │
        │                     │              │                     │
        │  [Email: ______]    │              │  [G] Sign in with   │
        │  [Pass: ______]     │              │      Google         │
        │  [Sign In]          │              │                     │
        └──────────┬──────────┘              └──────────┬──────────┘
                   │                                     │
                   │                                     │
                   ▼                                     ▼
        ┌─────────────────────┐              ┌─────────────────────┐
        │  Frontend:          │              │  Frontend:          │
        │                     │              │                     │
        │  AuthManager.       │              │  AuthManager.       │
        │  login(email, pass) │              │  googleSignIn()     │
        │                     │              │                     │
        └──────────┬──────────┘              └──────────┬──────────┘
                   │                                     │
                   │                                     │  signInWithPopup()
                   │                                     │  (Firebase SDK)
                   │                                     │
                   │                                     ▼
                   │                          ┌─────────────────────┐
                   │                          │  GOOGLE SERVERS     │
                   │                          │                     │
                   │                          │  - OAuth2 flow      │
                   │                          │  - User consents    │
                   │                          │  - Returns token    │
                   │                          └──────────┬──────────┘
                   │                                     │
                   │                                     │  Firebase ID Token
                   │                                     │
                   ▼                                     ▼
        ┌─────────────────────┐              ┌─────────────────────┐
        │  POST /user/login   │              │  POST /user/        │
        │                     │              │  google-auth        │
        │  {                  │              │                     │
        │    email: "...",    │              │  {                  │
        │    password: "..."  │              │    firebase_token:  │
        │  }                  │              │    "eyJ..."         │
        │                     │              │  }                  │
        └──────────┬──────────┘              └──────────┬──────────┘
                   │                                     │
                   │                                     │
                   ▼                                     ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│                              CLINKS BACKEND                                   │
│                                                                               │
│  ┌───────────────────────────┐         ┌───────────────────────────┐         │
│  │  Login View               │         │  GoogleAuth View          │         │
│  │                           │         │                           │         │
│  │  1. Get user by email     │         │  1. Verify Firebase token │         │
│  │  2. check_password()      │         │  2. Get user by email     │         │
│  │  3. check_if_user_active()│         │     OR google_uid         │         │
│  │  4. get_detailed(user)    │         │  3. Create/link user      │         │
│  │  5. Token.create(user)    │         │  4. check_if_user_active()│         │
│  │                           │         │  5. get_detailed(user)    │         │
│  │                           │         │  6. Token.create(user)    │         │
│  └─────────────┬─────────────┘         └─────────────┬─────────────┘         │
│                │                                      │                       │
│                └──────────────────┬───────────────────┘                       │
│                                   │                                           │
│                                   ▼                                           │
│                    ┌─────────────────────────────┐                            │
│                    │     SAME USER TABLE         │                            │
│                    │     SAME JWT GENERATION     │                            │
│                    │     SAME RESPONSE FORMAT    │                            │
│                    └─────────────────────────────┘                            │
│                                                                               │
└────────────────────────────────────┬──────────────────────────────────────────┘
                                     │
                                     ▼
                      ┌─────────────────────────────┐
                      │     RESPONSE                │
                      │                             │
                      │  {                          │
                      │    "tokens": {              │
                      │      "access": "eyJ...",    │
                      │      "refresh": "eyJ..."    │
                      │    },                       │
                      │    "admin": { ... }         │
                      │  }                          │
                      │                             │
                      └─────────────┬───────────────┘
                                    │
                                    ▼
                      ┌─────────────────────────────┐
                      │     FRONTEND                │
                      │                             │
                      │  - Store in localStorage    │
                      │  - Set AuthManager state    │
                      │  - Redirect to dashboard    │
                      │                             │
                      └─────────────────────────────┘
```

### 8.2 New User Google Sign-Up

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    NEW USER - GOOGLE SIGN-UP                                 │
└─────────────────────────────────────────────────────────────────────────────┘

  New User             Frontend              Google             Backend
     │                    │                    │                   │
     │  Click "Sign in    │                    │                   │
     │  with Google"      │                    │                   │
     │───────────────────▶│                    │                   │
     │                    │                    │                   │
     │                    │  signInWithPopup() │                   │
     │                    │───────────────────▶│                   │
     │                    │                    │                   │
     │───────────────────────────────────────▶│                   │
     │  Select Google account                  │                   │
     │  (popup window)    │                    │                   │
     │◀───────────────────────────────────────│                   │
     │  Consent granted   │                    │                   │
     │                    │                    │                   │
     │                    │◀───────────────────│                   │
     │                    │  Firebase token    │                   │
     │                    │                    │                   │
     │                    │  POST /user/google-auth                │
     │                    │  {firebase_token}  │                   │
     │                    │────────────────────────────────────────▶
     │                    │                    │                   │
     │                    │                    │   firebase_auth.  │
     │                    │                    │   verify_id_token()
     │                    │                    │                   │
     │                    │                    │   Decoded:        │
     │                    │                    │   - email         │
     │                    │                    │   - name          │
     │                    │                    │   - google_uid    │
     │                    │                    │                   │
     │                    │                    │   User NOT found  │
     │                    │                    │   → CREATE new:   │
     │                    │                    │   - User record   │
     │                    │                    │   - Admin record  │
     │                    │                    │                   │
     │                    │                    │   Token.create()  │
     │                    │                    │                   │
     │                    │◀────────────────────────────────────────
     │                    │  {tokens, admin}   │                   │
     │                    │                    │                   │
     │                    │  Store tokens      │                   │
     │◀───────────────────│                    │                   │
     │  Redirect to       │                    │                   │
     │  Dashboard         │                    │                   │
```

### 8.3 Existing User Links Google Account

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    EXISTING USER LINKS GOOGLE ACCOUNT                        │
└─────────────────────────────────────────────────────────────────────────────┘

Existing user: john@gmail.com (password login only)

  User                 Frontend              Google             Backend
     │                    │                    │                   │
     │  Click "Sign in    │                    │                   │
     │  with Google"      │                    │                   │
     │  (same email)      │                    │                   │
     │───────────────────▶│                    │                   │
     │                    │                    │                   │
     │                    │  signInWithPopup() │                   │
     │                    │───────────────────▶│                   │
     │                    │                    │                   │
     │                    │◀───────────────────│                   │
     │                    │  Firebase token    │                   │
     │                    │                    │                   │
     │                    │  POST /user/google-auth                │
     │                    │  {firebase_token}  │                   │
     │                    │────────────────────────────────────────▶
     │                    │                    │                   │
     │                    │                    │   Verify token    │
     │                    │                    │                   │
     │                    │                    │   Email: john@    │
     │                    │                    │   gmail.com       │
     │                    │                    │                   │
     │                    │                    │   User FOUND by   │
     │                    │                    │   email!          │
     │                    │                    │                   │
     │                    │                    │   google_uid is   │
     │                    │                    │   NULL → UPDATE   │
     │                    │                    │   to link account │
     │                    │                    │                   │
     │                    │                    │   Token.create()  │
     │                    │                    │                   │
     │                    │◀────────────────────────────────────────
     │                    │  {tokens, admin}   │                   │
     │                    │                    │                   │
     │◀───────────────────│                    │                   │
     │  Success!          │                    │                   │
     │  Now can use       │                    │                   │
     │  EITHER method     │                    │                   │

RESULT: User can now login with:
✓ Email + Password (existing method)
✓ Google Sign-In (newly linked)
```

---

## 9. Implementation Roadmap

### Timeline: 3 Days (Complete by Saturday)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        IMPLEMENTATION TIMELINE                               │
└─────────────────────────────────────────────────────────────────────────────┘

DAY 1 (Thursday) - BACKEND
═══════════════════════════

  Morning (2 hours)
  ─────────────────
  □ Install firebase-admin: pip install firebase-admin
  □ Update requirements.txt
  □ Add google_uid field to User model
  □ Create and run migration

  Afternoon (3 hours)
  ───────────────────
  □ Create GoogleAuth view
  □ Create GoogleAuthCustomer view
  □ Add URL routes
  □ Test with Postman/curl


DAY 2 (Friday) - FRONTEND
═══════════════════════════

  Morning (2 hours)
  ─────────────────
  □ Install Firebase SDK: npm install firebase
  □ Create firebase.js config
  □ Add Firebase environment variables
  □ Update Api.js with GoogleAuth endpoint

  Afternoon (3 hours)
  ───────────────────
  □ Add googleSignIn() to AuthManager.js
  □ Update Login.js with Google button
  □ Add styling for Google button
  □ Test locally


DAY 3 (Saturday) - TESTING & DEPLOYMENT
═════════════════════════════════════════

  Morning (2 hours)
  ─────────────────
  □ Integration testing (frontend + backend)
  □ Test all scenarios:
    - New user Google signup
    - Existing user Google login
    - Account linking
    - Error handling

  Afternoon (2 hours)
  ───────────────────
  □ Deploy backend to server
  □ Deploy frontend
  □ End-to-end testing on production
  □ Bug fixes if needed

  ┌───────────────────────────────────────┐
  │  ✓ LIVE BY SATURDAY EVENING          │
  └───────────────────────────────────────┘
```

### Detailed Task Checklist

#### Day 1: Backend

| # | Task | Time | Status |
|---|------|------|--------|
| 1 | `pip install firebase-admin` | 5 min | ⬜ |
| 2 | Update `requirements.txt` | 5 min | ⬜ |
| 3 | Add `google_uid` to User model | 10 min | ⬜ |
| 4 | Run `python manage.py makemigrations` | 5 min | ⬜ |
| 5 | Run `python manage.py migrate` | 5 min | ⬜ |
| 6 | Add Firebase initialization | 20 min | ⬜ |
| 7 | Create `GoogleAuth` view | 45 min | ⬜ |
| 8 | Create `GoogleAuthCustomer` view | 30 min | ⬜ |
| 9 | Update `urls.py` | 10 min | ⬜ |
| 10 | Test with curl/Postman | 30 min | ⬜ |

#### Day 2: Frontend

| # | Task | Time | Status |
|---|------|------|--------|
| 1 | `npm install firebase` | 5 min | ⬜ |
| 2 | Create `src/config/firebase.js` | 15 min | ⬜ |
| 3 | Add Firebase env variables | 10 min | ⬜ |
| 4 | Update `src/constants/Api.js` | 5 min | ⬜ |
| 5 | Add `googleSignIn()` to AuthManager | 30 min | ⬜ |
| 6 | Update Login.js with Google button | 30 min | ⬜ |
| 7 | Add CSS for Google button | 15 min | ⬜ |
| 8 | Test locally | 30 min | ⬜ |

#### Day 3: Testing & Deployment

| # | Task | Time | Status |
|---|------|------|--------|
| 1 | Test: New user Google signup | 15 min | ⬜ |
| 2 | Test: Existing user Google login | 15 min | ⬜ |
| 3 | Test: Account linking | 15 min | ⬜ |
| 4 | Test: Email/password still works | 10 min | ⬜ |
| 5 | Test: Error scenarios | 20 min | ⬜ |
| 6 | Deploy backend | 30 min | ⬜ |
| 7 | Deploy frontend | 20 min | ⬜ |
| 8 | Production testing | 30 min | ⬜ |
| 9 | Fix any issues | 30 min | ⬜ |

---

## 10. Security Considerations

### 10.1 Token Security

| Concern | Mitigation |
|---------|------------|
| Firebase token verification | ALWAYS verify on backend, never trust frontend |
| JWT storage | localStorage (consider httpOnly cookies for production) |
| Token lifetime | Access: 2 weeks, Refresh: 1 year |
| Token rotation | Enabled - refresh tokens rotate |
| Blacklisting | Enabled - old tokens invalidated |

### 10.2 Firebase Service Account

```
⚠️ IMPORTANT: Move service account to environment variable!

CURRENT (not secure for production):
  - File: clinks-1f1c7-firebase-adminsdk-odhg6-3bf322a88e.json
  - Location: Project root

RECOMMENDED (production):
  - Store as environment variable
  - Use secret manager (AWS Secrets, Google Secret Manager)
  - Never commit to git
```

### 10.3 Account Security

| Scenario | Handling |
|----------|----------|
| User with same email exists | Link Google account to existing user |
| Google account already linked to different user | Reject (or prompt for account merge) |
| User tries to login without approved role | Return 403 Forbidden |
| Inactive/suspended user | Return 403 with "account inactive" |

### 10.4 HTTPS Requirements

```
ALL authentication endpoints MUST use HTTPS in production:

✓ POST /user/login           (existing)
✓ POST /user/google-auth     (new)
✓ POST /user/refresh-token   (existing)

Firebase tokens contain sensitive data and must be transmitted securely.
```

---

## Appendix A: Environment Variables

### Backend (.env)

```env
# Existing
GENERAL_SECRET_KEY=your-django-secret-key
GENERAL_DEBUG=False
DATABASE_ENGINE=django.db.backends.postgresql
DATABASE_NAME=clinks
DATABASE_USER=clinks_user
DATABASE_PASSWORD=secure_password
DATABASE_HOST=localhost
DATABASE_PORT=5432

# Firebase (recommended for production)
FIREBASE_CREDENTIALS_PATH=/secure/path/to/service-account.json
# OR as JSON string:
# FIREBASE_CREDENTIALS_JSON='{"type":"service_account",...}'
```

### Frontend (.env)

```env
# Existing
REACT_APP_API_BASE=https://api.clinks.ie

# Firebase (get from Firebase Console → Project Settings)
REACT_APP_FIREBASE_API_KEY=AIzaSy...
REACT_APP_FIREBASE_AUTH_DOMAIN=clinks-1f1c7.firebaseapp.com
REACT_APP_FIREBASE_PROJECT_ID=clinks-1f1c7
REACT_APP_FIREBASE_STORAGE_BUCKET=clinks-1f1c7.appspot.com
REACT_APP_FIREBASE_MESSAGING_SENDER_ID=123456789
REACT_APP_FIREBASE_APP_ID=1:123456789:web:abcdef
```

---

## Appendix B: Testing Commands

### Backend Testing

```bash
# Install Firebase Admin
pip install firebase-admin

# Create migration
python manage.py makemigrations api --name add_google_uid_to_user

# Run migration
python manage.py migrate

# Test Google Auth endpoint
curl -X POST http://localhost:8000/user/google-auth \
  -H "Content-Type: application/json" \
  -d '{"firebase_token": "your-firebase-token"}'

# Run unit tests
python manage.py test api.tests.test_google_auth
```

### Frontend Testing

```bash
# Install Firebase
npm install firebase

# Start development server
npm start

# Build for production
npm run build
```

---

## Appendix C: Error Handling

| Error | HTTP Code | User Message |
|-------|-----------|--------------|
| Missing token | 400 | "Firebase token is required" |
| Invalid token | 401 | "Invalid Firebase token" |
| Expired token | 401 | "Firebase token has expired" |
| Not admin | 403 | "Only admin accounts can access this portal" |
| Account inactive | 403 | "Your account is no longer active" |
| Popup closed | - | "Sign-in cancelled" |
| Network error | - | "Network error. Please try again." |

---

## Document Approval

**Prepared By:** Bharath Reddy  
**Date:** February 12, 2026  

**Reviewed By:** ________________  
**Date:** ________________  

**Approved By:** Sushant Sarvade  
**Date:** ________________  

---

*This document outlines both the existing system and the Firebase integration plan. Both authentication methods will work IN PARALLEL - users choose their preferred method. Implementation ready to start upon approval.*
