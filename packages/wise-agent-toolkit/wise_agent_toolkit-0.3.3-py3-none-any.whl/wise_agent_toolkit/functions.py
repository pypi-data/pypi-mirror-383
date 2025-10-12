from typing import Optional
from datetime import datetime

import wise_api_client

from .configuration import Context
import uuid


def create_transfer(
  api_client,
  context: Context,
  quote_uuid: str,
  target_account: int,
  source_account: Optional[int] = None,
  reference: Optional[str] = None,
  customer_transaction_id: Optional[str] = None,
  transfer_purpose: Optional[str] = None,
  transfer_purpose_sub: Optional[str] = None,
  transfer_purpose_invoice: Optional[str] = None,
  source_of_funds: Optional[str] = None
):
  """
  Create a transfer.

  Parameters:
          api_client: The Wise API client.
          context (Context): The context.
          quote_uuid (str): The UUID of the quote.
          target_account (int): The ID of the target recipient account.
          source_account (int, optional): The ID of the source account (refund).
          customer_transaction_id (str, optional): Customer transaction ID. If not provided, a UUID will be generated.
          reference (str, optional): Reference for the transfer (required).
          transfer_purpose (str, optional): Purpose of the transfer.
          transfer_purpose_sub (str, optional): Sub-purpose of the transfer.
          transfer_purpose_invoice (str, optional): Invoice number.
          source_of_funds (str, optional): Source of funds.

  Returns:
          The created transfer.
  """
  transfer_api = wise_api_client.TransfersApi(api_client)

  if not customer_transaction_id:
    customer_transaction_id = str(uuid.uuid4())

  details = None
  if reference:
    details = wise_api_client.TransferDetails(
      reference=reference,
      transfer_purpose=transfer_purpose,
      transfer_purpose_sub_transfer_purpose=transfer_purpose_sub,
      transfer_purpose_invoice_number=transfer_purpose_invoice,
      source_of_funds=source_of_funds
    )

  # Create CreateStandardTransferRequest object using Python field names
  create_standard_transfer_request = wise_api_client.CreateStandardTransferRequest(
    target_account=target_account,
    source_account=source_account,
    quote_uuid=quote_uuid,
    customer_transaction_id=customer_transaction_id,
    details=details
  )

  return transfer_api.create_transfer(create_standard_transfer_request)


def create_quote(
  api_client,
  context: Context,
  source_currency: str,
  target_currency: str,
  source_amount: Optional[float] = None,
  target_amount: Optional[float] = None,
  target_account: Optional[int] = None,
  pay_out: Optional[str] = None,
  preferred_pay_in: Optional[str] = None,
  profile_id: Optional[str] = None,
):
  """
  Create a quote with enhanced parameter support.

  Parameters:
      api_client: The Wise API client.
      context (Context): The context.
      source_currency (str): ISO 4217 three-letter currency code for source.
      target_currency (str): ISO 4217 three-letter currency code for target.
      source_amount (float): The amount in the source currency. Must be greater than 0.
      target_amount (float): The amount in the target currency. Must be greater than 0.
      target_account (int, optional): A unique recipient account identifier.
      pay_out (str, optional): Preferred payout method. Default is BANK_TRANSFER.
      preferred_pay_in (str, optional): Preferred payin method.
      profile_id (str, optional): The profile ID. If not provided, will be taken from context.

  Returns:
      The created quote.
  """
  quotes_api = wise_api_client.QuotesApi(api_client)

  # Get profile ID from context if not provided
  if not profile_id:
    profile_id = context.get("profile_id")
    if not profile_id:
      raise ValueError("Profile ID must be provided either as a parameter or in context.")

  # Either source_amount or target_amount should be provided, but not both
  if source_amount is not None and target_amount is not None:
    raise ValueError("Please provide either source_amount or target_amount, not both.")
  elif source_amount is None and target_amount is None:
    raise ValueError("Either source_amount or target_amount must be provided.")

  # Build quote request data
  quote_request_data = {
    "source_currency": source_currency,
    "target_currency": target_currency,
  }

  # Add optional fields
  if target_account is not None:
    quote_request_data["target_account"] = target_account

  if pay_out is not None:
    quote_request_data["pay_out"] = pay_out

  if preferred_pay_in is not None:
    quote_request_data["preferred_pay_in"] = preferred_pay_in

  if source_amount is not None:
    quote_request_data["source_amount"] = source_amount
    r = wise_api_client.CreateAuthenticatedSourceAmountQuoteRequest(**quote_request_data)
  else:
    quote_request_data["target_amount"] = target_amount
    r = wise_api_client.CreateAuthenticatedTargetAmountQuoteRequest(**quote_request_data)

  create_authenticated_quote_request = wise_api_client.CreateAuthenticatedQuoteRequest(r)
  return quotes_api.create_authenticated_quote(int(profile_id), create_authenticated_quote_request)


