from models.generations import Generation

def get_by(**kwargs):
    return Generation.query.filter_by(**kwargs).first()

def get_all():
    return Generation.query.all()