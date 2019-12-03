with open('MinerClub/data/members.csv') as f:
    members = f.read().split('\n')


def is_member(member_id):
    if member_id:
        return member_id in members
    return False
