from typing import Literal, Optional
from typing_extensions import TypedDict

# Define Object type
Object = Literal[
  "transfers",
  "profiles",
  "quotes",
  "recipients",
  "balances",
  "activities",
]


# Define Permission type
class Permission(TypedDict, total=False):
  create: Optional[bool]
  update: Optional[bool]
  read: Optional[bool]


# Define BalancePermission type
class BalancePermission(TypedDict, total=False):
  read: Optional[bool]


# Define Actions type
class Actions(TypedDict, total=False):
  transfers: Optional[Permission]
  profiles: Optional[Permission]
  quotes: Optional[Permission]
  recipients: Optional[Permission]
  balances: Optional[BalancePermission]


# Define Context type
class Context(TypedDict, total=False):
  profile_id: Optional[str]


# Define Configuration type
class Configuration(TypedDict, total=False):
  actions: Optional[Actions]
  context: Optional[Context]


ACTIONS_ALL: Actions = {
  "transfers": {"create": True, "update": True, "read": True},
  "profiles": {"create": True, "update": True, "read": True},
  "quotes": {"create": True, "update": True, "read": True},
  "recipients": {"create": True, "update": True, "read": True, "delete": True},
  "balances": {"read": True},
  "activities": {"read": True},
}


def is_tool_allowed(tool, configuration):
  # Configuration should never be None now that we provide defaults
  for resource, permissions in tool.get("actions").items():
    if resource not in configuration.get("actions", {}):
      return False
    for permission in permissions:
      if (
        not configuration["actions"]
          .get(resource, {})
          .get(permission, False)
      ):
        return False
  return True
