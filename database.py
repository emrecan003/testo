from sqlalchemy import create_engine
from sqlalchemy.engine.base import Transaction
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, session, sessionmaker
from sqlalchemy import Integer, String, Column
from sqlalchemy.sql.sqltypes import Boolean
import threading
import os

######## INITIALISE SQL #########
def sql_session() -> scoped_session:
    engine = create_engine(os.environ.get('DATABASE_URL'))
    BASE.metadata.bind = engine
    BASE.metadata.create_all(engine)
    return scoped_session(sessionmaker(bind=engine, autoflush=False))


BASE = declarative_base()
SESSION = sql_session()
##################################


class Users(BASE):
    __tablename__ = "users"
    userid = Column('userid', Integer, primary_key=True, unique=True)
    username = Column('username', String)
    adress = Column('adress', String, unique=True)
    txn = Column('txn',String, unique=True)
    photo_id = Column('photo_id', String, unique=True)
    is_finished = Column('is_finished',Boolean, default=False)
    is_disqalified = Column('is_disqalified', Boolean, default=False)
    raw_balance = Column('raw_balance',String)
    readable_balance = Column('readable_balance', String)
    transaction_date = Column('transaction_date',String)

    def __init__(self, userid, username, adress=None, txn=None, photo_id=None, is_disqalified=False, is_finished=False, raw_balance=None, readable_balance=None, transaction_date=None) -> None:
        self.userid = userid
        self.username = username
        self.adress = adress
        self.txn = txn
        self.photo_id = photo_id
        self.is_finished = is_finished
        self.is_disqalified = is_disqalified
        self.raw_balance = raw_balance
        self.readable_balance = readable_balance
        self.transaction_date = transaction_date



    def __repr__(self) -> str:
        return '{}-{}-{} Hesap oluşturuldu'.format(self.userid, self.username, self.adress)


Users.__table__.create(checkfirst=True)


USERS_LOCK = threading.RLock()

def create_new_user(userid, username) -> bool:
    with USERS_LOCK:
        try:
            if not username:
                username = f'This user has no username <a href="tg://user?id={userid}">Userlink</a>'
            SESSION.add(Users(userid=userid, username=username))
            SESSION.commit()
            SESSION.close()
            return True
        except:
            return False



def add_attribute_to_user(userid,attribute_name,attribute=None):
    with USERS_LOCK:
        try:
            user = SESSION.query(Users).filter(Users.userid == userid).first()
            if attribute_name == 'adress':
                user.adress = attribute
                SESSION.commit()
                SESSION.close()
                return True
            elif attribute_name == 'photo_id':
                user.photo_id = attribute
                SESSION.commit()
                SESSION.close()
                return True
            elif attribute_name == 'txn':
                user.txn = attribute
                SESSION.commit()
                SESSION.close()
                return True
            elif attribute_name == 'finish':
                user.is_finished = True
                SESSION.commit()
                SESSION.close()
                return True
            elif attribute_name == 'raw_balance':
                user.raw_balance = attribute
                SESSION.commit()
                SESSION.close()
                return True
            elif attribute_name == 'readable_balance':
                user.readable_balance = attribute
                SESSION.commit()
                SESSION.close()
                return True
            elif attribute_name == 'transaction_date':
                user.transaction_date = attribute
                SESSION.commit()
                SESSION.close()
                return True
        except:
            return None


def check_user_exists(userid) -> bool:
    with USERS_LOCK:
        return True if SESSION.query(Users).filter(Users.userid == userid).first() else False



def check_is_finished(userid) -> bool:
    with USERS_LOCK:
        return True if SESSION.query(Users).filter(Users.userid == userid).first().is_finished else False

def check_is_disqalified(userid) -> bool:
    with USERS_LOCK:
        return True if SESSION.query(Users).filter(Users.userid == userid).first().is_disqalified else False


def get_user(userid):
    with USERS_LOCK:
        return SESSION.query(Users).filter(Users.userid == userid).first()
