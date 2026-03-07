# Deployment Guide — Phase 2
**NSU Audit Core | Deploy everything before the demo**

---

## Backend → Railway

### First-time setup

1. Go to https://railway.app and sign in with GitHub
2. Click "New Project" → "Deploy from GitHub repo"
3. Select your repo
4. Set the root directory to `backend/`

### Environment Variables (set in Railway dashboard)

Go to your Railway project → Variables tab. Add:
```
SUPABASE_URL=https://<project>.supabase.co
SUPABASE_ANON_KEY=<anon_key>
SUPABASE_SERVICE_KEY=<service_key>
PORT=8000

```

### Procfile

Create `backend/Procfile`:
```
web: uvicorn main:app --host 0.0.0.0 --port $PORT
```

### Verify Deployment

After Railway deploys, visit:
```
https://nsu-audit-api.railway.app/health
```
Should return: `{"status": "ok", "version": "2.0"}`

Also check auto-generated docs:
```
https://nsu-audit-api.railway.app/docs
```

### Re-deploy (after code changes)

```bash
railway up
```
Or push to `main` — GitHub Actions will auto-deploy.

---

## Frontend → Vercel

### First-time setup

1. Go to https://vercel.com and sign in with GitHub
2. Click "Add New Project" → import your repo
3. Set root directory to `frontend/`
4. Framework: Vite
5. Build command: `npm run build`
6. Output directory: `dist`

### Environment Variables (set in Vercel dashboard)

Go to Project Settings → Environment Variables. Add:
```
VITE_SUPABASE_URL=https://<project>.supabase.co
VITE_SUPABASE_ANON_KEY=<anon_key>
VITE_API_URL=https://nsu-audit-api.railway.app
```

### vercel.json (SPA routing)

Create `frontend/vercel.json`:
```json
{
  "rewrites": [
    { "source": "/(.*)", "destination": "/index.html" }
  ]
}
```

### Verify Deployment

Visit your Vercel URL. You should see the login page.

### Re-deploy

Push to `main` — Vercel auto-deploys on every push.

---

## Mobile → Flutter APK

### Prerequisites
- Flutter SDK installed
- Android Studio + Android SDK
- Device connected or emulator running

### Configure Supabase in Flutter

Create `mobile/lib/config.dart`:
```dart
class Config {
  static const String supabaseUrl = 'https://<project>.supabase.co';
  static const String supabaseAnonKey = '<anon_key>';
  static const String apiBaseUrl = 'https://nsu-audit-api.railway.app';
}
```
⚠️ This file goes in `.gitignore` if it contains real keys, or use `--dart-define` for CI.

### Add Google OAuth redirect scheme

In `mobile/android/app/src/main/AndroidManifest.xml`, inside `<activity>`:
```xml
<intent-filter>
  <action android:name="android.intent.action.VIEW" />
  <category android:name="android.intent.category.DEFAULT" />
  <category android:name="android.intent.category.BROWSABLE" />
  <data android:scheme="io.supabase.nsuaudit" android:host="login-callback" />
</intent-filter>
```

Add this redirect URL in Supabase Auth settings:
```
io.supabase.nsuaudit://login-callback
```

### Build Debug APK (for testing)
```bash
cd mobile
flutter pub get
flutter build apk --debug
```
APK location: `mobile/build/app/outputs/flutter-apk/app-debug.apk`

### Build Release APK (for demo)
```bash
flutter build apk --release
```
APK location: `mobile/build/app/outputs/flutter-apk/app-release.apk`

### Install on Device
```bash
flutter install
```
Or drag APK to device.

---

## CI/CD → GitHub Actions

### Secrets to add in GitHub repo settings

Go to repo → Settings → Secrets and variables → Actions. Add:
```
RAILWAY_TOKEN=<your railway token>
VERCEL_TOKEN=<your vercel token>
VERCEL_ORG_ID=<vercel org id>
VERCEL_PROJECT_ID=<vercel project id>
```

Get Railway token: Railway dashboard → Account → Tokens
Get Vercel token: Vercel dashboard → Settings → Tokens

### GitHub Actions workflow location
`.github/workflows/ci.yml`

This runs automatically on every push to `main` and every PR.

---

## Checklist Before Demo

- [ ] Backend live on Railway: `https://nsu-audit-api.railway.app/health` returns 200
- [ ] Frontend live on Vercel: login page loads
- [ ] Google login works on web
- [ ] CSV audit works end-to-end on web
- [ ] OCR audit works with a test transcript image
- [ ] History page shows past scans
- [ ] Flutter APK installs and Google login works
- [ ] CLI `--remote` flag saves to history
- [ ] Load test passed (20 users, 0% errors)
- [ ] GitHub Actions CI green on `main`
