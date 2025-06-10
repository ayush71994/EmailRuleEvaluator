import unittest
from datetime import datetime, timedelta

from rule_evaluator import evaluate_rule, evaluate_rule_group, apply_rules_to_email
class TestRuleEngine(unittest.TestCase):

    def setUp(self):
        self.email_linkedin = {
            "from": "linkedin.com",
            "subject": "Welcome to the platform!",
            "received_at": datetime.now().isoformat(),
        }

        self.email_older_than_30_days = {
            "from": "admin@example.com",
            "subject": "Monthly Update",
            "received_at": (datetime.now() - timedelta(days=30)).isoformat(),
        }

    def test_contains_predicate(self):
        rule = {"field": "subject", "predicate": "contains", "value": "welcome"}
        self.assertTrue(evaluate_rule(rule, self.email_linkedin))

    def test_does_not_contain_predicate(self):
        rule = {"field": "subject", "predicate": "does_not_contain", "value": "unsubscribe"}
        self.assertTrue(evaluate_rule(rule, self.email_linkedin))

    def test_newer_than_days(self):
        rule = {"field": "received_at", "predicate": "newer_than_x_days", "value": "3"}
        self.assertTrue(evaluate_rule(rule, self.email_linkedin))

    def test_older_than_days(self):
        rule = {"field": "received_at", "predicate": "older_than_x_days", "value": "10"}
        self.assertTrue(evaluate_rule(rule, self.email_older_than_30_days))

    def test_missing_field(self):
        email = {"subject": "No From Field"}
        rule = {"field": "from", "predicate": "contains", "value": "abc@"}
        self.assertFalse(evaluate_rule(rule, email))

    def test_group_predicate_all(self):
        group = {
            "group_predicate": "all",
            "rules": [
                {"field": "subject", "predicate": "contains", "value": "welcome"},
                {"field": "from", "predicate": "contains", "value": "linkedin"}
            ]
        }
        self.assertTrue(evaluate_rule_group(group, self.email_linkedin))

    def test_group_predicate_any(self):
        group = {
            "group_predicate": "any",
            "rules": [
                {"field": "subject", "predicate": "contains", "value": "foobar"},
                {"field": "from", "predicate": "contains", "value": "linkedin"}
            ]
        }
        self.assertTrue(evaluate_rule_group(group, self.email_linkedin))

    def test_apply_rules_match_found(self):
        rules = [
            {
                "group_predicate": "all",
                "rules": [
                    {"field": "subject", "predicate": "contains", "value": "welcome"}
                ],
                "actions": ["mark_as_read", "move:Welcome"]
            }
        ]
        result = apply_rules_to_email(rules, self.email_linkedin)
        self.assertEqual(result, ["mark_as_read", "move:Welcome"])

    def test_apply_rules_no_match(self):
        rules = [
            {
                "group_predicate": "all",
                "rules": [
                    {"field": "subject", "predicate": "contains", "value": "unsubscribe"}
                ],
                "actions": ["mark_as_read"]
            }
        ]
        result = apply_rules_to_email(rules, self.email_linkedin)
        self.assertEqual(result, ["No action email would remain in Inbox"])

    def test_apply_rules_first_match_only(self):
        rules = [
            {
                "group_predicate": "any",
                "rules": [
                    {"field": "subject", "predicate": "contains", "value": "welcome"}
                ],
                "actions": ["move:Welcome"]
            },
            {
                "group_predicate": "any",
                "rules": [
                    {"field": "subject", "predicate": "contains", "value": "platform"}
                ],
                "actions": ["move:Platform"]
            }
        ]
        result = apply_rules_to_email(rules, self.email_linkedin)
        self.assertEqual(result, ["move:Welcome"])  # Stops at first match

if __name__ == "__main__":
    unittest.main()