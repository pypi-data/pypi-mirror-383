from typing import Dict, List

from .prompts import (
  CREATE_TRANSFER_PROMPT, CREATE_QUOTE_PROMPT, LIST_RECIPIENT_ACCOUNTS_PROMPT, CREATE_RECIPIENT_ACCOUNT_PROMPT,
  LIST_TRANSFERS_PROMPT, CANCEL_TRANSFER_PROMPT, GET_TRANSFER_BY_ID_PROMPT, LIST_PROFILES_PROMPT,
  GET_PROFILE_BY_ID_PROMPT, GET_QUOTE_BY_ID_PROMPT, DEACTIVATE_RECIPIENT_ACCOUNT_PROMPT,
  GET_RECIPIENT_ACCOUNT_BY_ID_PROMPT, UPDATE_QUOTE_PROMPT, GET_ACCOUNT_REQUIREMENTS_PROMPT,
  LIST_ACTIVITIES_PROMPT,
)

from .schema import (
  CreateTransfer, CreateQuote, ListRecipientAccounts, CreateRecipientAccount, ListTransfers, CancelTransfer,
  GetTransferById, ListProfiles, GetProfileById, GetQuoteById, DeactivateRecipientAccount,
  GetRecipientAccountById, UpdateQuote, GetAccountRequirements, ListActivities,
)

tools: List[Dict] = [
  {
    "method": "create_transfer",
    "name": "Create Transfer",
    "description": CREATE_TRANSFER_PROMPT,
    "args_schema": CreateTransfer,
    "actions": {
      "transfers": {
        "create": True,
      }
    },
  },
  {
    "method": "create_quote",
    "name": "Create Quote",
    "description": CREATE_QUOTE_PROMPT,
    "args_schema": CreateQuote,
    "actions": {
      "quotes": {
        "create": True,
      }
    },
  },
  {
    "method": "update_quote",
    "name": "Update Quote",
    "description": UPDATE_QUOTE_PROMPT,
    "args_schema": UpdateQuote,
    "actions": {
      "quotes": {
        "update": True,
      }
    },
  },
  {
    "method": "list_recipient_accounts",
    "name": "List Recipient Accounts",
    "description": LIST_RECIPIENT_ACCOUNTS_PROMPT,
    "args_schema": ListRecipientAccounts,
    "actions": {
      "recipients": {
        "read": True,
      }
    },
  },
  {
    "method": "create_recipient_account",
    "name": "Create Recipient Account",
    "description": CREATE_RECIPIENT_ACCOUNT_PROMPT,
    "args_schema": CreateRecipientAccount,
    "actions": {
      "recipients": {
        "create": True,
      }
    },
  },
  {
    "method": "deactivate_recipient_account",
    "name": "Deactivate Recipient Account",
    "description": DEACTIVATE_RECIPIENT_ACCOUNT_PROMPT,
    "args_schema": DeactivateRecipientAccount,
    "actions": {
      "recipients": {
        "delete": True,
      }
    },
  },
  {
    "method": "list_transfers",
    "name": "List Transfers",
    "description": LIST_TRANSFERS_PROMPT,
    "args_schema": ListTransfers,
    "actions": {
      "transfers": {
        "read": True,
      }
    },
  },
  {
    "method": "cancel_transfer",
    "name": "Cancel Transfer",
    "description": CANCEL_TRANSFER_PROMPT,
    "args_schema": CancelTransfer,
    "actions": {
      "transfers": {
        "update": True,
      }
    },
  },
  {
    "method": "get_transfer_by_id",
    "name": "Get Transfer By ID",
    "description": GET_TRANSFER_BY_ID_PROMPT,
    "args_schema": GetTransferById,
    "actions": {
      "transfers": {
        "read": True,
      }
    },
  },
  {
    "method": "list_profiles",
    "name": "List Profiles",
    "description": LIST_PROFILES_PROMPT,
    "args_schema": ListProfiles,
    "actions": {
      "profiles": {
        "read": True,
      }
    },
  },
  {
    "method": "get_profile_by_id",
    "name": "Get Profile By ID",
    "description": GET_PROFILE_BY_ID_PROMPT,
    "args_schema": GetProfileById,
    "actions": {
      "profiles": {
        "read": True,
      }
    },
  },
  {
    "method": "get_quote_by_id",
    "name": "Get Quote By ID",
    "description": GET_QUOTE_BY_ID_PROMPT,
    "args_schema": GetQuoteById,
    "actions": {
      "quotes": {
        "read": True,
      }
    },
  },
  {
    "method": "get_recipient_account_by_id",
    "name": "Get Recipient Account By ID",
    "description": GET_RECIPIENT_ACCOUNT_BY_ID_PROMPT,
    "args_schema": GetRecipientAccountById,
    "actions": {
      "recipients": {
        "read": True,
      }
    },
  },
  {
    "method": "get_account_requirements",
    "name": "Get Account Requirements",
    "description": GET_ACCOUNT_REQUIREMENTS_PROMPT,
    "args_schema": GetAccountRequirements,
    "actions": {
      "recipients": {
        "read": True,
      }
    },
  },
  {
    "method": "list_activities",
    "name": "List Activities",
    "description": LIST_ACTIVITIES_PROMPT,
    "args_schema": ListActivities,
    "actions": {
      "activities": {
        "read": True,
      }
    },
  },
]
