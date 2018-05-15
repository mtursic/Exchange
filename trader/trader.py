from sqlalchemy import desc

from exchange import DBSession
from exchange.models import ActiveOrder, User


def run_trader():
    buy_orders = DBSession.query(ActiveOrder).filter_by(type=ActiveOrder.BUY_ORDER, deleted=False) \
        .order_by(desc(ActiveOrder.price), ActiveOrder.time)

    if buy_orders.first() is None:
        print('No buy orders')
        return

    max_buy_price = buy_orders.first().price

    sell_orders = DBSession.query(ActiveOrder).filter(ActiveOrder.price <= max_buy_price) \
        .filter_by(type=ActiveOrder.SELL_ORDER, deleted=False).order_by(ActiveOrder.price, ActiveOrder.time)

    if sell_orders.first():

        print('SELL')
        for sell_order in sell_orders:
            print('price ' + str(sell_order.price) + ' date ' + str(sell_order.time) + " amount " + str(
                sell_order.amount))

        print('BUY')
        for buy_order in buy_orders:
            print('price ' + str(buy_order.price) + ' date ' + str(buy_order.time) + " amount " + str(
                buy_order.amount))

        print('Execute trade')

        for sell_order in sell_orders:

            sell_order_id = sell_order.id
            sell_price = sell_order.price
            sell_amount = sell_order.amount
            sell_user_id = sell_order.user_id

            for buy_order in buy_orders:

                buy_order_id = buy_order.id
                buy_price = buy_order.price
                buy_amount = buy_order.amount
                buy_user_id = buy_order.user_id

                if sell_user_id == buy_user_id:
                    print('Same user trade WARNING!')
                    break

                if sell_price <= buy_price:

                    if sell_amount < buy_amount:
                        """
                        Sell order deleted.
                        Sell user balance:
                            BTC: - sell_amount
                            EUR:  + (buy_price * sell_amount) !!! sell price can be higher than buy
                        
                        Buy order updated:
                            amount: buy_amount - sell_amount
                        Buy user balance:
                            BTC: + buy_amount - sell_amount
                            EUR: - (buy_amount - sell_amount) * buy_price
                        """
                        DBSession.query(ActiveOrder).filter_by(id=sell_order_id).delete()
                        sell_user = DBSession.query(User).filter_by(id=sell_user_id).one()
                        DBSession.query(User).filter_by(id=sell_user_id) \
                            .update({'eur': sell_user.eur + (buy_price * sell_amount),
                                     'btc': sell_user.btc - sell_amount})

                        buy_amount -= sell_amount
                        DBSession.query(ActiveOrder).filter_by(id=buy_order_id).update({'amount': buy_amount})
                        buy_user = DBSession.query(User).filter_by(id=buy_user_id).one()
                        DBSession.query(User).filter_by(id=buy_user_id) \
                            .update({'eur': buy_user.eur - sell_amount * buy_price,
                                     'btc': buy_user.btc + sell_amount})
                        break

                    if sell_amount == buy_amount:
                        """
                        """
                        DBSession.query(ActiveOrder).filter_by(id=sell_order_id).delete()
                        sell_user = DBSession.query(User).filter_by(id=sell_user_id).one()
                        DBSession.query(User).filter_by(id=sell_user_id) \
                            .update({'eur': sell_user.eur + (sell_price * sell_amount),
                                     'btc': sell_user.btc - sell_amount})

                        DBSession.query(ActiveOrder).filter_by(id=buy_order_id).delete()
                        buy_user = DBSession.query(User).filter_by(id=buy_user_id).one()
                        DBSession.query(User).filter_by(id=buy_user_id) \
                            .update({'eur': buy_user.eur - buy_amount * buy_price,
                                     'btc': buy_user.btc + buy_amount})
                        break

                    if sell_amount > buy_amount:
                        """
                        """
                        sell_amount -= buy_amount
                        DBSession.query(ActiveOrder).filter_by(id=sell_order_id).update({'amount': sell_amount})
                        sell_user = DBSession.query(User).filter_by(id=sell_user_id).one()
                        DBSession.query(User).filter_by(id=sell_user_id) \
                            .update({'eur': sell_user.eur + (sell_price * sell_amount),
                                     'btc': sell_user.btc - sell_amount})

                        DBSession.query(ActiveOrder).filter_by(id=buy_order_id).delete()
                        buy_user = DBSession.query(User).filter_by(id=buy_user_id).one()
                        DBSession.query(User).filter_by(id=buy_user_id) \
                            .update({'eur': buy_user.eur - sell_amount * buy_price,
                                     'btc': buy_user.btc + sell_amount})
