from app.extensions import db

class DBService:
    @staticmethod
    def call_proc(proc_name, args):
        """Ejecuta un procedimiento almacenado"""
        sql = f'CALL {proc_name}({",".join(["%s"]*len(args))})'
        result = db.session.execute(sql, args)
        db.session.commit()
        return result

    @staticmethod
    def get_view(view_name):
        """Obtiene datos de una vista"""
        return db.session.execute(f'SELECT * FROM {view_name}').fetchall()