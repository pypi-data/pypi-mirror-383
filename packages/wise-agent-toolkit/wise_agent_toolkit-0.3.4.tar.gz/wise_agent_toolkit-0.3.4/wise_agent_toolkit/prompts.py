CREATE_TRANSFER_PROMPT = """
This tool will create a transfer between accounts in Wise.

It takes the following arguments:
- target_account (int): The ID of the target recipient account.
- quote_uuid (str): The UUID of the quote.
- reference (str, optional): Reference for the transfer (optional, max 100 chars).
- source_account (int, optional): The ID of the source account (for refunds).
- customer_transaction_id (str, optional): A unique ID for this transaction. If not provided, a UUID will be generated.
- transfer_purpose (str, optional): Purpose of the transfer.
- transfer_purpose_sub (str, optional): Sub-purpose of the transfer.
- transfer_purpose_invoice (str, optional): Invoice number related to the transfer.
- source_of_funds (str, optional): Source of funds for the transfer.

Returns:
    The created transfer object from Wise.
"""

CREATE_QUOTE_PROMPT = """
This tool will create a quote for currency conversion in Wise.

It takes the following arguments:
- source_currency (str): The source currency code (3-letter ISO currency code).
- target_currency (str): The target currency code (3-letter ISO currency code).
- source_amount (float, optional): The amount in the source currency to be converted.
- target_amount (float, optional): The amount in the target currency to receive.
  Note: Provide either source_amount or target_amount, not both.
- target_account (int, optional): A unique recipient account identifier.
- profile_id (str, optional): The profile ID. If not provided, will be taken from context.
- pay_out (str, optional): The pay out method.
- preferred_pay_in (str, optional): The preferred pay in method.

Returns:
    The created quote object from Wise.
"""

UPDATE_QUOTE_PROMPT = """
This tool will update an existing quote for currency conversion in Wise.

It takes the following arguments:
- quote_id (str): The ID of the quote to update.
- source_currency (str, optional): The source currency code (3-letter ISO currency code).
- target_currency (str, optional): The target currency code (3-letter ISO currency code).
- source_amount (float, optional): The amount in the source currency to be converted.
- target_amount (float, optional): The amount in the target currency to receive.
- target_account (int, optional): A unique recipient account identifier.
- profile_id (str, optional): The profile ID. If not provided, will be taken from context.
- pay_out (str, optional): The pay out method.
- preferred_pay_in (str, optional): The preferred pay in method.

Note: All parameters except quote_id are optional. You can update any combination of fields.

Returns:
    The updated quote object from Wise.
"""

LIST_RECIPIENT_ACCOUNTS_PROMPT = """
This tool will list recipient accounts registered in Wise.

It takes the following arguments:
- profile_id (str, optional): The profile ID to list recipients for. If not provided, will be taken from context.
- currency (str, optional): Filter recipients by currency (3-letter ISO currency code).
- size (int, optional): Number of items per page for pagination.
- seek_position (int, optional): Position to start seeking from for pagination.

Returns:
    A paginated list of recipient accounts from Wise containing information about each recipient.
"""

CREATE_RECIPIENT_ACCOUNT_PROMPT = """
This tool will create a recipient account in Wise.

It takes the following arguments:
- account_holder_name (str): The recipient's full name.
- currency (str): 3 character currency code for the recipient's account.
- type (str): The type of recipient account, determined from the account requirements.
- profile_id (int, optional): The profile ID that the recipient will be created under. If not provided, will be taken from context.
- owned_by_customer (bool, optional): Whether this account is owned by the sending user.
- **kwargs: Dynamic fields based on account requirements. This can include:
  - details (dict): Account-specific details like legalType, email, IBAN, sort code, account number, etc.
  - address (dict): Address information with country, city, postCode, firstLine, etc.
  - Any other fields required by the specific currency route as returned by /v1/quotes/{quoteId}/account-requirements.

Returns:
    The created recipient account object from Wise.
"""

DEACTIVATE_RECIPIENT_ACCOUNT_PROMPT = """
This tool will deactivate a recipient account in Wise.

It takes the following arguments:
- account_id (int): The ID of the recipient account to deactivate.

Returns:
    The deactivated recipient account object from Wise.
"""

