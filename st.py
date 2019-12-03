from MinerClub import app, db, mail
from MinerClub.site import Member, Whitelist


users = Member.query.all()
whitelist = Whitelist.query.all()


def u(member_id):
    return Member.query.get(member_id)


def w(username):
    return Whitelist.query.get(username)
