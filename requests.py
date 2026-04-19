#Тут я реализую функции для работы с базой данных, а также функции для получения и обработки запросов от пользователей.

from database import SessionLocal
from models import User

def add_user(tg_id: int, name: str, phone: str, date: str):
    with SessionLocal() as db:
        new_user = User(tg_id=tg_id, name=name, phone=phone, date=date)
        db.add(new_user)
        db.commit()
    return True

def delete_user(tg_id: int):
    with SessionLocal() as db:
        user = db.query(User).filter(User.tg_id == tg_id).first()
        if user:
            db.delete(user)
            db.commit()