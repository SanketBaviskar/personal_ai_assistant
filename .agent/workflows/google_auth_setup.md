---
description: How to create a Google Client ID for OAuth 2.0
---

# Setting up Google OAuth 2.0

Follow these steps to generate a Google Client ID for your application.

## 1. Create a Project

1. Go to the [Google Cloud Console](https://console.cloud.google.com/).
2. Click the project dropdown at the top left and select **"New Project"**.
3. Name your project (e.g., "Personal AI Assistant") and click **"Create"**.

## 2. Configure OAuth Consent Screen

1. In the left sidebar, navigate to **APIs & Services** > **OAuth consent screen**.
2. Select **External** (for personal testing) and click **Create**.
3. Fill in the required fields:
    - **App Name**: Personal AI Assistant
    - **User Support Email**: Your email
    - **Developer Contact Information**: Your email
4. Click **Save and Continue** through the "Scopes" and "Test Users" sections (you can add yourself as a test user if needed).
5. Click **Back to Dashboard**.

## 3. Create Credentials

1. In the left sidebar, click **Credentials**.
2. Click **+ CREATE CREDENTIALS** at the top and select **OAuth client ID**.
3. **Application type**: Select **Web application**.
4. **Name**: `React Frontend` (or similar).
5. **Authorized JavaScript origins**:
    - Add: `http://localhost:5173`
6. **Authorized redirect URIs**:
    - Add: `http://localhost:5173`
    - Add: `http://localhost:5173/login`
7. Click **Create**.

## 4. Copy Your Client ID

1. A modal will appear with your **Client ID** and **Client Secret**.
2. Copy the **Client ID** (it looks like `123456789-abcdefg.apps.googleusercontent.com`).

## 5. Update Your Code

### Frontend

Open `frontend/src/App.tsx` and replace `YOUR_GOOGLE_CLIENT_ID_HERE` with your new Client ID.

```typescript
const GOOGLE_CLIENT_ID = "123456789-abcdefg.apps.googleusercontent.com";
```

### Backend (Optional but Recommended)

Set the `GOOGLE_CLIENT_ID` environment variable for your backend to strictly verify tokens were issued for your app.

```bash
# Windows PowerShell
$env:GOOGLE_CLIENT_ID="your_client_id_here"
```
