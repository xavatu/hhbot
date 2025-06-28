from db.cruds.base import CRUDBase
from db.models.client import User, Session

UserCRUD = CRUDBase(User)
SessionCRUD = CRUDBase(Session)