LIST_TRANSFERS_PROMPT = """
This tool will list transfers in Wise.

It takes the following arguments:
- profile (int, optional): The profile ID to list transfers for. If not provided, will be taken from context.
- status (str, optional): Filter transfers by status (e.g., incoming_payment_waiting, processing, outgoing_payment_sent, cancelled).
- source_currency (str, optional): Filter transfers by source currency (3-letter ISO currency code).
- target_currency (str, optional): Filter transfers by target currency (3-letter ISO currency code).
- created_date_start (date, optional): Filter transfers created on or after this date. Format: YYYY-MM-DD (e.g., 2025-09-01).
- created_date_end (date, optional): Filter transfers created before this date. Format: YYYY-MM-DD (e.g., 2025-10-01).
- limit (int, optional): Number of items per page for pagination (default 20, max 40).
- offset (int, optional): Offset for pagination (default 0). This is a row count offset (e.g., offset=100 skips the first 100 transfers), NOT a transfer ID.

Pagination Example:
- First page: offset=0, limit=20 (returns transfers 1-20)
- Second page: offset=20, limit=20 (returns transfers 21-40)
- Third page: offset=40, limit=20 (returns transfers 41-60)

Returns:
    A list of transfers from Wise containing information about each transfer.
"""

CANCEL_TRANSFER_PROMPT = """
This tool will cancel a transfer in Wise.

It takes the following arguments:
- transfer_id (int): The ID of the transfer to cancel.

Returns:
    The cancelled transfer object from Wise.

Note: Only transfers in certain states can be cancelled (e.g., incoming_payment_waiting, processing). 
Transfers that have already been sent or completed cannot be cancelled.
"""

GET_TRANSFER_BY_ID_PROMPT = """
This tool will retrieve a transfer by its ID in Wise.

It takes the following arguments:
- transfer_id (int): The ID of the transfer to retrieve.

Returns:
    The transfer object from Wise containing detailed information about the transfer including its status, amounts, currencies, and other transfer details.
"""

LIST_PROFILES_PROMPT = """
This tool will list profiles in Wise.

It takes no arguments and returns all profiles associated with the authenticated user.

Returns:
    A list of profiles from Wise containing information about each profile including profile ID, type, and details.
"""

GET_PROFILE_BY_ID_PROMPT = """
This tool will get a profile by ID from Wise.

It takes the following arguments:
- profile_id (int): The ID of the profile to retrieve.

Returns:
    The profile object from Wise containing information about the profile.
"""

GET_QUOTE_BY_ID_PROMPT = """
This tool will retrieve a quote by its ID in Wise.

It takes the following arguments:
- quote_id (str): The ID of the quote to retrieve.
- profile_id (str, optional): The profile ID. If not provided, will be taken from context.

Returns:
    The quote object from Wise containing all quote information including exchange rates, fees, and delivery times.
"""

GET_RECIPIENT_ACCOUNT_BY_ID_PROMPT = """
This tool will retrieve a specific recipient account by its ID in Wise.

It takes the following arguments:
- account_id (int): The ID of the recipient account to retrieve.

Returns:
    The recipient account object from Wise containing detailed information about the recipient.
"""

GET_ACCOUNT_REQUIREMENTS_PROMPT = """
This tool will get account requirements for a quote in Wise.

It takes the following arguments:
- quote_id (str): The ID of the quote to get account requirements for.
- address_required (bool, optional): Whether address is required for the recipient.

Returns:
    The account requirements object from Wise containing information about required fields for creating a recipient account for the specified quote.
"""

LIST_ACTIVITIES_PROMPT = """
This tool will list activities for a profile in Wise.

It takes the following arguments:
- profile_id (int, optional): The profile ID to list activities for. If not provided, will be taken from context.
- monetary_resource_type (str, optional): Filter by resource type.
- status (str, optional): Filter by activity status.
- since (datetime, optional): Filter activities created after this timestamp.
- until (datetime, optional): Filter activities created before this timestamp.
- next_cursor (str, optional): Pagination cursor for next page.
- size (int, optional): Number of results per page (default 10).

Returns:
    A list of activities from Wise containing information about each activity.
"""
