from sqlalchemy import sql, Column, Sequence

from utils.db_api.database import db


class Screenshots(db.Model):
    __tablename__ = "items"
    query: sql.Select

    id = Column(db.Integer, Sequence("user_id_seq"), primary_key=True )
    test_code = Column(db.String(20))
    test_name = Column(db.String(200))
    exercise_name = Column(db.String(20))
    exercise_code = Column(db.String(20))
    photo = Column(db.String(250))
    isCheck = Column(db.Boolean)
    author = Column(db.Integer)
    isDeleted = Column(db.Boolean)
    def __repr__(self):
        return f"""
Скриншот № {self.id} 
Тема - {self.test_name} 
{self.exercise_name} номер
"""

class Users(db.Model):
    __tablename__ = "users"
    query: sql.Select

    id = Column(db.Integer, Sequence("user_id_seq"), primary_key=True )
    tg_id = Column(db.Integer)
    first_name = Column(db.String(200))
    full_name = Column(db.String(200))
    balance = Column(db.String(250))
    referal = Column(db.Integer)
    referal_code = Column(db.String(250))
    username = Column(db.String(200))
    isReferalActivated = Column(db.Boolean)

    def __repr__(self):
        return f"""
Юзер № {self.id} 
Имя - {self.first_name} 
Полное имя - {self.full_name}
Баланс - {self.balance} 
Реферал - {self.referal} 
Рефералка - {self.referal_code} 
Юзернейм - {self.username}
"""