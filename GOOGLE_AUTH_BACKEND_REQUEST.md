# Google Sign-In — Mobile App Integration Details for Backend

**Date:** February 17, 2026  
**From:** Mobile App Team  
**To:** Backend Team  
**Subject:** Google Sign-In implementation on mobile — endpoint & contract requirements

---

## 1. Overview

We have implemented Google Sign-In on the mobile app (React Native, Android). The mobile app uses **Firebase Authentication** to verify the user's Google account and then sends a **Firebase ID Token** to the backend for session creation.

This document describes exactly what the mobile app sends, what it expects back, and the Firebase project details needed for backend token verification.

---

## 2. Firebase Project Details

The mobile app is configured with the following Firebase project:

| Field              | Value                                      |
|--------------------|---------------------------------------------|
| **Project ID**     | `clinks-915af`                              |
| **Project Number** | `766862456420`                              |
| **Storage Bucket** | `clinks-915af.firebasestorage.app`          |
| **Android Package**| `com.clinksreactnative`                     |
| **API Key**        | `AIzaSyDCRYczvCpGijcr8HCYTxO7ZLa4k1Wgh6g`  |

> **IMPORTANT:** The backend must verify Firebase ID tokens issued by project `clinks-915af`. If the backend currently uses a different Firebase project (e.g., `clinks-372004`), it will need to either:
> - Add `clinks-915af` as an accepted project for token verification, or
> - Share the existing Firebase project credentials so the mobile app can be added to it instead.

---

## 3. Authentication Flow

```
┌──────────┐      ┌──────────┐      ┌──────────┐      ┌──────────┐
│  Mobile   │──1──▶│  Google   │──2──▶│ Firebase │──3──▶│ Backend  │
│   App     │◀─────│  OAuth    │◀─────│   Auth   │      │  Server  │
└──────────┘      └──────────┘      └──────────┘      └──────────┘
```

**Step-by-step:**

1. User taps **"Continue with Google"** on the login screen
2. Google OAuth popup opens → user selects their Google account
3. Mobile app receives a Google ID token
4. Mobile app exchanges the Google ID token for a **Firebase credential**
5. Mobile app signs into Firebase → receives a **Firebase ID Token** (JWT)
6. Mobile app sends the Firebase ID Token to the backend via `POST /user/google-auth-customer`
7. Backend verifies the Firebase ID Token, creates/finds user, and returns JWT session tokens

---

## 4. API Endpoint Contract

### `POST /user/google-auth-customer`

**Full URL:** `{BASE_URL}/user/google-auth-customer`  
**Current Base URL:** `http://10.178.149.11:8000`

---

### 4.1 Request

**Headers:**
```
Content-Type: application/json
```

**Body (JSON):**

```json
{
  "firebase_token": "<Firebase ID Token - JWT string>",
  "date_of_birth": "YYYY-MM-DD"
}
```

| Field             | Type     | Required | Description |
|-------------------|----------|----------|-------------|
| `firebase_token`  | `string` | **Yes**  | Firebase ID Token (JWT) obtained after Google Sign-In via Firebase Auth. The backend should verify this token using Firebase Admin SDK. |
| `date_of_birth`   | `string` | No*      | Date of birth in `YYYY-MM-DD` format. **Required only for new users** (first-time Google sign-in). Optional for returning users. |

> *If `date_of_birth` is required but not provided, the backend should return a `400` response (see section 4.3).

---

### 4.2 Expected Success Response

**Status:** `200 OK`

The response must match the same structure as the existing `POST /user/login` endpoint, so the mobile app can use the same session management logic.

**Expected Body (JSON):**

```json
{
  "tokens": {
    "access": "<JWT access token>",
    "refresh": "<JWT refresh token>"
  },
  "customer": {
    "id": 123,
    "first_name": "John",
    "last_name": "Doe",
    "email": "john@gmail.com",
    "date_of_birth": "1995-06-15",
    ...
  }
}
```

| Field     | Type     | Required | Description |
|-----------|----------|----------|-------------|
| `tokens`  | `object` | **Yes**  | Contains `access` and `refresh` JWT tokens (same format as `/user/login`). |
| `customer`| `object` | **Yes**  | The customer/user profile object (same structure as returned by `/user/login`). |

> The mobile app extracts tokens via `data.tokens` and user info via the existing `AuthManager.config.getUser(data)` method (which reads from the `customer` key or equivalent).

---

### 4.3 Error Responses

#### New User Without Date of Birth

**Status:** `400 Bad Request`

