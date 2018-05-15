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
from sqlalchemy import desc, func
from sqlalchemy.sql import label

from .models import DBSession, User, ActiveOrder
from .security import (
    USERS,
    check_password
)

from trader import trader

@view_defaults(renderer='templates/home.jinja2')
class TutorialViews:
    def __init__(self, request):
        self.request = request
        self.logged_in = request.authenticated_userid

    @view_config(route_name='home')
    def home(self):
        buy_orders = DBSession.query(ActiveOrder, label('total', func.sum(ActiveOrder.amount)), ActiveOrder.price)\
            .group_by(ActiveOrder.price).filter_by(type=ActiveOrder.BUY_ORDER, deleted=0)\
            .order_by(desc(ActiveOrder.price))

        sell_orders = DBSession.query(ActiveOrder, label('total', func.sum(ActiveOrder.amount)), ActiveOrder.price)\
            .group_by(ActiveOrder.price).filter_by(type=ActiveOrder.SELL_ORDER, deleted=0)\
            .order_by(ActiveOrder.price)

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
        request = self.request
        user_data = DBSession.query(User).filter_by(username=self.logged_in).one()
        message = ''

        if 'buy_form.submitted' in request.params:
            buy_price = request.params['buy_price']
            buy_amount = request.params['buy_amount']
            message = 'Buy order placed for ' + buy_amount + ' BTC for ' + buy_price + ' EUR'

            DBSession.add(ActiveOrder(time=int(datetime.now().timestamp()),
                                      type=ActiveOrder.BUY_ORDER,
                                      amount=buy_amount,
                                      price=buy_price,
                                      user_id=user_data.id
                                      ))
            trader.run_trader()

        if 'sell_form.submitted' in request.params:
            sell_price = request.params['sell_price']
            sell_amount = request.params['sell_amount']
            message = 'Sell order placed for ' + sell_amount + ' BTC for ' + sell_price + ' EUR'

            DBSession.add(ActiveOrder(time=int(datetime.now().timestamp()),
                                      type=ActiveOrder.SELL_ORDER,
                                      amount=sell_amount,
                                      price=sell_price,
                                      user_id=user_data.id))
            trader.run_trader()

        user_orders = DBSession.query(ActiveOrder).filter_by(user_id=user_data.id, deleted=0).order_by(ActiveOrder.time)

        return dict(
            user_data=user_data,
            url=request.application_url + '/user',
            message=message,
            user_orders=user_orders
        )

    @view_config(route_name='delete')
    def delete_order(self):
        order_id = self.request.matchdict['order_id']
        DBSession.query(ActiveOrder).filter_by(id=order_id).delete()
        # DBSession.query(ActiveOrder).filter_by(id=order_id).update({'deleted': True})

        return HTTPFound(location='user')
