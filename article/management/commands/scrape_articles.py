from django.core.management.base import BaseCommand
from playwright.sync_api import sync_playwright
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from dateparser import parse as parse_date
from article.models import Article
from django.utils import timezone

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
     
        
    def add_entry(self, entry):
        for existing in self.art_data:
            if existing['url'] == entry['url']:
                existing.update({k: v for k, v in entry.items() if v})
                return
        self.art_data.append(entry)

    
    def scrap_next(self, url, tag='', class_=''):
        def parse_date_return(raw_dt):
            if not raw_dt:
                return None
            parsed = parse_date(raw_dt, languages=['pl'])
            if not parsed:
                return None
            relative_words = [    "ago", "yesterday", "godzin", "minut", "sekund",
                                    "wczoraj", "dzień temu", "dni temu", "temu"
                                ]
            
            if not any(word in raw_dt.lower() for word in relative_words):
                parsed = parsed.replace(hour=0, minute=0, second=0, microsecond=0)
            if timezone.is_naive(parsed):
                parsed = timezone.make_aware(parsed)
            return parsed
        
        def scrape_date(page):
            
            time = page.query_selector('time')
            if time:
                dt = time.get_attribute('datetime')
                raw_dt = dt.strip() if dt else time.inner_text().strip()
                parsed = parse_date_return(raw_dt)
                if timezone.is_naive(parsed):
                    parsed = timezone.make_aware(parsed)
                return parsed
            
            for tag in ['p', 'span', 'div']:
                elements = page.query_selector_all(tag)
                for el in elements:
                    text = el.inner_text().strip()
                    parsed = parse_date_return(text)
                    if parsed:
                        return parsed
            return 'Not found'
        
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()            
            try:
                page.goto(url,wait_until="networkidle", timeout=30000)
                selector = f"{tag}.{class_.split()[0]}" if class_ else "div"
                try:
                    page.wait_for_selector(selector, state="attached", timeout=15000)
                except TimeoutError:
                    self.stdout.write(self.style.WARNING(f'No {tag} found for {url}'))
                    
                if url not in self.success_urls:
                    self.success_urls.append(url)
                    
                title = page.query_selector(tag)
                title_clear = title.inner_text().strip() if title else 'Not found'

                body = page.query_selector(f"{tag}.{class_}" if class_ else "div")
                body_clear = body.inner_text().strip() if body else 'Not found'
                body_html = body.evaluate("el => el.outerHTML") if body else 'Not found'
                date = scrape_date(page)
                
                self.add_entry({
                    "url": url,
                    "title": title_clear,
                    "body": body_clear,
                    "HTML_body": body_html,
                    "date":date
                })

                success = True
            except PlaywrightTimeoutError as e:
                self.stdout.write(self.style.ERROR(f"Timeout while loading {url}: {e}"))
                self.fetch_failed.append(url)
                success = False
                
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Playwright error for {url}: {e}"))
                self.fetch_failed.append(url)
                success = False
                
            finally:
                browser.close()
            return success
        
    def handle(self, *args, **kwargs):
        ## Get titles
        for i, url in enumerate(articles_url, start=1):
            
            article = Article.objects.filter(source=url)
            if article:
                self.stdout.write(self.style.SUCCESS(f"\nURL: {url} -- exist in DB"))
                continue
            
            self.stdout.write(f'Scraping article {i}')
            self.scrap_next(url, tag='h1', class_='')
            
            art_body = self.scrap_next(url, tag='div', class_='table-post')
            if not art_body: 
                self.scrap_next(url, tag="div", class_='article-content')

        ## Get body        
        for entry in self.art_data:
            self.stdout.write(self.style.SUCCESS(f"\nSaving scraped DATA: {entry['url']}"))
            try:
                ## Save article to DB
                art_obj = Article.objects.create(
                    title=entry.get('title', 'No title'),
                    html_description=entry.get('HTML_body', ''),
                    clear_description=entry.get('body', ''),
                    source=entry.get('url'),
                    date=entry.get('date') 
                )                
            except Exception as e:
                self.stdout.write(self.style.WARNING(f"Failed to save article: {entry.get('url')} - {e}"))
        
        self.stdout.write(self.style.SUCCESS("Finished scraping"))
