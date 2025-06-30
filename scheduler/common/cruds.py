from db.models import Session, Filter, AutoApplyConfig
from fabric.cruds.base import CRUDBase

SessionCRUD = CRUDBase(Session)
FilterCRUD = CRUDBase(Filter)
AutoApplyConfigCRUD = CRUDBase(AutoApplyConfig)
