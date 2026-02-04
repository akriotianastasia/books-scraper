from fastapi import FastAPI, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.db.session import SessionLocal, Base, engine
from app.db import crud
from app.db import models
from app.scraper import scrape_books
from app.export import books_to_excel_bytes

app = FastAPI(title="Books Scraper API")

# Create tables
Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/scrape")
def scrape(pages: int = 1, db: Session = Depends(get_db)):
    books = scrape_books(max_pages=pages)
    affected = crud.upsert_books(db, books)
    db.commit()
    total = crud.count_books(db)
    return {"scraped": len(books), "db_rows_affected": affected, "total_in_db": total}


@app.get("/books")
def get_books(page: int = 1, limit: int = 20, db: Session = Depends(get_db)):
    limit = max(1, min(limit, 200))
    page = max(1, page)

    items = crud.list_books_page(db, page=page, limit=limit)
    total = crud.count_books(db)

    return {
        "total": total,
        "page": page,
        "limit": limit,
        "items": [
            {
                "id": b.id,
                "title": b.title,
                "price": b.price,
                "availability": b.availability,
                "rating": b.rating,
                "url": b.url,
            }
            for b in items
        ],
    }

from fastapi.responses import StreamingResponse
from app.export import books_to_excel_bytes

@app.get("/export.xlsx")
def export_xlsx(page: int = 1, limit: int = 200, db: Session = Depends(get_db)):
    limit = max(1, min(limit, 2000))
    page = max(1, page)

    rows = crud.list_books_page(db, page=page, limit=limit)

    books = [
        {
            "title": b.title,
            "price": b.price,
            "availability": b.availability,
            "rating": b.rating,
            "url": b.url,
        }
        for b in rows
    ]

    content = books_to_excel_bytes(books)
    filename = f'books_page_{page}_limit_{limit}.xlsx'

    return StreamingResponse(
        content,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
