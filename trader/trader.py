from exchange.models import ActiveOrder, User


def run_trader():
    buy_orders = ActiveOrder.filter_order_by_desc_price_time(ActiveOrder.BUY_ORDER)

    if buy_orders.first() is None:
        print('No buy orders')
        return

    max_buy_price = buy_orders.first().price

    sell_orders = ActiveOrder.filter_order_by_price_time(max_buy_price, ActiveOrder.SELL_ORDER)

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
                        """
                        ActiveOrder.delete(sell_order_id)
                        User.update_balance_on_sell(sell_user_id, dict(eur=round(buy_price * sell_amount, 8),
                                                                       btc=round(sell_amount, 8)))

                        buy_amount -= sell_amount
                        ActiveOrder.update(buy_order_id, buy_amount)
                        User.update_balance_on_buy(buy_user_id, dict(eur=round(sell_amount * buy_price, 8),
                                                                     btc=round(sell_amount, 8)))
                        break

                    if sell_amount == buy_amount:
                        """
                        """
                        ActiveOrder.delete(sell_order_id)
                        User.update_balance_on_sell(sell_user_id, dict(eur=round(sell_price * sell_amount, 8),
                                                                       btc=round(sell_amount, 8)))

                        ActiveOrder.delete(buy_order_id)
                        User.update_balance_on_buy(buy_user_id, dict(eur=round(buy_amount * buy_price, 8),
                                                                     btc=round(buy_amount, 8)))
                        break

                    if sell_amount > buy_amount:
                        """
                        """
                        sell_amount -= buy_amount
                        ActiveOrder.update(sell_order_id, sell_amount)
                        User.update_balance_on_sell(sell_user_id, dict(eur=round(sell_price * sell_amount, 8),
                                                                       btc=round(sell_amount, 8)))

                        ActiveOrder.delete(buy_order_id)
                        User.update_balance_on_buy(buy_user_id, dict(eur=round(sell_amount * buy_price, 8),
                                                                     btc=round(sell_amount, 8)))
