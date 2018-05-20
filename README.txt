Exchange README
==================

Getting Started
---------------

- cd <directory containing this file>

- $VENV/bin/pip install -e .

- $VENV/bin/pserve development.ini

- $VENV/bin/initialize_tutorial_db.exe development.ini

Info
---------------
There are two users predefined to login into the exchange.
Authentication data:
username:
- 'user1', password: 'user1'
- 'user2', password: 'user2'

On front page there are active buy and sell orders. When user login, he is redirected to user 'dashboard' page where
he can place and remove his orders.