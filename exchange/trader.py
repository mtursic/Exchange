from sqlalchemy import desc

from exchange import DBSession
from exchange.models import ActiveOrder


def run_trader():

    buy_orders = DBSession.query(ActiveOrder).filter_by(type=ActiveOrder.BUY_ORDER, deleted=False) \
        .order_by(desc(ActiveOrder.price), ActiveOrder.time)

    sell_orders = DBSession.query(ActiveOrder).filter_by(type=ActiveOrder.SELL_ORDER, deleted=False) \
        .order_by(ActiveOrder.price, ActiveOrder.time)

    max_buy_price = buy_orders.first().price
    min_sell_price = sell_orders.first().price

    print("buy: " + str(max_buy_price) + " sell: " + str(min_sell_price))

    if max_buy_price >= min_sell_price:
        print('Execute trade')

    # for sell_order in sell_orders:
    #
    #     print('price ' + str(sell_order.price) + ' date ' + str(sell_order.time) + " amount " + str(sell_order.amount))
    #
    #     for buy_order in buy_orders:
    #
    #         if buy_order.price >= sell_order.price:



run_trader()
