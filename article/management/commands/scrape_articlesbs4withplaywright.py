from django.core.management.base import BaseCommand
from bs4 import BeautifulSoup
import requests
from playwright.sync_api import sync_playwright

articles_url = [
    'https://galicjaexpress.pl/ford-c-max-jaki-silnik-benzynowy-wybrac-aby-zaoszczedzic-na-paliwie',
    'https://galicjaexpress.pl/bmw-e9-30-cs-szczegolowe-informacje-o-osiagach-i-historii-modelu',
    'https://take-group.github.io/example-blog-without-ssr/jak-kroic-piers-z-kurczaka-aby-uniknac-suchych-kawalkow-miesa',
    'https://take-group.github.io/example-blog-without-ssr/co-mozna-zrobic-ze-schabu-oprocz-kotletow-5-zaskakujacych-przepisow',
]

class Command(BaseCommand):
    help = 'Command to scrape data from articles'
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36"
        }
    
    def __init__(self):
        super().__init__()
        self.fetch_failed = []
        self.success_urls = []
        self.art_data = []
        
    def found_value(self, value, tag,  url=None):
        if value:
            text = value.get_text(strip=True)
            entry = {'url':url}
            if tag in ('h1', 'title'):
                entry['title'] = text
            else: 
                entry['body'] = text
                entry['HTML_body'] = str(value)
            self.add_entry(entry)
            
            if url not in self.success_urls:
                self.success_urls.append(url)
                
            return True
        else:
            self.fetch_failed.append(url)
            return False
        
    def fetch_and_parse(self, url, tag='h1', class_=None):
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            return soup.find(tag, class_=class_)
        except requests.RequestException as e:
            self.stdout.write(self.style.ERROR(f'Fetching error {url}: {e}'))
            return False
        
    def add_entry(self, entry):
        """Dodaje lub aktualizuje wpis w self.art_data bez duplikatów URL."""
        for existing in self.art_data:
            if existing['url'] == entry['url']:
                existing.update({k: v for k, v in entry.items() if v})
                return
        self.art_data.append(entry)
        
    def try_tags(self, url, tag, class_=None):
        result = self.fetch_and_parse(url, tag=tag, class_=class_)
        if self.found_value(result, tag=tag, url=url):
            return True
        return False
    
    def scrap_next(self, url, tag='', class_=''):
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()            
            page.goto(url,wait_until="networkidle", timeout=15000)
            try:
                selector = f"{tag}.{class_.split()[0]}" if class_ else "div"
                try:
                    page.wait_for_selector(selector, state="attached", timeout=15000)
                except TimeoutError:
                    self.stdout.write(self.style.WARNING(f'No {tag} found for {url}'))
                    
                title = page.query_selector(tag)
                title_clear = title.inner_text().strip() if title else None

                body = page.query_selector(f"{tag}.{class_}" if class_ else "div")
                body_clear = body.inner_text().strip() if body else None
                body_html = body.evaluate("el => el.outerHTML") if body else None

                self.add_entry({
                    "url": url,
                    "title": title_clear,
                    "body": body_clear,
                    "HTML_body": body_html
                })
                if url not in self.success_urls:
                    self.success_urls.append(url)
                success = True
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Playwright error for {url}: {e}"))
                self.fetch_failed.append(url)
                success = False
            finally:
                browser.close()
            return success
             
    def handle(self, *args, **kwargs):
        ## First get titles
        for i, url in enumerate(articles_url, start=1):
            self.stdout.write(f'Scraping article {i}')
            ##title = self.try_tags(url, tag='h1', class_='div')
            title = self.scrap_next(url, tag='h1', class_='')
            if not title:
                self.scrap_next(url, tag='h1')
            
        ## Second get 
        for url in self.success_urls:
            ##art_body = self.try_tags(url, tag='div', class_='table-post')
            art_body = self.scrap_next(url, tag='div', class_='table-post')
            ##date = self.try_tags(url, tag='div', class_='table-post')
            if not art_body: 
                self.scrap_next(url, tag="div", class_='article-content')


                                
        for entry in self.art_data:
            self.stdout.write(self.style.SUCCESS(f"\nURL: {entry['url']}"))
            if 'title' in entry:
                self.stdout.write(f"Title: {entry['title']}")
            if 'body' in entry:
                self.stdout.write(f"Body (start): {entry['body'][:100]}...")
            if 'HTML_body' in entry:
                self.stdout.write(f"HTML_body (start): {entry['HTML_body'][:100]}...")