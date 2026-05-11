import os
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from pydantic import BaseModel

from routers.session import SaveSessionRequest

from auth import get_current_user

router = APIRouter(prefix="", tags=["login"])


class StudentLoginForm(BaseModel):
    student_id: str
    password: str


ADMIN_LOGIN_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Admin Login - NSU Audit System</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }
        .container {
            background: white;
            padding: 40px;
            border-radius: 12px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            text-align: center;
            max-width: 400px;
            width: 90%;
        }
        h1 { color: #333; margin-bottom: 10px; }
        p { color: #666; margin-bottom: 30px; }
        .btn {
            display: inline-block;
            background: #4285f4;
            color: white;
            padding: 14px 28px;
            border-radius: 8px;
            text-decoration: none;
            font-weight: 600;
            font-size: 16px;
            transition: transform 0.2s, box-shadow 0.2s;
            cursor: pointer;
            border: none;
        }
        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 20px rgba(66, 133, 244, 0.4);
        }
        .logo {
            font-size: 48px;
            margin-bottom: 20px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="logo">🎓</div>
        <h1>Admin Login</h1>
        <p>Sign in with your NSU Google account</p>
        <a href="/api/v1/auth/google" class="btn">
            Sign in with Google
        </a>
    </div>
</body>
</html>
"""


STUDENT_LOGIN_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Student Login - NSU Audit System</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }
        .container {
            background: white;
            padding: 40px;
            border-radius: 12px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            text-align: center;
            max-width: 400px;
            width: 90%;
        }
        h1 { color: #333; margin-bottom: 10px; }
        p { color: #666; margin-bottom: 30px; }
        .form-group { margin-bottom: 20px; text-align: left; }
        label { display: block; margin-bottom: 8px; color: #333; font-weight: 500; }
        input {
            width: 100%;
            padding: 12px;
            border: 2px solid #e0e0e0;
            border-radius: 8px;
            font-size: 16px;
            transition: border-color 0.2s;
        }
        input:focus { outline: none; border-color: #667eea; }
        .btn {
            width: 100%;
            background: #4285f4;
            color: white;
            padding: 14px;
            border-radius: 8px;
            font-weight: 600;
            font-size: 16px;
            cursor: pointer;
            border: none;
            transition: transform 0.2s;
        }
        .btn:hover { transform: translateY(-2px); }
        .error {
            background: #ffebee;
            color: #c62828;
            padding: 12px;
            border-radius: 8px;
            margin-bottom: 20px;
            display: none;
        }
        .logo { font-size: 48px; margin-bottom: 20px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="logo">🎓</div>
        <h1>Student Login</h1>
        <p>Enter your NSU credentials</p>
        <div class="error" id="error"></div>
        <form id="loginForm">
            <div class="form-group">
                <label for="student_id">Student ID</label>
                <input type="text" id="student_id" name="student_id" 
                       placeholder="e.g., 2211234567" required pattern="2\\d{9}">
            </div>
            <div class="form-group">
                <label for="password">Password</label>
                <input type="password" id="password" name="password" required>
            </div>
            <button type="submit" class="btn">Login</button>
        </form>
        <script>
            document.getElementById('loginForm').addEventListener('submit', async (e) => {
                e.preventDefault();
                const studentId = document.getElementById('student_id').value;
                const password = document.getElementById('password').value;
                const errorEl = document.getElementById('error');
                
                try {
                    const response = await fetch('/api/v1/student/login', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({student_id: studentId, password: password})
                    });
                    const data = await response.json();
                    
                    if (response.ok) {
                        localStorage.setItem('access_token', data.access_token);
                        localStorage.setItem('student_id', studentId);
                        window.location.href = '/student/dashboard';
                    } else {
                        errorEl.textContent = data.detail || 'Login failed';
                        errorEl.style.display = 'block';
                    }
                } catch (err) {
                    errorEl.textContent = 'Connection error. Is backend running?';
                    errorEl.style.display = 'block';
                }
            });
        </script>
    </div>
</body>
</html>
"""


SUCCESS_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Login Successful</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }
        .container {
            background: white;
            padding: 60px;
            border-radius: 12px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            text-align: center;
        }
        .check { font-size: 64px; color: #4caf50; }
        h1 { color: #333; margin: 20px 0; }
        p { color: #666; }
        .btn {
            display: inline-block;
            margin-top: 20px;
            background: #4285f4;
            color: white;
            padding: 12px 24px;
            border-radius: 8px;
            text-decoration: none;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="check">✓</div>
        <h1>Login Successful!</h1>
        <p id="message">You can now use the MCP tools.</p>
        <a href="/login" class="btn">Back to Login</a>
    </div>
    <script>
        setTimeout(() => window.close(), 3000);
    </script>
</body>
</html>
"""


SESSION_SAVE_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Session Saved</title>
    <script>
        // Auto-save token from URL hash or localStorage to backend
        window.addEventListener('load', async () => {
            const hash = window.location.hash.substring(1);
            const params = new URLSearchParams(hash);
            const token = params.get('access_token') || localStorage.getItem('access_token');
            
            if (token) {
                try {
                    await fetch('/api/v1/session/save', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({access_token: token})
                    });
                } catch(e) {}
            }
            document.body.innerHTML = '<div style="font-family:sans-serif;text-align:center;padding:50px;"><h1>✓ Session saved</h1><p>You can now return to MCP.</p></div>';
        });
    </script>
</head>
<body></body>
</html>
"""


@router.get("/login", response_class=HTMLResponse)
async def login_page():
    """Main login page - redirects to appropriate login based on user type."""
    return ADMIN_LOGIN_HTML


@router.get("/login/admin", response_class=HTMLResponse)
async def admin_login_page():
    """Admin login page with Google OAuth."""
    return ADMIN_LOGIN_HTML


@router.get("/login/student", response_class=HTMLResponse)
async def student_login_page():
    """Student login page with ID/password form."""
    return STUDENT_LOGIN_HTML


@router.get("/login/success", response_class=HTMLResponse)
async def login_success():
    """Login success page shown after authentication."""
    return SUCCESS_HTML


@router.get("/session/callback", response_class=HTMLResponse)
async def session_callback():
    """Page that saves session token from URL and returns success."""
    return SESSION_SAVE_HTML


@router.get("/api/v1/auth/google")
async def google_auth_redirect():
    """Redirect to Google OAuth login."""
    from config import settings
    from supabase import create_client

    supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_ANON_KEY)
    redirect_to = f"{settings.API_URL}/session/callback"

    try:
        auth_url = supabase.auth.sign_in_with_oauth(
            {"provider": "google", "options": {"redirect_to": redirect_to}}
        )
        if hasattr(auth_url, "url"):
            return RedirectResponse(url=auth_url.url)
        elif isinstance(auth_url, dict):
            return RedirectResponse(url=auth_url.get("url", "/login"))
        else:
            return RedirectResponse(url="/login")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Auth redirect failed: {str(e)}")


@router.get("/api/v1/session/status")
async def session_status():
    """Check if session token exists and is valid."""
    from pathlib import Path

    token_path = Path.home() / ".nsu_mcp" / "supabase_token.txt"
    if not token_path.exists():
        return {"status": "no_session", "message": "No session found"}

    token = token_path.read_text().strip()
    if not token:
        return {"status": "empty", "message": "Session file is empty"}

    return {"status": "success", "message": "Session exists"}


@router.post("/api/v1/session/check")
async def check_session(request: SaveSessionRequest):
    """Verify a token is valid by attempting to decode it."""
    import jwt
    from config import settings

    try:
        payload = jwt.decode(
            request.access_token,
            settings.SUPABASE_JWT_SECRET,
            algorithms=["HS256", "RS256"],
        )
        return {"status": "valid", "user": payload}
    except jwt.ExpiredSignatureError:
        return {"status": "expired", "message": "Token has expired"}
    except jwt.InvalidTokenError as e:
        return {"status": "invalid", "message": str(e)}
