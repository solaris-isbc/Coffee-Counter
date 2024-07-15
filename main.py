import datetime

from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import create_engine, Column, Integer, Date, Float
import sqlalchemy
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel

app = FastAPI()

# Database setup
DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = sqlalchemy.orm.declarative_base()


# Database model
class DailyEntry(Base):
    __tablename__ = "daily_entries"
    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, index=True)
    amount = Column(Float, default=0)


# Create tables
Base.metadata.create_all(bind=engine)


# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Pydantic model for request data
class DailyEntryCreate(BaseModel):
    date: datetime.date
    amount: float


# Pydantic model for response data
class DailyEntryResponse(BaseModel):
    id: int
    date: datetime.date
    amount: float


# API endpoint to upsert an entry
@app.post("/daily_entries/", response_model=DailyEntryResponse)
async def upsert_daily_entry(daily_entry: DailyEntryCreate, db: Session = Depends(get_db)):
    posted_entry = DailyEntry(**daily_entry.model_dump())
    db_entry = db.query(DailyEntry).filter(DailyEntry.date == posted_entry.date).first()
    if db_entry is None:
        db.add(posted_entry)
        db.commit()
        db.refresh(posted_entry)
        return posted_entry

    db_entry.amount += daily_entry.amount
    db.commit()
    db.refresh(db_entry)
    return db_entry


# API endpoint to read an item by ID
@app.get("/daily_entries/{date}", response_model=DailyEntryResponse)
async def read_daily_entry(date: datetime.date, db: Session = Depends(get_db)):
    db_entry = db.query(DailyEntry).filter(DailyEntry.date == date).first()
    if db_entry is None:
        raise HTTPException(status_code=404, detail="Entry not found")
    return db_entry


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)