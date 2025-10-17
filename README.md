
# Article scraping

Wykonanie zadania rekrutacyjnego, w którym należało zescrapować dane z zadanych artykułow.
Skrypt napisany pod scrap_articles ograniczony jest jedynie do pobierania danych z artykułow na przesłanych stronach, ze względu na wyszukiwanie po konkretnej klasie.

Po uruchomieniu docker'a automatycznie scrapowane są dane z dołączonych artykułów.

Do scrapowania danych została wykorzystana biblioteka playwright, ze względu na strony, które nie korzystają z SSR(pojawił się problem z dostępem do danych przy użyniu beautifulsoup4)

Istnieje możliwość uruchomienia aplikacji za pomocą Docker'a, który odpowiednio zainstaluje wymagane obrazy. W tym przypadku aplikację(django) oraz wskazanego postgresql.

## Biblioteki

**Djagno:** 5.2.1

**djangorestframework:** 3.15.2

**requests:** 2.31.0

**playwright:** 1.55.0

**dateparser:** 1.2.2

**django-filter:** 24.2

**beautifulsoup4:** 4.12.3 (nie wymagane)

**psycopg2-binary** 2.9 (nie wymagane bez dockera)

## Instalacja


```
git clone https://github.com/Toqqe/articlescrap
cd articlescrap

python -m venv venv
# Windows: venv\Scripts\activate
# Linux / macOS: source venv/bin/activate

pip install -r requirements.txt

python manage.py makemigrations
python manage.py migrate

playwright install

python manage.py runserver // python manage.py scrap_articles

```
Uruchomienie z dockerem
```
...

docker compose build
docker compose up

```
## API 

#### Pobierz wszystkie artykuły

```http
  GET /api/v1/articles/
```
#### Pobierz artykuł o danym ID

```http
  GET /api/v1/articles/{id}
```

| Parametr | Typ     | Opis                       |
| :-------- | :------- | :-------------------------------- |
| `id`      | `string` | **Opcjonalny**. Id do pobrania artykułu |

Ex. http://localhost:8000/api/v1/articles/

```http
  GET /api/v1/articles/?source=domain.pl
```

| Parametr | Typ     | Opis                       |
| :-------- | :------- | :-------------------------------- |
| `source`      | `string` | **Opcjonalny**. Id of item to fetch |

Ex. http://localhost:8000/api/v1/articles/1

