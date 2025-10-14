from stoobly_agent.app.settings import RemoteSettings
from stoobly_agent.lib.orm.request import Request

from .local_db.query_param_adapter import LocalDBQueryParamAdapter

class QueryParamResourceFactory():

  def __init__(self, settings: RemoteSettings):
    self.__remote_settings = settings

  def local_db(self) -> LocalDBQueryParamAdapter:
    return LocalDBQueryParamAdapter(Request)  