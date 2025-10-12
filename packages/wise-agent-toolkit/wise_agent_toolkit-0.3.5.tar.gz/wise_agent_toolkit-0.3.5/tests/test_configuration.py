import unittest

from wise_agent_toolkit.configuration import is_tool_allowed


class TestConfigurations(unittest.TestCase):
  def test_allowed(self):
    tool = {
      "actions": {
        "transfers": {"create": True, "read": True},
        "quotes": {"create": True, "read": True},
      }
    }

    configuration = {
      "actions": {
        "transfers": {"create": True, "read": True},
        "quotes": {"create": True, "read": True},
      }
    }

    self.assertTrue(is_tool_allowed(tool, configuration))

  def test_partial_allowed(self):
    tool = {
      "actions": {
        "transfers": {"create": True, "read": True},
        "quotes": {"create": True, "read": True},
      }
    }

    configuration = {
      "actions": {
        "transfers": {"create": True, "read": True},
        "quotes": {"create": True, "read": False},
      }
    }

    self.assertFalse(is_tool_allowed(tool, configuration))

  def test_not_allowed(self):
    tool = {
      "actions": {
        "payment_links": {"create": True},
      }
    }

    configuration = {
      "actions": {
        "transfers": {"create": True, "read": True},
        "quotes": {"create": True, "read": True},
      }
    }

    self.assertFalse(is_tool_allowed(tool, configuration))


if __name__ == "__main__":
  unittest.main()
