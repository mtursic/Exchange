from .models import DBSession, ActiveOrder, User


def buy_data_valid(user_id, buy_price, buy_amount):

    if buy_price == '' or buy_amount == '':
        return 'Please fill in both fields if you want to add BUY order'

    sell_order = DBSession.query(ActiveOrder).filter_by(user_id=user_id, type=ActiveOrder.SELL_ORDER,
                                                        price=buy_price, deleted=0)

    if sell_order.first():
        return 'Self trading is not allowed. Sell order with price ' + str(buy_price) + ' exists'

    user_data = DBSession.query(User).filter_by(id=user_id).one()
    eur = user_data.eur

    if eur - float(buy_price) * float(buy_amount) < 0:
        return 'Not enough EUR to place this order'

    return ''
