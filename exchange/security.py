import bcrypt


def hash_password(pw):
    pwhash = bcrypt.hashpw(pw.encode('utf8'), bcrypt.gensalt())
    return pwhash.decode('utf8')


def check_password(pw, hashed_pw):
    expected_hash = hashed_pw.encode('utf8')
    return bcrypt.checkpw(pw.encode('utf8'), expected_hash)


USERS = {'user1': hash_password('user1'),
         'user2': hash_password('user2')}
GROUPS = {'user': ['group:users']}


def group_finder(userid, request):
    if userid in USERS:
        return GROUPS.get(userid, [])