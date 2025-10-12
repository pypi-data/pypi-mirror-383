from __future__ import annotations

import json
from typing import Optional

import wise_api_client
from pydantic import BaseModel
from wise_api_client import ApiClient

from .configuration import Context
from .functions import (
  create_transfer, create_quote, update_quote, list_recipient_accounts, create_recipient_account,
  deactivate_recipient_account, list_transfers, cancel_transfer, get_transfer_by_id, list_profiles,
  get_profile_by_id, get_quote_by_id, get_recipient_account_by_id, list_activities, get_account_requirements,
)


class WiseAPI(BaseModel):
  """Wrapper for Wise API"""

  _context: Context
  _api_client: ApiClient

  def __init__(self, api_key: str, host: str, context: Optional[Context]):
    super().__init__()

    self._context = context if context is not None else Context()

    configuration = wise_api_client.Configuration(
      access_token=api_key,
      host=host,
    )
    self._api_client = wise_api_client.ApiClient(configuration)

  def run(self, method: str, *args, **kwargs) -> str:
    if method == "create_transfer":
      transfer = create_transfer(self._api_client, self._context, *args, **kwargs).to_dict()
      return json.dumps(
        transfer,
        default=str  # to_dict() does not serialize datetime objects
      )
    elif method == "create_quote":
      quote = create_quote(self._api_client, self._context, *args, **kwargs).to_dict()
      return json.dumps(
        quote,
        default=str  # to_dict() does not serialize datetime objects
      )
    elif method == "update_quote":
      quote = update_quote(self._api_client, self._context, *args, **kwargs).to_dict()
      return json.dumps(
        quote,
        default=str  # to_dict() does not serialize datetime objects
      )
    elif method == "list_recipient_accounts":
      recipients = list_recipient_accounts(self._api_client, self._context, *args, **kwargs).to_dict()
      return json.dumps(recipients, default=str)  # to_dict() does not serialize datetime objects
    elif method == "create_recipient_account":
      recipient = create_recipient_account(self._api_client, self._context, *args, **kwargs).to_dict()
      return json.dumps(
        recipient,
        default=str  # to_dict() does not serialize datetime objects
      )
    elif method == "deactivate_recipient_account":
      recipient = deactivate_recipient_account(self._api_client, self._context, *args, **kwargs).to_dict()
      return json.dumps(
        recipient,
        default=str  # to_dict() does not serialize datetime objects
      )
    elif method == "list_transfers":
      transfers = list_transfers(self._api_client, self._context, *args, **kwargs)
      transfers = [] if transfers is None else transfers
      transfers = [t.to_dict() for t in transfers]
      return json.dumps(
        transfers,
        default=str  # to_dict() does not serialize datetime objects
      )
    elif method == "cancel_transfer":
      transfer = cancel_transfer(self._api_client, self._context, *args, **kwargs).to_dict()
      return json.dumps(
        transfer,
        default=str  # to_dict() does not serialize datetime objects
      )
    elif method == "get_transfer_by_id":
      transfer = get_transfer_by_id(self._api_client, self._context, *args, **kwargs).to_dict()
      return json.dumps(
        transfer,
        default=str  # to_dict() does not serialize datetime objects
      )
    elif method == "list_profiles":
      profiles = list_profiles(self._api_client, self._context)
      profiles = [] if profiles is None else profiles
      profiles = [p.to_dict() for p in profiles]
      return json.dumps(
        profiles,
        default=str  # to_dict() does not serialize datetime objects
      )
    elif method == "get_profile_by_id":
      profile = get_profile_by_id(self._api_client, self._context, *args, **kwargs).to_dict()
      return json.dumps(
        profile,
        default=str  # to_dict() does not serialize datetime objects
      )
    elif method == "get_quote_by_id":
      quote = get_quote_by_id(self._api_client, self._context, *args, **kwargs).to_dict()
      return json.dumps(
        quote,
        default=str  # to_dict() does not serialize datetime objects
      )
    elif method == "get_recipient_account_by_id":
      recipient = get_recipient_account_by_id(self._api_client, self._context, *args, **kwargs).to_dict()
      return json.dumps(
        recipient,
        default=str  # to_dict() does not serialize datetime objects
      )
    elif method == "get_account_requirements":
      requirements = get_account_requirements(self._api_client, self._context, *args, **kwargs)
      requirements = [] if requirements is None else requirements
      requirements = [r.to_dict() for r in requirements]
      return json.dumps(
        requirements,
        default=str  # to_dict() does not serialize datetime objects
      )
    elif method == "list_activities":
      activities = list_activities(self._api_client, self._context, *args, **kwargs).to_dict()
      return json.dumps(activities, default=str)  # to_dict() does not serialize datetime objects
    else:
      raise ValueError("Invalid method " + method)
