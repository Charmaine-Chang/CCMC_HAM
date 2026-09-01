"""Capture screenshots of key pages for the README.

Start the app first (python app.py), then run:
    python scripts/capture_screenshots.py [base_url]

Screenshots are saved to docs/screenshots/.
"""
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright

BASE_URL = sys.argv[1] if len(sys.argv) > 1 else 'http://127.0.0.1:5005'
OUT_DIR = Path(__file__).resolve().parent.parent / 'docs' / 'screenshots'

PUBLIC_PAGES = [
    ('home', '/'),
    ('welcome', '/welcome'),
    ('public-events', '/public-events'),
]

AUTH_PAGES = [
    ('dashboard', '/dashboard/'),
    ('events', '/events/'),
    ('visitors', '/visitors/'),
    ('reports', '/reports'),
    ('settings', '/manage/settings'),
]


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        browser = p.chromium.launch(channel='msedge', headless=True)
        page = browser.new_page(viewport={'width': 1280, 'height': 900})

        for name, path in PUBLIC_PAGES:
            page.goto(BASE_URL + path, wait_until='networkidle')
            page.screenshot(path=str(OUT_DIR / f'{name}.png'), full_page=True)
            print(f'saved {name}.png')

        page.goto(BASE_URL + '/auth/login', wait_until='networkidle')
        page.fill('input[name="username"]', 'admin')
        page.fill('input[name="password"]', 'Password123!')
        page.click('form button')
        page.wait_for_load_state('networkidle')
        print('logged in as admin')

        for name, path in AUTH_PAGES:
            page.goto(BASE_URL + path, wait_until='networkidle')
            page.wait_for_timeout(800)
            page.screenshot(path=str(OUT_DIR / f'{name}.png'), full_page=True)
            print(f'saved {name}.png')

        browser.close()


if __name__ == '__main__':
    main()