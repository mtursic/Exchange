from datetime import datetime

from pyramid.httpexceptions import HTTPFound
from pyramid.security import (
    remember,
    forget,
)
from pyramid.view import (
    view_config,
    view_defaults
)

from trader import trader
from .models import User, ActiveOrder
from .security import (
    USERS,
    check_password
)


@view_defaults(renderer='templates/home.jinja2')
class ExchangeViews:
    def __init__(self, request):
        self.request = request
        self.logged_in = request.authenticated_userid
        self.message = ''

    @view_config(route_name='home')
    def home(self):
        buy_orders = ActiveOrder.sum_amount(ActiveOrder.BUY_ORDER)
        sell_orders = ActiveOrder.sum_amount(ActiveOrder.SELL_ORDER)

        return {'buy_orders': buy_orders, 'sell_orders': sell_orders}

    @view_config(route_name='login', renderer='templates/login.jinja2')
    def login(self):
        request = self.request
        login_url = request.route_url('login')
        referrer = request.url
        if referrer == login_url:
            referrer = '/'  # never use login form itself as came_from
        came_from = request.params.get('came_from', referrer)
        message = ''
        login = ''
        password = ''
        if 'form.submitted' in request.params:
            login = request.params['login']
            password = request.params['password']
            hashed_pw = USERS.get(login)
            if hashed_pw and check_password(password, hashed_pw):
                headers = remember(request, login)
                return HTTPFound(location='user',
                                 headers=headers)
            message = 'Failed login'

        return dict(
            name='Login',
            message=message,
            url=request.application_url + '/login',
            came_from=came_from,
            login=login,
            password=password,
        )

    @view_config(route_name='logout')
    def logout(self):
        request = self.request
        headers = forget(request)
        url = request.route_url('home')
        return HTTPFound(location=url,
                         headers=headers)

    @view_config(route_name='user', renderer='templates/user.jinja2')
    def user_view(self):
        print('user view')
        request = self.request
        user_data = User.get_by_username(self.logged_in)
        user_orders = ActiveOrder.filter_by_user_id_order_by_time(user_data.id)

        if 'buy_form.submitted' in request.params:
            buy_price = request.params['buy_price']
            buy_amount = request.params['buy_amount']

            self.message = ActiveOrder.validate_order(user_data, user_orders, buy_price, buy_amount,
                                                      ActiveOrder.BUY_ORDER)

            if self.message == '':
                ActiveOrder.add(dict(time=int(datetime.now().timestamp()),
                                     type=ActiveOrder.BUY_ORDER,
                                     amount=buy_amount,
                                     price=buy_price,
                                     user_id=user_data.id
                                     ))

                self.message = 'Buy order placed for ' + str(buy_amount) + ' BTC for ' + str(buy_price) + ' EUR'
                trader.run_trader()

        if 'sell_form.submitted' in request.params:
            sell_price = request.params['sell_price']
            sell_amount = request.params['sell_amount']

            self.message = ActiveOrder.validate_order(user_data, user_orders, sell_price, sell_amount,
                                                      ActiveOrder.SELL_ORDER)

            if self.message == '':
                ActiveOrder.add(dict(time=int(datetime.now().timestamp()),
                                     type=ActiveOrder.SELL_ORDER,
                                     amount=sell_amount,
                                     price=sell_price,
                                     user_id=user_data.id
                                     ))

                trader.run_trader()
                self.message = 'Sell order placed for ' + sell_amount + ' BTC for ' + sell_price + ' EUR'

        balance_eur = user_data.eur
        for buy_order in user_orders.filter_by(type=ActiveOrder.BUY_ORDER):
            balance_eur -= float(buy_order.price) * float(buy_order.amount)

        balance_btc = user_data.btc
        for sell_order in user_orders.filter_by(type=ActiveOrder.SELL_ORDER):
            balance_btc -= float(sell_order.amount)

        return dict(
            user_data=user_data,
            url=request.application_url + '/user',
            message=self.message,
            user_orders=user_orders,
            balance_eur=balance_eur,
            balance_btc=balance_btc
        )

    @view_config(route_name='delete')
    def delete_order(self):
        print('delete_order view')
        ActiveOrder.delete(self.request.matchdict['order_id'])
        return HTTPFound(location=self.request.application_url + '/user')
