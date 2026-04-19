from database import Base
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Integer

class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True)
    tg_id: Mapped[int] = mapped_column(Integer, unique=True)
    name: Mapped[str] = mapped_column(String(50))
    phone: Mapped[str] = mapped_column(String(20))
    date: Mapped[str] = mapped_column(String(20))

    def __repr__(self):
        return f"User(id={self.id}, tg_id={self.tg_id}, name='{self.name}', phone='{self.phone}', date='{self.date}')"
