import pdb

from typing import Iterable, List, TypedDict, Union

from stoobly_agent.app.proxy.test.context_abc import TestContextABC as TestContext
from stoobly_agent.app.proxy.test.helpers.request_component_names_facade import RequestComponentNamesFacade
from stoobly_agent.config.constants.lifecycle_hooks import ON_LENGTH_MATCH_ERROR, ON_PARAM_NAME_EXISTS_ERROR, ON_PARAM_NAME_MISSING_ERROR, ON_TYPE_MATCH_ERROR, ON_VALID_TYPE_ERROR, ON_VALUE_MATCH_ERROR
from stoobly_agent.lib.api.interfaces.endpoints import RequestComponentName, ResponseParamName
from stoobly_agent.lib.utils.python_to_ruby_type import convert

def build_match_context(context: TestContext, facade: RequestComponentNamesFacade):
    return MatchContext({ 
        'lifecycle_hooks': context.lifecycle_hooks,
        'path_key': '', 
        'query': '', 
        'request_component_names_facade': facade
    })

class IMatchContext(TypedDict):
    lifecycle_hooks: dict
    path_key: str
    query: str
    request_component_names_facade: RequestComponentNamesFacade

class MatchContext():

    def __init__(self, context: IMatchContext):
        self.keys = context.get('keys') or [] # List of visited keys
        self.path_key = context['path_key']
        self.query = context['query']

        self.__lifecycle_hooks = context.get('lifecycle_hooks') # Optional
        self.__request_component_names_facade = context['request_component_names_facade']

    @property
    def current_key(self):
        length = len(self.keys)

        if length == 0:
            return
        return self.keys[length - 1]

    @property
    def request_component_names_query_index(self):
        return self.__request_component_names_facade.query_index

    @property
    def request_component_name(self) -> Union[RequestComponentName, None]:
        return self.request_component_names_query_index.get(self.query)

    @property
    def children(self) -> List[RequestComponentName]:
        if self.query == '':
            return self.__request_component_names_facade.edges_index.get(None) or []

        component_names = self.request_component_names_query_index.get(self.query)
        if not component_names:
            return []

        if not isinstance(component_names, list):
            component_names = [component_names]

        edges_index = self.__request_component_names_facade.edges_index

        for component_name in component_names:
            edges = edges_index.get(component_name.get('id'))
            if edges:
                return edges

        return []

    def to_dict(self) -> IMatchContext:
        return {
            'lifecycle_hooks': self.__lifecycle_hooks,
            'keys': self.keys.copy(),
            'path_key': self.path_key,
            'query': self.query,
            'request_component_names_facade': self.__request_component_names_facade,
        }

    def clone(self):
        return __class__(self.to_dict())

    def visit_list(self, key):
        self.keys.append(key)
        self.path_key = f"{self.path_key}[{key}]"
        self.query = f"{self.query}[*]"

    def visit_dict(self, key):
        self.keys.append(key)
        self.path_key = '.'.join([self.path_key, key]) if len(self.path_key) > 0 else key
        self.query = '.'.join([self.query, key]) if len(self.query) > 0 else key

    def selected(self):
        return self.__request_component_names_facade.is_selected(self.query)

    def ignored(self, expected_value = None, actual_value = None):
        return not self.selected() or (not self.required() and self.__required_matches(expected_value, actual_value))

    def deterministic(self) -> bool:
        request_component_names_facade: RequestComponentNamesFacade = self.__request_component_names_facade
        if not request_component_names_facade or len(request_component_names_facade.all) == 0:
            return True

        query: str = self.query
        deterministic_param_names: ResponseParamName = request_component_names_facade.deterministic
        return self.__param_name_matches(query, deterministic_param_names)

    def required(self) -> bool:
        request_component_names_facade: RequestComponentNamesFacade = self.__request_component_names_facade
        if not request_component_names_facade or len(request_component_names_facade.all) == 0:
            return True

        query: str = self.query
        required_param_names: ResponseParamName = request_component_names_facade.required
        return self.__param_name_matches(query, required_param_names)

    ### Matchers

    def length_matches(self, v1, v2):
        return len(v1) == len(v2)

    def param_name_exists(self, key, actual):
        return key in actual

    def value_contract_matches(self, v1, contracts: Union[RequestComponentName, List[RequestComponentName]]):
        if not contracts:
            return True

        if not isinstance(contracts, list):
            contracts = [contracts]

        v_type = str(type(v1))
        for contract in contracts:
            if not contract.get('inferred_type'):
                return True

            if convert(v_type) == contract.get('inferred_type'):
                return True

        return False

    def value_fuzzy_matches(self, v1, v2):
        return type(v1) == type(v2)

    def value_matches(self, v1, v2):
        return v1 == v2

    def value_type_exists(self, value, valid_types: list):
        return type(value) in valid_types

    def value_type_matches(self, t1, t2):
        if type(t1) == type(t2):
            return True

        if t1 == dict or t2 == dict:
            return self.value_is_dict(t1) and self.value_is_dict(t2)

        if t1 == list or t2 == list:
            return self.value_is_list(t1) and self.value_is_list(t2)

        return False

    def value_is_dict(self, d):
        if isinstance(d, dict):
            return True
        return hasattr(d, 'items') and isinstance(d, Iterable)

    def value_is_list(self, l):
        if isinstance(l, list):
            return True
        return hasattr(l, 'sort') and isinstance(l, Iterable)

    ### Errors

    def handle_length_match_error(self, actual):
        handler = self.__lifecycle_hook(ON_LENGTH_MATCH_ERROR)

        if handler:
            return handler(self.clone(), actual)

    def handle_param_name_exists_error(self, actual):
        handler = self.__lifecycle_hook(ON_PARAM_NAME_EXISTS_ERROR)

        if handler:
            return handler(self.clone(), actual)

    def handle_param_name_missing_error(self, actual):
        handler = self.__lifecycle_hook(ON_PARAM_NAME_MISSING_ERROR)

        if handler:
            return handler(self.clone(), actual)

    def handle_type_match_error(self, actual):
        handler = self.__lifecycle_hook(ON_TYPE_MATCH_ERROR)

        if handler:
            return handler(self.clone(), actual)

    def handle_valid_type_error(self, actual):
        handler = self.__lifecycle_hook(ON_VALID_TYPE_ERROR)

        if handler:
            return handler(self.clone(), actual)
    
    ### Private

    def __lifecycle_hook(self, name):
        if not self.__lifecycle_hooks:
            return

        return self.__lifecycle_hooks.get(name)

    def __param_name_matches(self, query, param_names: List[ResponseParamName]) -> bool:
        for param_name in param_names:
            # Not all components will have a query property,
            # If query property does not exist, then use name property
            _query = param_name['query'] if 'query' in param_name else param_name['name']

            if _query == query:
                return True

        return False

    def __required_matches(self, v1, v2):
        if v1 == None or v2 == None:
            return v1 == v2
        return True