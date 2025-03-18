from models.drawing import Drawing


def get_by(**kwargs):
    return Drawing.query.filter_by(**kwargs).first()