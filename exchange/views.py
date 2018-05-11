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

from .security import (
    USERS,
    check_password
)

from .models import DBSession, User, ActiveOrder


@view_defaults(renderer='templates/home.jinja2')
class TutorialViews:
    def __init__(self, request):
        self.request = request
        self.logged_in = request.authenticated_userid

    @view_config(route_name='home')
    def home(self):
        buy_orders = DBSession.query(ActiveOrder, label('total', func.sum(ActiveOrder.amount)), ActiveOrder.price) \
            .group_by(ActiveOrder.price).filter_by(type=ActiveOrder.BUY_ORDER, deleted=0).order_by(ActiveOrder.price)

        sell_orders = DBSession.query(ActiveOrder, label('total', func.sum(ActiveOrder.amount)), ActiveOrder.price) \
            .group_by(ActiveOrder.price).filter_by(type=ActiveOrder.SELL_ORDER, deleted=0) \
            .order_by(desc(ActiveOrder.price))

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
        user_data = DBSession.query(User).filter_by(username=self.logged_in).one()
        return {'user_data': user_data}
