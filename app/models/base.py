from app.extensions import db

class BaseModel(db.Model):
    __abstract__ = True
    
    @classmethod
    def get_by_id(cls, id):
        return cls.query.get(id)
    
    def save(self):
        db.session.add(self)
        db.session.commit()
    
    def delete(self):
        db.session.delete(self)
        db.session.commit()