from app.hh_integration.client import models, schemas
from fabric.common.crud import CRUDBase


class ClientCrud(CRUDBase[models.Client, schemas.AuthorizedClientSchema]):
    def __init__(self):
        super().__init__(models.Client)


client_crud = ClientCrud()
