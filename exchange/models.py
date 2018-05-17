from pyramid.security import Allow, Everyone
from sqlalchemy import (
    Column,
    Integer,
    Text,
    Boolean,
    SmallInteger,
    ForeignKey,
    Float,
    desc,
    func
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import (
    scoped_session,
    sessionmaker,
)
from sqlalchemy.sql import label
from zope.sqlalchemy import ZopeTransactionExtension

DBSession = scoped_session(
    sessionmaker(extension=ZopeTransactionExtension()))
Base = declarative_base()


def foreign_key_column(name, type_, target, nullable=False):
    fk = ForeignKey(target)
    if name:
        return Column(name, type_, fk, nullable=nullable)
    else:
        return Column(type_, fk, nullable=nullable)


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(Text, unique=True)
    eur = Column(Float)
    btc = Column(Float)

    @staticmethod
    def get_by_username(username):
        return DBSession.query(User).filter_by(username=username).one()

    @staticmethod
    def get_by_id(id):
        return DBSession.query(User).filter_by(id=id).one()

    @staticmethod
    def filter_by_id_update_eur(id, eur):
        return DBSession.query(User).filter_by(id=id).update(dict(eur=eur))

    @staticmethod
    def filter_by_id_update_btc(id, btc):
        return DBSession.query(User).filter_by(id=id).update(dict(btc=btc))


class ActiveOrder(Base):
    BUY_ORDER = 0
    SELL_ORDER = 1

    __tablename__ = 'active_orders'
    id = Column(Integer, primary_key=True)
    time = Column(Integer, unique=True)
    type = Column(SmallInteger)
    amount = Column(Float)
    price = Column(Float)
    deleted = Column(Boolean, default=False)
    user_id = foreign_key_column(None, Integer, "users.id")

    @staticmethod
    def add(data):
        return DBSession.add(ActiveOrder(time=data['time'],
                                         type=data['type'],
                                         amount=data['amount'],
                                         price=data['price'],
                                         user_id=data['user_id']
                                         ))

    @staticmethod
    def delete(id):
        return DBSession.query(ActiveOrder).filter_by(id=id).delete()

    @staticmethod
    def filter_by_user_id_order_by_time(user_id):
        return DBSession.query(ActiveOrder).filter_by(user_id=user_id, deleted=False).order_by(ActiveOrder.time)

    @staticmethod
    def sum_amount(type):
        return DBSession.query(ActiveOrder, label('total', func.sum(ActiveOrder.amount)), ActiveOrder.price) \
            .group_by(ActiveOrder.price).filter_by(type=type, deleted=False).order_by(desc(ActiveOrder.price))


class Root(object):
    __acl__ = [(Allow, Everyone, 'view'),
               (Allow, 'group:editors', 'edit')]

    def __init__(self, request):
        pass
