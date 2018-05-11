from pyramid.security import Allow, Everyone

from sqlalchemy import (
    Column,
    Integer,
    Text,
    Boolean,
    SmallInteger,
    ForeignKey
    )

from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy.orm import (
    scoped_session,
    sessionmaker,
    )

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
    eur = Column(Integer)
    btc = Column(Integer)


class ActiveOrder(Base):

    BUY_ORDER = 0
    SELL_ORDER = 1

    __tablename__ = 'active_orders'
    id = Column(Integer, primary_key=True)
    time = Column(Integer, unique=True)
    type = Column(SmallInteger)
    amount = Column(Integer)
    price = Column(Integer)
    deleted = Column(Boolean, default=False)
    user_id = foreign_key_column(None, Integer, "users.id")


class Root(object):
    __acl__ = [(Allow, Everyone, 'view'),
               (Allow, 'group:editors', 'edit')]

    def __init__(self, request):
        pass