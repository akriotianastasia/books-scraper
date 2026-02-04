from sqlalchemy.orm import Session
from sqlalchemy.dialects.postgresql import insert
from .models import Book

def upsert_books(db: Session, books: list[dict]) -> int:
    if not books:
        return 0

    allowed = set(Book.__table__.columns.keys())
    books_clean = [{k: v for k, v in b.items() if k in allowed} for b in books]

    stmt = insert(Book).values(books_clean)
    update_cols = {
        c.name: getattr(stmt.excluded, c.name)
        for c in Book.__table__.columns
        if c.name not in ("id", "created_at")
    }
    stmt = stmt.on_conflict_do_update(index_elements=[Book.url], set_=update_cols)
    result = db.execute(stmt)
    return result.rowcount

def count_books(db: Session) -> int:
    return db.query(Book).count()

def list_books_page(db: Session, page: int, limit: int):
    # page=1 → offset=0
    offset = max(page - 1, 0) * limit
    return (
        db.query(Book)
        .order_by(Book.id.asc())
        .offset(offset)
        .limit(limit)
        .all()
    )
