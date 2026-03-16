import os
import argparse
from pathlib import Path


def get_config():
    """Parse CLI arguments and return configuration dictionary."""
    parser = argparse.ArgumentParser()
    parser.add_argument('--remote', action='store_true', default=False,
                        help='Use remote Railway backend instead of offline mode')
    parser.add_argument('--reauth', action='store_true', default=False,
                        help='Force re-authentication with Google OAuth')
    parser.add_argument('--api-url', type=str, default=None,
                        help='Railway API URL (overrides RAILWAY_API_URL env var)')
    args = parser.parse_args()

    base_dir = Path.home() / '.nsu_mcp'
    base_dir.mkdir(exist_ok=True)

    api_url = args.api_url if args.api_url else os.getenv(
        'RAILWAY_API_URL', 
        'https://nsu-audit-api.railway.app'
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
