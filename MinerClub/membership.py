import requests

with open('members.csv') as f:
    members = f.read().split('\n')


def is_member(member_id):
    """
    Check is in member list
    """
    if member_id:
        return member_id in members
    return False


def get_mj_id(username):
    """
    Check mojang username exists - get mojang ID thingy.

    Returns None if no user with that name found.
    """
    p = requests.post("https://api.mojang.com/profiles/minecraft", data='["{}"]'.format(username))
    if p.json():
        return p.json()[0]['id']
    else:
        return None
