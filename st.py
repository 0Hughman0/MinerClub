from MinerClub import app, db, mail
from MinerClub.database import Member, Whitelist

users = Member.query.all()
whitelist = Whitelist.query.all()


def u(member_id):
    """
    Get member by id
    """
    return Member.query.get(member_id)


def from_code(code):
    """
    Get member by sponsor code
    """

    return Member.query.filter(Member.sponsor_code == code).first()


def w(username):
    """
    Get whitelist entry by username
    """
    return Whitelist.query.get(username)


def summarise():
    for user in users:
        print("User {}:".format(user))
        for entry in user.users:
            print("\tGuest: {}".format(entry))
