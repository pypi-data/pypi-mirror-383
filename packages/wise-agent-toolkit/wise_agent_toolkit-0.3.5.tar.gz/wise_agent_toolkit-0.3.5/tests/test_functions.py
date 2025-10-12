import unittest
from unittest import mock

from wise_agent_toolkit.functions import create_transfer, create_quote, update_quote, list_recipient_accounts, \
  create_recipient_account, deactivate_recipient_account, list_transfers, list_profiles, get_profile_by_id, \
  get_quote_by_id, \
  get_recipient_account_by_id, get_account_requirements, list_activities


class TestWiseFunctions(unittest.TestCase):

  def test_create_transfer(self):
    mock_api_client = mock.Mock()
    mock_transfer_api = mock.Mock()
    mock_response = {"id": "123", "status": "pending"}

    with mock.patch("wise_api_client.TransfersApi") as mock_transfers_api_class:
      mock_transfers_api_class.return_value = mock_transfer_api
      mock_transfer_api.create_transfer.return_value = mock_response

      context = {"account": "test-account"}
      target_account = 12345
      quote_uuid = "quote-uuid-123"
      reference = "Test Payment"

      result = create_transfer(
        api_client=mock_api_client,
        context=context,
        target_account=target_account,
        quote_uuid=quote_uuid,
        reference=reference
      )

      mock_transfers_api_class.assert_called_once_with(mock_api_client)

      mock_transfer_api.create_transfer.assert_called_once()

      call_args = mock_transfer_api.create_transfer.call_args[0][0]

      self.assertEqual(target_account, call_args.target_account)
      self.assertEqual(quote_uuid, call_args.quote_uuid)
      self.assertEqual(reference, call_args.details.reference)

      self.assertEqual(result, mock_response)

  def test_create_quote(self):
    mock_api_client = mock.Mock()
    mock_quotes_api = mock.Mock()
    mock_response = {"id": "quote-123", "rate": 1.2, "sourceAmount": 100, "targetAmount": 120}

    with mock.patch("wise_api_client.QuotesApi") as mock_quotes_api_class:
      mock_quotes_api_class.return_value = mock_quotes_api
      mock_quotes_api.create_authenticated_quote.return_value = mock_response

      # Test with source_amount
      context = {"profile_id": "456"}
      source_currency = "USD"
      target_currency = "EUR"
      source_amount = 100

      result = create_quote(
        api_client=mock_api_client,
        context=context,
        source_currency=source_currency,
        target_currency=target_currency,
        source_amount=source_amount
      )

      mock_quotes_api_class.assert_called_once_with(mock_api_client)
      mock_quotes_api.create_authenticated_quote.assert_called_once()

      call_args = mock_quotes_api.create_authenticated_quote.call_args
      self.assertEqual(int(context["profile_id"]), call_args[0][0])  # profile_id

      # Access the actual instance from the oneOf wrapper
      request_obj = call_args[0][1]
      actual_request = request_obj.actual_instance
      self.assertEqual(source_currency, actual_request.source_currency)
      self.assertEqual(target_currency, actual_request.target_currency)
      self.assertEqual(source_amount, actual_request.source_amount)

      self.assertEqual(result, mock_response)

  # def test_update_quote(self):
  #   mock_api_client = mock.Mock()
  #   mock_quotes_api = mock.Mock()
  #   mock_response = {"id": "quote-123", "rate": 1.25, "sourceAmount": 100, "targetAmount": 125}
  #
  #   with mock.patch("wise_api_client.QuotesApi") as mock_quotes_api_class:
  #     mock_quotes_api_class.return_value = mock_quotes_api
  #     mock_quotes_api.update_quote.return_value = mock_response
  #
  #     # Test with source_amount
  #     context = {"profile_id": "456"}
  #     quote_id = "quote-123"
  #     source_currency = "USD"
  #     target_currency = "EUR"
  #     source_amount = 100
  #
  #     result = update_quote(
  #       api_client=mock_api_client,
  #       context=context,
  #       quote_id=quote_id,
  #       source_currency=source_currency,
  #       target_currency=target_currency,
  #       source_amount=source_amount
  #     )
  #
  #     mock_quotes_api_class.assert_called_once_with(mock_api_client)
  #     mock_quotes_api.update_quote.assert_called_once()
  #
  #     call_args = mock_quotes_api.update_quote.call_args
  #     self.assertEqual(int(context["profile_id"]), call_args[0][0])  # profile_id
  #     self.assertEqual(quote_id, call_args[0][1])  # quote_id
  #
  #     # Access the actual instance from the oneOf wrapper
  #     request_obj = call_args[0][2]
  #     actual_request = request_obj.actual_instance
  #     self.assertEqual(source_currency, actual_request.source_currency)
  #     self.assertEqual(target_currency, actual_request.target_currency)
  #     self.assertEqual(source_amount, actual_request.source_amount)
  #
  #     self.assertEqual(result, mock_response)

  def test_list_recipient_accounts(self):
    mock_api_client = mock.Mock()
    mock_recipients_api = mock.Mock()
    mock_response = {
      "items": [
        {"id": "111", "accountHolderName": "Test Recipient", "currency": "USD"},
        {"id": "222", "accountHolderName": "Another Recipient", "currency": "EUR"}
      ],
      "itemsPerPage": 2,
      "totalItems": 2,
      "totalPages": 1
    }

    with mock.patch("wise_api_client.RecipientsApi") as mock_recipients_api_class:
      mock_recipients_api_class.return_value = mock_recipients_api
      mock_recipients_api.list_recipient_accounts.return_value = mock_response

      # Test with explicit profile_id
      context = {}
      profile_id = "456"
      currency = "USD"
      size = 10
      seek_position = 0

      result = list_recipient_accounts(
        api_client=mock_api_client,
        context=context,
        profile_id=profile_id,
        currency=currency,
        size=size,
        seek_position=seek_position
      )

      mock_recipients_api_class.assert_called_once_with(mock_api_client)
      mock_recipients_api.list_recipient_accounts.assert_called_once_with(
        profile_id=int(profile_id),
        currency=currency,
        size=size,
        seek_position=seek_position
      )

      self.assertEqual(result, mock_response)

      # Reset mocks for next test
      mock_recipients_api_class.reset_mock()
      mock_recipients_api.list_recipient_accounts.reset_mock()

      # Test with profile_id from context
      context = {"profile_id": "789"}

      result = list_recipient_accounts(
        api_client=mock_api_client,
        context=context,
        currency=currency
      )

      mock_recipients_api.list_recipient_accounts.assert_called_once_with(
        profile_id=int(context["profile_id"]),
        currency=currency,
        size=None,
        seek_position=None
      )

      self.assertEqual(result, mock_response)

  def test_create_recipient_account(self):
    mock_api_client = mock.Mock()
    mock_recipients_api = mock.Mock()
    mock_response = {
      "id": "recipient-123",
      "account_holder_name": "John Doe",
      "currency": "USD",
      "country": "US",
      "type": "email",
      "details": {
        "email": "john.doe@example.com",
        "address": {
          "country": "US",
          "city": "New York",
          "postCode": "10001",
          "firstLine": "123 Main St"
        }
      }
    }

    with mock.patch("wise_api_client.RecipientsApi") as mock_recipients_api_class:
      mock_recipients_api_class.return_value = mock_recipients_api
      mock_recipients_api.create_recipient_account.return_value = mock_response

      context = {"profile_id": "456"}

      # Test with new function signature using individual parameters and kwargs
      result = create_recipient_account(
        api_client=mock_api_client,
        context=context,
        account_holder_name="John Doe",
        currency="USD",
        type="email",
        owned_by_customer=True,
        details={
          "legalType": "PRIVATE",
          "email": "john.doe@example.com",
          "address": {
            "country": "US",
            "city": "New York",
            "postCode": "10001",
            "firstLine": "123 Main St"
          }
        }
      )

      mock_recipients_api_class.assert_called_once_with(mock_api_client)
      mock_recipients_api.create_recipient_account.assert_called_once()

      call_args = mock_recipients_api.create_recipient_account.call_args[0][0]
      self.assertEqual("John Doe", call_args.account_holder_name)
      self.assertEqual("USD", call_args.currency)
      self.assertEqual("email", call_args.type)
      self.assertEqual(int(context["profile_id"]), call_args.profile)
      self.assertEqual(True, call_args.owned_by_customer)

      self.assertEqual(result, mock_response)

  def test_deactivate_recipient_account(self):
    mock_api_client = mock.Mock()
    mock_recipients_api = mock.Mock()
    mock_response = {
      "id": 12345,
      "account_holder_name": "John Doe",
      "currency": "USD",
      "type": "email",
      "active": False,
      "status": "inactive"
    }

    with mock.patch("wise_api_client.RecipientsApi") as mock_recipients_api_class:
      mock_recipients_api_class.return_value = mock_recipients_api
      mock_recipients_api.deactivate_recipient_account.return_value = mock_response

      context = {}
      account_id = 12345

      result = deactivate_recipient_account(
        api_client=mock_api_client,
        context=context,
        account_id=account_id
      )

      mock_recipients_api_class.assert_called_once_with(mock_api_client)
      mock_recipients_api.deactivate_recipient_account.assert_called_once_with(account_id=account_id)

      self.assertEqual(result, mock_response)

  def test_list_transfers(self):
    mock_api_client = mock.Mock()
    mock_transfers_api = mock.Mock()
    mock_response = [
      {
        "id": "transfer-123",
        "status": "outgoing_payment_sent",
        "sourceAmount": 100.0,
        "sourceCurrency": "USD",
        "targetAmount": 85.0,
        "targetCurrency": "EUR",
        "createdAt": "2023-10-01T12:00:00Z"
      },
      {
        "id": "transfer-456",
        "status": "funds_converted",
        "sourceAmount": 200.0,
        "sourceCurrency": "GBP",
        "targetAmount": 230.0,
        "targetCurrency": "USD",
        "createdAt": "2023-10-02T15:30:00Z"
      }
    ]

    with mock.patch("wise_api_client.TransfersApi") as mock_transfers_api_class:
      mock_transfers_api_class.return_value = mock_transfers_api
      mock_transfers_api.list_transfers.return_value = mock_response

      # Test with explicit profile parameter
      context = {}
      profile = 456
      status = "outgoing_payment_sent"
      source_currency = "USD"
      target_currency = "EUR"
      limit = 10
      offset = 0

      result = list_transfers(
        api_client=mock_api_client,
        context=context,
        profile=profile,
        status=status,
        source_currency=source_currency,
        target_currency=target_currency,
        limit=limit,
        offset=offset
      )

      mock_transfers_api_class.assert_called_once_with(mock_api_client)
      mock_transfers_api.list_transfers.assert_called_once_with(
        profile=profile,
        status=status,
        source_currency=source_currency,
        target_currency=target_currency,
        created_date_start=None,
        created_date_end=None,
        limit=limit,
        offset=offset
      )

      self.assertEqual(result, mock_response)

      # Reset mocks for next test
      mock_transfers_api_class.reset_mock()
      mock_transfers_api.list_transfers.reset_mock()

      # Test with profile_id from context
      context = {"profile_id": "789"}

      result = list_transfers(
        api_client=mock_api_client,
        context=context,
        status="funds_converted"
      )

      mock_transfers_api.list_transfers.assert_called_once_with(
        profile=int(context["profile_id"]),
        status="funds_converted",
        source_currency=None,
        target_currency=None,
        created_date_start=None,
        created_date_end=None,
        limit=None,
        offset=None
      )

      self.assertEqual(result, mock_response)

      # Reset mocks for error test
      mock_transfers_api_class.reset_mock()
      mock_transfers_api.list_transfers.reset_mock()

      # Test error when no profile_id is provided
      context = {}

      with self.assertRaises(ValueError) as cm:
        list_transfers(
          api_client=mock_api_client,
          context=context
        )

      self.assertEqual(str(cm.exception), "Profile ID must be provided either as a parameter or in context.")

  def test_list_profiles(self):
    mock_api_client = mock.Mock()
    mock_profiles_api = mock.Mock()
    mock_response = [
      {
        "id": 123,
        "type": "personal",
        "details": {
          "firstName": "John",
          "lastName": "Doe",
          "dateOfBirth": "1990-01-01",
          "phoneNumber": "+1234567890"
        }
      },
      {
        "id": 456,
        "type": "business",
        "details": {
          "name": "Acme Corp",
          "registrationNumber": "12345678",
          "companyType": "LIMITED",
          "companyRole": "OWNER"
        }
      }
    ]

    with mock.patch("wise_api_client.ProfilesApi") as mock_profiles_api_class:
      mock_profiles_api_class.return_value = mock_profiles_api
      mock_profiles_api.list_profiles.return_value = mock_response

      context = {}

      result = list_profiles(
        api_client=mock_api_client,
        context=context
      )

      mock_profiles_api_class.assert_called_once_with(mock_api_client)
      mock_profiles_api.list_profiles.assert_called_once_with()

      self.assertEqual(result, mock_response)

  def test_get_profile_by_id(self):
    mock_api_client = mock.Mock()
    mock_profiles_api = mock.Mock()
    mock_response = {
      "id": 123,
      "type": "personal",
      "details": {
        "firstName": "John",
        "lastName": "Doe",
        "dateOfBirth": "1990-01-01",
        "phoneNumber": "+1234567890"
      }
    }

    with mock.patch("wise_api_client.ProfilesApi") as mock_profiles_api_class:
      mock_profiles_api_class.return_value = mock_profiles_api
      mock_profiles_api.get_profile_by_id.return_value = mock_response

      context = {}
      profile_id = 123

      result = get_profile_by_id(
        api_client=mock_api_client,
        context=context,
        profile_id=profile_id
      )

      mock_profiles_api_class.assert_called_once_with(mock_api_client)
      mock_profiles_api.get_profile_by_id.assert_called_once_with(profile_id)

      self.assertEqual(result, mock_response)

  def test_get_quote_by_id(self):
    mock_api_client = mock.Mock()
    mock_quotes_api = mock.Mock()
    mock_response = {
      "id": "quote-123",
      "sourceCurrency": "USD",
      "targetCurrency": "EUR",
      "sourceAmount": 100.0,
      "targetAmount": 85.0,
      "rate": 0.85,
      "createdTime": "2023-10-01T12:00:00Z",
      "guaranteedTargetAmount": True,
      "providedAmountType": "SOURCE"
    }

    with mock.patch("wise_api_client.QuotesApi") as mock_quotes_api_class:
      mock_quotes_api_class.return_value = mock_quotes_api
      mock_quotes_api.get_quote_by_id.return_value = mock_response

      # Test with explicit profile_id
      context = {}
      quote_id = "quote-123"
      profile_id = "456"

      result = get_quote_by_id(
        api_client=mock_api_client,
        context=context,
        quote_id=quote_id,
        profile_id=profile_id
      )

      mock_quotes_api_class.assert_called_once_with(mock_api_client)
      mock_quotes_api.get_quote_by_id.assert_called_once_with(
        profile_id=int(profile_id),
        quote_id=quote_id
      )

      self.assertEqual(result, mock_response)

      # Reset mocks for next test
      mock_quotes_api_class.reset_mock()
      mock_quotes_api.get_quote_by_id.reset_mock()

      # Test with profile_id from context
      context = {"profile_id": "789"}

      result = get_quote_by_id(
        api_client=mock_api_client,
        context=context,
        quote_id=quote_id
      )

      mock_quotes_api.get_quote_by_id.assert_called_once_with(
        profile_id=int(context["profile_id"]),
        quote_id=quote_id
      )

      self.assertEqual(result, mock_response)

      # Reset mocks for error test
      mock_quotes_api_class.reset_mock()
      mock_quotes_api.get_quote_by_id.reset_mock()

      # Test error when no profile_id is provided
      context = {}

      with self.assertRaises(ValueError) as cm:
        get_quote_by_id(
          api_client=mock_api_client,
          context=context,
          quote_id=quote_id
        )

      self.assertEqual(str(cm.exception), "Profile ID must be provided either as a parameter or in context.")

  def test_get_recipient_account_by_id(self):
    mock_api_client = mock.Mock()
    mock_recipients_api = mock.Mock()
    mock_response = {
      "id": 12345,
      "account_holder_name": "John Doe",
      "currency": "USD",
      "country": "US",
      "type": "email",
      "active": True,
      "details": {
        "email": "john.doe@example.com",
        "address": {
          "country": "US",
          "city": "New York",
          "postCode": "10001",
          "firstLine": "123 Main St"
        }
      }
    }

    with mock.patch("wise_api_client.RecipientsApi") as mock_recipients_api_class:
      mock_recipients_api_class.return_value = mock_recipients_api
      mock_recipients_api.get_recipient_account_by_id.return_value = mock_response

      context = {}
      account_id = 12345

      result = get_recipient_account_by_id(
        api_client=mock_api_client,
        context=context,
        account_id=account_id
      )

      mock_recipients_api_class.assert_called_once_with(mock_api_client)
      mock_recipients_api.get_recipient_account_by_id.assert_called_once_with(account_id=account_id)

      self.assertEqual(result, mock_response)

  def test_get_account_requirements(self):
    mock_api_client = mock.Mock()
    mock_recipients_api = mock.Mock()
    mock_response = [
      {
        "type": "email",
        "fields": [
          {
            "name": "email",
            "group": [
              {
                "key": "email",
                "type": "text",
                "required": True,
                "displayFormat": None,
                "example": "john.doe@example.com",
                "minLength": None,
                "maxLength": None,
                "validationRegexp": None,
                "validationAsync": None,
                "valuesAllowed": None
              }
            ]
          }
        ]
      },
      {
        "type": "iban",
        "fields": [
          {
            "name": "iban",
            "group": [
              {
                "key": "iban",
                "type": "text",
                "required": True,
                "displayFormat": None,
                "example": "DE89370400440532013000",
                "minLength": None,
                "maxLength": None,
                "validationRegexp": None,
                "validationAsync": None,
                "valuesAllowed": None
              }
            ]
          }
        ]
      }
    ]

    with mock.patch("wise_api_client.RecipientsApi") as mock_recipients_api_class:
      mock_recipients_api_class.return_value = mock_recipients_api
      mock_recipients_api.get_account_requirements.return_value = mock_response

      context = {}
      quote_id = "quote-123"

      # Test without address_required
      result = get_account_requirements(
        api_client=mock_api_client,
        context=context,
        quote_id=quote_id
      )

      mock_recipients_api_class.assert_called_once_with(mock_api_client)
      mock_recipients_api.get_account_requirements.assert_called_once_with(
        quote_id=quote_id,
        accept_minor_version=1,
        address_required=None
      )

      self.assertEqual(result, mock_response)

      # Reset mocks for next test
      mock_recipients_api_class.reset_mock()
      mock_recipients_api.get_account_requirements.reset_mock()

      # Test with address_required=True
      result = get_account_requirements(
        api_client=mock_api_client,
        context=context,
        quote_id=quote_id,
        address_required=True
      )

      mock_recipients_api.get_account_requirements.assert_called_once_with(
        quote_id=quote_id,
        accept_minor_version=1,
        address_required=True
      )

      self.assertEqual(result, mock_response)

  def test_list_activities(self):
    mock_api_client = mock.Mock()
    mock_activities_api = mock.Mock()
    mock_response = [
      {
        "id": "activity-123",
        "status": "COMPLETED",
        "type": "TRANSFER",
        "createdAt": "2023-10-01T12:00:00Z",
        "details": {
          "transferId": 12345,
          "amount": 100.0,
          "currency": "USD"
        }
      },
      {
        "id": "activity-456",
        "status": "PENDING",
        "type": "BALANCE_ADJUSTMENT",
        "createdAt": "2023-10-02T15:30:00Z",
        "details": {
          "amount": 50.0,
          "currency": "EUR"
        }
      }
    ]

    with mock.patch("wise_api_client.ActivitiesApi") as mock_activities_api_class:
      mock_activities_api_class.return_value = mock_activities_api
      mock_activities_api.list_activities.return_value = mock_response

      # Test with explicit profile_id parameter
      context = {}
      profile_id = 456
      status = "COMPLETED"
      monetary_resource_type = "TRANSFER"
      size = 10
      next_cursor = "cursor123"

      result = list_activities(
        api_client=mock_api_client,
        context=context,
        profile_id=profile_id,
        status=status,
        monetary_resource_type=monetary_resource_type,
        size=size,
        next_cursor=next_cursor
      )

      mock_activities_api_class.assert_called_once_with(mock_api_client)
      mock_activities_api.list_activities.assert_called_once_with(
        profile_id=profile_id,
        monetary_resource_type=monetary_resource_type,
        status=status,
        since=None,
        until=None,
        next_cursor=next_cursor,
        size=size
      )

      self.assertEqual(result, mock_response)

      # Reset mocks for next test
      mock_activities_api_class.reset_mock()
      mock_activities_api.list_activities.reset_mock()

      # Test with profile_id from context
      context = {"profile_id": "789"}

      result = list_activities(
        api_client=mock_api_client,
        context=context,
        status="PENDING"
      )

      mock_activities_api.list_activities.assert_called_once_with(
        profile_id=int(context["profile_id"]),
        monetary_resource_type=None,
        status="PENDING",
        since=None,
        until=None,
        next_cursor=None,
        size=None
      )

      self.assertEqual(result, mock_response)

      # Reset mocks for error test
      mock_activities_api_class.reset_mock()
      mock_activities_api.list_activities.reset_mock()

      # Test error when no profile_id is provided
      context = {}

      with self.assertRaises(ValueError) as cm:
        list_activities(
          api_client=mock_api_client,
          context=context
        )

      self.assertEqual(str(cm.exception), "Profile ID must be provided either as a parameter or in context.")


if __name__ == "__main__":
  unittest.main()