```json
{
  "detail": "Date of birth is required for new customers"
}
```
OR
```json
{
  "message": "Date of birth is required for new customers"
}
```

> When the mobile app receives this response, it will prompt the user to enter their date of birth and then retry the request with `date_of_birth` included.

#### Invalid/Expired Firebase Token

**Status:** `401 Unauthorized`

```json
{
  "detail": "Invalid or expired Firebase token"
}
```

#### General Server Error

**Status:** `500 Internal Server Error`

```json
{
  "detail": "An error occurred during authentication"
}
```

---

## 5. Backend Implementation Requirements

### 5.1 Firebase Token Verification

The backend must verify the `firebase_token` using the **Firebase Admin SDK**:

**Python example:**
```python
import firebase_admin
from firebase_admin import auth as firebase_auth

# Initialize Firebase Admin (do once at startup)
# Use the credentials for project: clinks-915af
cred = firebase_admin.credentials.Certificate("path/to/clinks-915af-serviceAccountKey.json")
firebase_admin.initialize_app(cred)

# Verify the token from the mobile app
def verify_firebase_token(firebase_token):
    decoded_token = firebase_auth.verify_id_token(firebase_token)
    
    uid = decoded_token['uid']           # Firebase UID (unique per user)
    email = decoded_token.get('email')    # User's Google email
    name = decoded_token.get('name')      # User's display name
    picture = decoded_token.get('picture')  # Profile photo URL
    
    return decoded_token
```

### 5.2 User Management Logic

```
IF firebase_token is valid:
    Extract email from decoded token
    
    IF user with this email already exists in DB:
        → Return existing user + new JWT tokens (same as /user/login)
    
    ELSE (new user):
        IF date_of_birth is provided:
            → Create new customer account using Google profile info + date_of_birth
            → Return new user + JWT tokens
        ELSE:
            → Return 400: "Date of birth is required for new customers"
```

### 5.3 Firebase Service Account Key

To verify tokens, the backend needs a **service account key** for the Firebase project `clinks-915af`:

1. Go to [Firebase Console](https://console.firebase.google.com/) → Project `clinks-915af`
2. **Project Settings** → **Service accounts** tab
3. Click **"Generate new private key"**
4. Download the JSON file and use it to initialize Firebase Admin SDK on the backend

---

## 6. Data Available from Firebase Token

When the backend decodes the Firebase ID token, these fields are available:

| Field            | Example                        | Description |
|------------------|--------------------------------|-------------|
| `uid`            | `"abc123def456"`               | Unique Firebase user ID |
| `email`          | `"user@gmail.com"`             | User's Google email (verified) |
| `email_verified` | `true`                         | Always `true` for Google accounts |
| `name`           | `"John Doe"`                   | Display name from Google account |
| `picture`        | `"https://lh3.google..."`      | Profile picture URL |
| `sign_in_provider` | `"google.com"`               | Authentication provider |
| `iss`            | `"https://securetoken.google.com/clinks-915af"` | Token issuer (includes project ID) |

---

## 7. Secondary Endpoint (Optional)

We also have a generic endpoint configured for potential future use:

### `POST /user/google-auth`

Same contract as `/user/google-auth-customer` but for other user types (e.g., drivers). Not currently in use — included here for awareness.

---

## 8. Testing Checklist

- [ ] Backend can verify Firebase ID tokens from project `clinks-915af`
- [ ] `POST /user/google-auth-customer` endpoint is created and accessible
- [ ] Existing users can sign in via Google (returns user + tokens)
- [ ] New users without `date_of_birth` get a `400` response with the correct message
- [ ] New users with `date_of_birth` get created and receive user + tokens
- [ ] Response format matches existing `/user/login` response structure
- [ ] JWT access/refresh tokens work with existing protected endpoints

---

## 9. Questions for Backend Team

1. Is the backend currently using Firebase project `clinks-372004` or `clinks-915af`? If different from `clinks-915af`, we need to align.
2. Should the `customer` object in the response include a field indicating the auth provider (e.g., `"auth_provider": "google"`)?
3. Are there any additional fields the backend needs from the mobile app beyond `firebase_token` and `date_of_birth`?
4. What is the expected behavior if a user signed up with email/password and later tries Google Sign-In with the same email? (Link accounts? Reject? Override?)

---

**Contact:** Mobile App Team  
**Files Modified:** `GoogleSignIn.js`, `Login.js`, `Api.js`, `index.js`  
**Packages Added:** `@react-native-firebase/auth`, `@react-native-google-signin/google-signin`
