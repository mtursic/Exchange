from datetime import datetime

from exchange import DBSession
from exchange.models import User


def run_trader():
    print('Kwaj dej poj dej')

    user = DBSession.query(User)

    while True:
        if datetime.now().timestamp() % 60000 == 0:
            print('trade script execute')