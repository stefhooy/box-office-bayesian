import requests, re, time, sys
from bs4 import BeautifulSoup
import pandas as pd
sys.stdout.reconfigure(encoding='utf-8')

HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

def make_slug(title, year=None):
    t = title.strip()
    for article in ['The ', 'A ', 'An ']:
        if t.startswith(article):
            t = t[len(article):] + '-' + article.strip()
            break
    t = re.sub(r"[''\u2019]", '', t)
    t = re.sub(r'[^a-zA-Z0-9\-]', '-', t)
    t = re.sub(r'-+', '-', t).strip('-')
    return f'{t}-({year})' if year else t

def parse_budget(html):
    text = html.replace('\xa0', ' ')
    m = re.search(r'Production Budget:\s*\$([\d,]+)', text)
    return int(m.group(1).replace(',', '')) if m else None

def parse_revenue(html):
    text = html.replace('\xa0', ' ')
    soup = BeautifulSoup(text, 'html.parser')
    for row in soup.find_all('tr'):
        if 'Worldwide Box Office' in row.get_text():
            m = re.search(r'\$([\d,]+)', row.get_text())
            if m:
                return int(m.group(1).replace(',', ''))
    return None

df_raw = pd.read_csv('data/movies_raw.csv')
df_raw['budget'] = pd.to_numeric(df_raw['budget'], errors='coerce').fillna(0)
df_raw['release_year'] = pd.to_datetime(df_raw['release_date'], errors='coerce').dt.year
missing = df_raw[df_raw['budget'] == 0].head(8)

for _, row in missing.iterrows():
    year = int(row['release_year']) if pd.notna(row['release_year']) else None
    found = False
    for slug in [make_slug(row['title']), make_slug(row['title'], year)]:
        r = requests.get('https://www.the-numbers.com/movie/' + slug, headers=HEADERS, timeout=8)
        if r.status_code == 200:
            b = parse_budget(r.text)
            rev = parse_revenue(r.text)
            print(f"FOUND  {row['title'][:35]:<35} budget=${b:,} revenue=${rev:,}" if b and rev else f"FOUND  {row['title'][:35]:<35} budget={b} revenue={rev}")
            found = True
            break
        time.sleep(0.3)
    if not found:
        print(f"MISSED {row['title'][:35]}")
    time.sleep(0.4)
