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
                        sell_user = User.get_by_id(sell_user_id)
                        User.update_balance(sell_user_id, dict(eur=sell_user.eur + (buy_price * sell_amount),
                                                               btc=sell_user.btc - sell_amount))

                        buy_amount -= sell_amount
                        ActiveOrder.update(buy_order_id, buy_amount)
                        buy_user = User.get_by_id(buy_user_id)
                        User.update_balance(buy_user_id, dict(eur=buy_user.eur - sell_amount * buy_price,
                                                              btc=buy_user.btc + sell_amount))
                        break

                    if sell_amount == buy_amount:
                        """
                        """
                        ActiveOrder.delete(sell_order_id)
                        sell_user = User.get_by_id(sell_user_id)
                        User.update_balance(sell_user_id, dict(eur=sell_user.eur + (sell_price * sell_amount),
                                                               btc=sell_user.btc - sell_amount))

                        ActiveOrder.delete(buy_order_id)
                        buy_user = User.get_by_id(buy_user_id)
                        User.update_balance(buy_user_id, dict(eur=buy_user.eur - buy_amount * buy_price,
                                                              btc=buy_user.btc + buy_amount))
                        break

                    if sell_amount > buy_amount:
                        """
                        """
                        sell_amount -= buy_amount
                        ActiveOrder.update(sell_order_id, sell_amount)
                        sell_user = User.get_by_id(sell_user_id)
                        User.update_balance(sell_user_id, dict(eur=sell_user.eur + (sell_price * sell_amount),
                                                               btc=sell_user.btc - sell_amount))

                        ActiveOrder.delete(buy_order_id)
                        buy_user = User.get_by_id(buy_user_id)
                        User.update_balance(buy_user_id, dict(eur=buy_user.eur - sell_amount * buy_price,
                                                              btc=buy_user.btc + sell_amount))