def update_quote(
  api_client,
  context: Context,
  quote_id: str,
  source_currency: str,
  target_currency: str,
  source_amount: Optional[float] = None,
  target_amount: Optional[float] = None,
  target_account: Optional[int] = None,
  pay_out: Optional[str] = None,
  preferred_pay_in: Optional[str] = None,
  profile_id: Optional[str] = None,
):
  """
  Update an existing quote with new parameters.

  Parameters:
      api_client: The Wise API client.
      context (Context): The context.
      quote_id (str): The ID of the quote to update.
      source_currency (str): ISO 4217 three-letter currency code for source.
      target_currency (str): ISO 4217 three-letter currency code for target.
      source_amount (float, optional): The amount in the source currency. Must be greater than 0.
      target_amount (float, optional): The amount in the target currency. Must be greater than 0.
      target_account (int, optional): A unique recipient account identifier.
      pay_out (str, optional): Preferred payout method. Default is BANK_TRANSFER.
      preferred_pay_in (str, optional): Preferred payin method.
      profile_id (str, optional): The profile ID. If not provided, will be taken from context.

  Returns:
      The updated quote.
  """
  quotes_api = wise_api_client.QuotesApi(api_client)

  # Get profile ID from context if not provided
  if not profile_id:
    profile_id = context.get("profile_id")
    if not profile_id:
      raise ValueError("Profile ID must be provided either as a parameter or in context.")

  # Either source_amount or target_amount should be provided, but not both
  if source_amount is not None and target_amount is not None:
    raise ValueError("Please provide either source_amount or target_amount, not both.")
  elif source_amount is None and target_amount is None:
    raise ValueError("Either source_amount or target_amount must be provided.")

  # Build quote request data
  quote_request_data = {
    "source_currency": source_currency,
    "target_currency": target_currency,
  }

  # Add optional fields
  if target_account is not None:
    quote_request_data["target_account"] = target_account

  if pay_out is not None:
    quote_request_data["pay_out"] = pay_out

  if preferred_pay_in is not None:
    quote_request_data["preferred_pay_in"] = preferred_pay_in

  if source_amount is not None:
    quote_request_data["source_amount"] = source_amount
    r = wise_api_client.CreateAuthenticatedSourceAmountQuoteRequest(**quote_request_data)
  else:
    quote_request_data["target_amount"] = target_amount
    r = wise_api_client.CreateAuthenticatedTargetAmountQuoteRequest(**quote_request_data)

  create_authenticated_quote_request = wise_api_client.CreateAuthenticatedQuoteRequest(r)
  # Note: The Wise API client might use the same request structure for updates as creates
  # This follows the pattern where PATCH operations reuse creation request models
  return quotes_api.update_quote(int(profile_id), create_authenticated_quote_request)


def create_recipient_account(
  api_client,
  context: Context,
  account_holder_name: str,
  currency: str,
  type: str,
  profile_id: Optional[int] = None,
  owned_by_customer: Optional[bool] = None,
  **kwargs
):
  """
  Create a recipient account.

  Parameters:
      api_client: The Wise API client.
      context (Context): The context.
      account_holder_name (str): The name of the account holder.
      currency (str): The currency code (3-letter ISO currency code).
      type (str): The type of recipient account.
      profile_id (int, optional): The profile ID. If not provided, will be taken from context.
      owned_by_customer (bool, optional): Whether this account is owned by the sending user.
      **kwargs: Dynamic fields based on account requirements (e.g., details, address, etc.).

  Returns:
      Recipient: The created recipient account.
  """
  recipients_api = wise_api_client.RecipientsApi(api_client)

  # Get profile ID from context if not provided
  if profile_id is None:
    profile_id = context.get("profile_id")
    if not profile_id:
      raise ValueError("Profile ID must be provided either as a parameter or in context.")

  # Create the request dictionary with fixed fields
  create_recipient_request_dict = {
    "accountHolderName": account_holder_name,
    "currency": currency,
    "type": type,
    "profile": int(profile_id)
  }

  # Add optional fixed field
  if owned_by_customer is not None:
    create_recipient_request_dict["ownedByCustomer"] = owned_by_customer

  # Add all dynamic fields
  create_recipient_request_dict.update(kwargs)

  # Create the request object from dictionary
  create_recipient_request = wise_api_client.CreateRecipientRequest.from_dict(create_recipient_request_dict)

  # Make the API call
  return recipients_api.create_recipient_account(create_recipient_request)


