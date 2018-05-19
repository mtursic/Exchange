import logging

from exchange.models import ActiveOrder, User

log = logging.getLogger(__name__)


def run_trader():
    """
    Trading script. First read all buy orders and sort them by descending price and time. If there are no buy order
    script ends. If there are some buy orders 'max value' of them is read and sell orders which have price equal or
    BIGGER than 'max value' are fetched. Looping through all suitable orders executing trades according to amount.
    """
    buy_orders = ActiveOrder.filter_order_by_desc_price_time(ActiveOrder.BUY_ORDER)

    if buy_orders.first() is None:
        log.info('No buy orders')
        return

    max_buy_price = buy_orders.first().price

    sell_orders = ActiveOrder.filter_order_by_price_time(max_buy_price, ActiveOrder.SELL_ORDER)

    if sell_orders.first():

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
                    log.info('Same user trade WARNING!')
                    break

                log.info('Trades executed.')

                if sell_price <= buy_price:

                    if sell_amount < buy_amount:
                        ActiveOrder.delete(sell_order_id)
                        fee = buy_price * sell_amount * ActiveOrder.FEE
                        User.update_balance_on_sell(sell_user_id, dict(eur=round(buy_price * sell_amount, 8),
                                                                       btc=round(sell_amount, 8),
                                                                       fee=round(fee, 8)))

                        buy_amount -= sell_amount
                        ActiveOrder.update(buy_order_id, buy_amount)
                        fee = buy_price * sell_amount * ActiveOrder.FEE
                        User.update_balance_on_buy(buy_user_id, dict(eur=round(buy_price * sell_amount, 8),
                                                                     btc=round(sell_amount, 8),
                                                                     fee=round(fee, 8)))
                        break

                    if sell_amount == buy_amount:
                        ActiveOrder.delete(sell_order_id)
                        fee = buy_price * sell_amount * ActiveOrder.FEE
                        User.update_balance_on_sell(sell_user_id, dict(eur=round(buy_price * sell_amount, 8),
                                                                       btc=round(sell_amount, 8),
                                                                       fee=round(fee, 8)))

                        ActiveOrder.delete(buy_order_id)
                        fee = buy_amount * buy_price * ActiveOrder.FEE
                        User.update_balance_on_buy(buy_user_id, dict(eur=round(buy_amount * buy_price, 8),
                                                                     btc=round(buy_amount, 8),
                                                                     fee=round(fee, 8)))
                        break

                    if sell_amount > buy_amount:
                        sell_amount -= buy_amount
                        ActiveOrder.update(sell_order_id, sell_amount)
                        fee = buy_price * buy_amount * ActiveOrder.FEE
                        User.update_balance_on_sell(sell_user_id, dict(eur=round(buy_price * buy_amount, 8),
                                                                       btc=round(buy_amount, 8),
                                                                       fee=round(fee, 8)))

                        ActiveOrder.delete(buy_order_id)
                        fee = buy_amount * buy_price * ActiveOrder.FEE
                        User.update_balance_on_buy(buy_user_id, dict(eur=round(buy_amount * buy_price, 8),
                                                                     btc=round(buy_amount, 8),
                                                                     fee=round(fee, 8)))
