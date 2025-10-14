from typing import List, TypedDict

DEFAULT_FORMAT = 'default'
JSON_FORMAT = 'json'

class Test(TypedDict):
  log: str
  passed: bool

class TestResponse(TypedDict):
  content: str
  latency: int
  status_code: int

class TestOutput(TypedDict):
  error: str
  expected_response: TestResponse
  passed: bool
  response: TestResponse
  tests: List[Test]

class ReplayOutput(TypedDict):
  content: str
  headers: dict
  method: str
  url: str