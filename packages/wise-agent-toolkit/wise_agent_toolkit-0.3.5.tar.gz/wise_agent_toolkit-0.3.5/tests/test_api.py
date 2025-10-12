import unittest
from unittest import mock
import json

from wise_agent_toolkit.api import WiseAPI
from wise_agent_toolkit.tools import tools


class TestWiseAPI(unittest.TestCase):
  """Test that all registered tools have corresponding cases in the API run method."""

  def setUp(self):
    """Set up test fixtures."""
    self.api_key = "test-api-key"
    self.host = "https://api.sandbox.transferwise.tech"
    self.context = {"profile_id": "123"}

  def test_all_tools_have_run_method_cases(self):
    """
    Dynamically test that every registered tool has a corresponding case in the run method.

    This test iterates through all tools registered in tools.py and verifies that each
    one is properly handled in the API's run() method switch case.
    """
    wise_api = WiseAPI(api_key=self.api_key, host=self.host, context=self.context)

    # Get all registered tool methods
    registered_methods = {tool["method"] for tool in tools}

    # Track results
    missing_methods = []
    tested_methods = []

    # Test each method to ensure it's handled in the run method
    for method in sorted(registered_methods):
      try:
        # Call run with the method - it should not raise ValueError for "Invalid method"
        # We expect it to fail with other errors (like missing parameters or API errors)
        # but not with "Invalid method"
        wise_api.run(method)
        # If it doesn't raise any error, that's fine - the method is handled
        tested_methods.append(method)
      except ValueError as e:
        # Check if it's the "Invalid method" error
        if "Invalid method" in str(e):
          missing_methods.append(method)
        else:
          # Any other ValueError is acceptable (e.g., missing required parameters)
          tested_methods.append(method)
      except Exception:
        # Any other exception is acceptable - we just want to ensure the method is recognized
        tested_methods.append(method)

    # Assert that no methods are missing
    if missing_methods:
      self.fail(
        f"The following {len(missing_methods)} tool(s) are registered in tools.py "
        f"but not handled in api.run():\n  - " + "\n  - ".join(missing_methods) +
        f"\n\nSuccessfully tested {len(tested_methods)} tool(s):\n  - " + "\n  - ".join(tested_methods)
      )

    # Print success message
    print(f"\n✓ Successfully verified all {len(tested_methods)} registered tools have API run() cases")

  def test_invalid_method(self):
    """Test that invalid method raises ValueError."""
    wise_api = WiseAPI(api_key=self.api_key, host=self.host, context=self.context)

    with self.assertRaises(ValueError) as cm:
      wise_api.run("invalid_method_that_does_not_exist")

    self.assertIn("Invalid method", str(cm.exception))


if __name__ == "__main__":
  unittest.main()
