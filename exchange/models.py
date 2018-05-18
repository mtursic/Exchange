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
    def update_balance(user_id, balance):
        return DBSession.query(User).filter_by(id=user_id).update(eur=balance['eur'], btc=balance['btc'])


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

    def filter_order_by_desc_price_time(type):
        return DBSession.query(ActiveOrder).filter_by(type=type, deleted=False).order_by(desc(ActiveOrder.price),
                                                                                         ActiveOrder.time)

    def filter_order_by_price_time(max_price, type):
        return DBSession.query(ActiveOrder).filter(ActiveOrder.price <= max_price) \
            .filter_by(type=type, deleted=False).order_by(ActiveOrder.price, ActiveOrder.time)

    def delete(order_id):
        return DBSession.query(ActiveOrder).filter_by(id=order_id).delete()

    def update(id, amount):
        return DBSession.query(ActiveOrder).filter_by(id=id).update(amount=amount)

    @staticmethod
    def validate_order(user_data, orders, price, amount, type):

        if price == '' or amount == '':
            return 'Please fill in both fields if you want to add an order'

        buy_orders = orders.filter_by(type=ActiveOrder.BUY_ORDER)
        sell_orders = orders.filter_by(type=ActiveOrder.SELL_ORDER)

        if type == ActiveOrder.BUY_ORDER:

            if sell_orders.filter_by(price=price).first():
                return 'Self trading is not allowed. Sell order with price ' + str(price) + ' exists'

            balance_eur = user_data.eur
            for buy_order in buy_orders:
                balance_eur -= float(buy_order.price) * float(buy_order.amount)

            # FEE check needs to be added here
            if balance_eur < 0:
                return 'Not enough EUR to place this order'

        elif type == ActiveOrder.SELL_ORDER:

            if buy_orders.filter_by(price=price).first():
                return 'Self trading is not allowed. Buy order with price ' + str(price) + ' exists'

            balance_btc = user_data.btc
            for sell_order in sell_orders:
                balance_btc -= float(sell_order.amount)

            # FEE check needs to be added
            if balance_btc < 0:
                return 'Not enough EUR to place this order'

        return ''


class Root(object):
    __acl__ = [(Allow, Everyone, 'view'),
               (Allow, 'group:editors', 'edit')]

    def __init__(self, request):
        pass
