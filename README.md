# Books Scraper API

An end-to-end backend mini-project that combines web scraping, REST APIs,
database persistence, and Excel export.

The application scrapes book data from a demo website, stores it in PostgreSQL
with deduplication logic, and exposes it through a FastAPI service.

---

## Tech Stack

- Python
- Playwright
- FastAPI
- PostgreSQL (Docker)
- SQLAlchemy
- Pandas
- OpenPyXL

---

## Data Source

https://books.toscrape.com/  
Demo website used for web scraping practice.

---

## Features

- Book scraping with pagination
- PostgreSQL persistence with upsert logic (based on book URL)
- API pagination using `page` and `limit`
- Excel export of a subset of records
- Clean separation of concerns (scraper, database, API)

---

## Prerequisites

Before running the project, make sure you have installed:

- Python 3.10+
- Docker
- Git

---

## Setup & Run

### 1. Clone repository and create virtual environment

```bash
git clone <repo-url>
cd books-scraper
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
  -e POSTGRES_DB=booksdb \
  -p 5432:5432 \
  -v books_pgdata:/var/lib/postgresql/data \
  -d postgres:16