def list_recipient_accounts(
  api_client,
  context: Context,
  profile_id: Optional[str] = None,
  currency: Optional[str] = None,
  size: Optional[int] = None,
  seek_position: Optional[int] = None,
):
  """
  List recipient accounts.

  Parameters:
      api_client: The Wise API client.
      context (Context): The context.
      profile_id (str, optional): The profile ID. If not provided, will be taken from context.
      currency (str, optional): Filter by currency.
      size (int, optional): Number of items per page.
      seek_position (int, optional): Position to start seeking from.

  Returns:
      PaginatedRecipients: A paginated list of recipient accounts.
  """
  recipients_api = wise_api_client.RecipientsApi(api_client)

  # Get profile ID from context if not provided
  if not profile_id:
    profile_id = context.get("profile_id")
    if not profile_id:
      raise ValueError("Profile ID must be provided either as a parameter or in context.")

  # Make the API call
  return recipients_api.list_recipient_accounts(
    profile_id=int(profile_id),
    currency=currency,
    size=size,
    seek_position=seek_position
  )


def deactivate_recipient_account(
  api_client,
  context: Context,
  account_id: int,
):
  """
  Deactivate a recipient account.

  Parameters:
      api_client: The Wise API client.
      context (Context): The context.
      account_id (int): The ID of the recipient account to deactivate.

  Returns:
      The deactivated recipient account.
  """
  recipients_api = wise_api_client.RecipientsApi(api_client)

  # Make the API call
  return recipients_api.deactivate_recipient_account(account_id=account_id)


def list_transfers(
  api_client,
  context: Context,
  profile: Optional[int] = None,
  status: Optional[str] = None,
  source_currency: Optional[str] = None,
  target_currency: Optional[str] = None,
  created_date_start: Optional[datetime] = None,
  created_date_end: Optional[datetime] = None,
  limit: Optional[int] = None,
  offset: Optional[int] = None,
):
  """
  List transfers.

  Parameters:
      api_client: The Wise API client.
      context (Context): The context.
      profile (int, optional): The profile ID. If not provided, will be taken from context.
      status (str, optional): Filter by transfer status.
      source_currency (str, optional): Filter by source currency.
      target_currency (str, optional): Filter by target currency.
      created_date_start (datetime, optional): Filter transfers created after this date.
      created_date_end (datetime, optional): Filter transfers created before this date.
      limit (int, optional): Number of items per page (default 20).
      offset (int, optional): Offset for pagination (default 0).

  Returns:
      List of transfers.
  """
  transfers_api = wise_api_client.TransfersApi(api_client)

  # Get profile ID from context if not provided
  if not profile:
    profile = context.get("profile_id")
    if not profile:
      raise ValueError("Profile ID must be provided either as a parameter or in context.")
    profile = int(profile)

  # Make the API call
  return transfers_api.list_transfers(
    profile=profile,
    status=status,
    source_currency=source_currency,
    target_currency=target_currency,
    created_date_start=created_date_start,
    created_date_end=created_date_end,
    limit=limit,
    offset=offset
  )


def cancel_transfer(
  api_client,
  context: Context,
  transfer_id: int
):
  """
  Cancel a transfer.

  Parameters:
      api_client: The Wise API client.
      context (Context): The context.
      transfer_id (int): The ID of the transfer to cancel.

  Returns:
      The cancelled transfer object from Wise.
  """
  transfer_api = wise_api_client.TransfersApi(api_client)

  return transfer_api.cancel_transfer(transfer_id)


