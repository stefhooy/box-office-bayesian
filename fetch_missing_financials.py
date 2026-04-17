"""
Gap-fill: fetch missing production budgets from The Numbers.
Only targets films where TMDb budget=0 but revenue > $5M
(small indie films with no public budget data are skipped).
Saves results to data/numbers_supplement.csv
"""
import re
import sys
import time

import pandas as pd
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm

sys.stdout.reconfigure(encoding='utf-8')

HEADERS = {
    'User-Agent': (
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    )
}
BASE = 'https://www.the-numbers.com/movie/'


def make_slug(title, year=None):
    t = title.strip()
    for article in ['The ', 'A ', 'An ']:
        if t.startswith(article):
            t = t[len(article):] + '-' + article.strip()
            break
    t = re.sub(r"[''\u2019\u2018]", '', t)
    t = re.sub(r'[^a-zA-Z0-9\-]', '-', t)
    t = re.sub(r'-+', '-', t).strip('-')
    return f'{t}-({year})' if year else t


def get_slugs(title, year):
    base = [
        make_slug(title),
        make_slug(title, year),
        make_slug(title.replace('&', 'and')),
        make_slug(title.replace('&', 'and'), year),
    ]
    return list(dict.fromkeys(base))


def parse_page(html):
    text = html.replace('\xa0', ' ')
    soup = BeautifulSoup(text, 'html.parser')
    budget, revenue = None, None
    m = re.search(r'Production Budget:\s*\$([\d,]+)', text)
    if m:
        budget = int(m.group(1).replace(',', ''))
    for row in soup.find_all('tr'):
        if 'Worldwide Box Office' in row.get_text():
            m2 = re.search(r'\$([\d,]+)', row.get_text())
            if m2:
                revenue = int(m2.group(1).replace(',', ''))
                break
    return budget, revenue


def fetch(title, year):
    for slug in get_slugs(title, year):
        try:
            r = requests.get(BASE + slug, headers=HEADERS, timeout=8)
            if r.status_code == 200:
                b, rev = parse_page(r.text)
                if b or rev:
                    return b, rev, slug
        except Exception:
            pass
        time.sleep(0.25)
    return None, None, None


def main():
    df = pd.read_csv('data/movies_raw.csv')
    df['budget'] = pd.to_numeric(df['budget'], errors='coerce').fillna(0)
    df['revenue'] = pd.to_numeric(df['revenue'], errors='coerce').fillna(0)
    df['release_year'] = (
        pd.to_datetime(df['release_date'], errors='coerce').dt.year
    )

    targets = df[
        (df['budget'] == 0) & (df['revenue'] > 5_000_000)
    ].copy()
    print(f'Targeting {len(targets)} films with budget=0 and revenue > $5M')

    rows = []
    for _, row in tqdm(targets.iterrows(), total=len(targets)):
        year = int(row['release_year']) if pd.notna(row['release_year']) else None
        b, rev, slug = fetch(row['title'], year)
        rows.append({
            'tmdb_id': row['tmdb_id'],
            'title': row['title'],
            'year': year,
            'tmdb_budget': row['budget'],
            'tmdb_revenue': row['revenue'],
            'numbers_budget': b,
            'numbers_revenue': rev,
            'numbers_slug': slug,
        })
        time.sleep(0.4)

    out = pd.DataFrame(rows)
    out.to_csv('data/numbers_supplement.csv', index=False)

    matched = out[out['numbers_budget'].notna()]
    print(f'\nDone. Budgets recovered: {len(matched)} / {len(targets)}')
    print(f'Revenue also recovered:  {out["numbers_revenue"].notna().sum()}')
    print('\nTop recoveries:')
    top = (
        matched[['title', 'numbers_budget', 'numbers_revenue']]
        .sort_values('numbers_budget', ascending=False)
        .head(15)
    )
    print(top.to_string(index=False))


if __name__ == '__main__':
    main()
