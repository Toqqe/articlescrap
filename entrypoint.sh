#!/bin/sh
set -e  

echo "Running migrations..."
python manage.py makemigrations
python manage.py migrate

# scrapowanie artykułów
echo "Scraping articles..."
python manage.py scrape_articles

# uruchomienie serwera Django
echo "Starting Django server..."
exec "$@"