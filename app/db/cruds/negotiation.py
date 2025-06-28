from db.cruds.base import CRUDBase
from db.models.negotiation import Filter, AutoApplyConfig

FilterCRUD = CRUDBase(Filter)
AutoApplyConfigCRUD = CRUDBase(AutoApplyConfig)