def get_transfer_by_id(
  api_client,
  context: Context,
  transfer_id: int
):
  """
  Get a transfer by its ID.

  Parameters:
      api_client: The Wise API client.
      context (Context): The context.
      transfer_id (int): The ID of the transfer to retrieve.

  Returns:
      The transfer object from Wise.
  """
  transfer_api = wise_api_client.TransfersApi(api_client)

  return transfer_api.get_transfer_by_id(transfer_id)


def list_profiles(
  api_client,
  context: Context,
):
  """
  List profiles.

  Parameters:
      api_client: The Wise API client.
      context (Context): The context.

  Returns:
      List: A list of profiles from Wise containing information about each profile.
  """
  profiles_api = wise_api_client.ProfilesApi(api_client)

  # Make the API call
  return profiles_api.list_profiles()


def get_profile_by_id(
  api_client,
  context: Context,
  profile_id: int,
):
  """
  Get a profile by ID.

  Parameters:
      api_client: The Wise API client.
      context (Context): The context.
      profile_id (int): The ID of the profile to retrieve.

  Returns:
      Profile: The profile object from Wise.
  """
  profiles_api = wise_api_client.ProfilesApi(api_client)

  return profiles_api.get_profile_by_id(profile_id)


def get_quote_by_id(
  api_client,
  context: Context,
  quote_id: str,
  profile_id: Optional[str] = None,
):
  """
  Get a quote by its ID.

  Parameters:
      api_client: The Wise API client.
      context (Context): The context.
      quote_id (str): The ID of the quote to retrieve.
      profile_id (str, optional): The profile ID. If not provided, will be taken from context.

  Returns:
      The quote object from Wise.
  """
  quotes_api = wise_api_client.QuotesApi(api_client)

  # Get profile ID from context if not provided
  if not profile_id:
    profile_id = context.get("profile_id")
    if not profile_id:
      raise ValueError("Profile ID must be provided either as a parameter or in context.")

  return quotes_api.get_quote_by_id(profile_id=int(profile_id), quote_id=quote_id)


def get_recipient_account_by_id(
  api_client,
  context: Context,
  account_id: int,
):
  """
  Get a recipient account by its ID.

  Parameters:
      api_client: The Wise API client.
      context (Context): The context.
      account_id (int): The ID of the recipient account to retrieve.

  Returns:
      The recipient account object from Wise.
  """
  recipients_api = wise_api_client.RecipientsApi(api_client)

  return recipients_api.get_recipient_account_by_id(account_id=account_id)


def get_account_requirements(
  api_client,
  context: Context,
  quote_id: str,
  address_required: Optional[bool] = None,
):
  """
  Get account requirements for a quote.

  Parameters:
      api_client: The Wise API client.
      context (Context): The context.
      quote_id (str): The ID of the quote to get account requirements for.
      address_required (bool, optional): Whether address is required for the recipient.

  Returns:
      The account requirements object from Wise containing information about required fields for creating a recipient account.
  """
  recipients_api = wise_api_client.RecipientsApi(api_client)

  return recipients_api.get_account_requirements(
    quote_id=quote_id,
    accept_minor_version=1,
    address_required=address_required
  )


def list_activities(
  api_client,
  context: Context,
  profile_id: Optional[int] = None,
  status: Optional[str] = None,
  created_date_start: Optional[datetime] = None,
  created_date_end: Optional[datetime] = None,
  limit: Optional[int] = None,
  offset: Optional[int] = None,
):
  """
  List activities for a profile.

  Parameters:
      api_client: The Wise API client.
      context (Context): The context.
      profile_id (int, optional): The profile ID. If not provided, will be taken from context.
      status (str, optional): Filter by activity status.
      created_date_start (datetime, optional): Filter activities created after this date.
      created_date_end (datetime, optional): Filter activities created before this date.
      limit (int, optional): Number of items per page (default 20).
      offset (int, optional): Offset for pagination (default 0).

  Returns:
      List of activities from Wise.
  """
  activities_api = wise_api_client.ActivitiesApi(api_client)

  # Get profile ID from context if not provided
  if not profile_id:
    profile_id = context.get("profile_id")
    if not profile_id:
      raise ValueError("Profile ID must be provided either as a parameter or in context.")
    profile_id = int(profile_id)

  # Make the API call
  return activities_api.list_activities(
    profile_id=profile_id,
    status=status,
    created_date_start=created_date_start,
    created_date_end=created_date_end,
    limit=limit,
    offset=offset
  )

