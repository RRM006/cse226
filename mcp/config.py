import os
import argparse
from pathlib import Path


def get_config():
    """Parse CLI arguments and return configuration dictionary."""
    parser = argparse.ArgumentParser()
    parser.add_argument('--remote', action='store_true', default=False,
                        help='Use remote Railway backend instead of local backend')
    parser.add_argument('--reauth', action='store_true', default=False,
                        help='Force re-authentication with Google OAuth')
    parser.add_argument('--api-url', type=str, default=None,
                        help='API URL (overrides RAILWAY_API_URL or LOCAL_API_URL env var)')
    args = parser.parse_args()

    base_dir = Path.home() / '.nsu_mcp'
    base_dir.mkdir(exist_ok=True)

    # Default: use local backend (http://localhost:8000)
    # Use --remote flag to switch to Railway backend
    if args.remote:
        api_url = args.api_url if args.api_url else os.getenv(
            'RAILWAY_API_URL', 
            'https://nsu-audit-api.railway.app'
        )
    else:
        # Local backend (default for mcp web / mcp local)
        api_url = args.api_url if args.api_url else os.getenv(
            'LOCAL_API_URL',
            'http://localhost:8000'
        )

    return {
        'remote': args.remote,
        'reauth': args.reauth,
        'api_url': api_url,
        'token_path': base_dir / 'token.json',
        'credentials_path': Path(__file__).parent / 'credentials.json',
        'history_path': base_dir / 'history.json',
        'api_token_path': base_dir / 'api_token.txt',
    }
