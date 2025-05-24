from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_cors import CORS

db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()
cors = CORS()

# Configuración adicional de JWT
@jwt.token_in_blocklist_loader
def check_if_token_revoked(jwt_header, jwt_payload):
    from app.models import RefreshToken
    jti = jwt_payload["jti"]
    token = RefreshToken.query.filter_by(token=jti, revocado=True).first()
    return token is not None