from models.generations import Generation


class GenerationRespository:
    @classmethod
    def get_by(cls, **kwargs):
        return Generation.query.filter_by(**kwargs).first()
    @classmethod
    def get_all(cls):
        return Generation.query.all()