from exchange import DBSession
from exchange.models import User


def print_greetings():
    user = DBSession.query(User).filter_by(id=1).one()

    print("Happy Birthday " + user.username)


print_greetings()
