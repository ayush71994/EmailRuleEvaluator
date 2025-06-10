import json
from datetime import datetime, timedelta

from EmailRuleEvaluator.MailFetcher.mail_fetcher import fetch_emails


def evaluate_rule(rule, email):
    field_value = email.get(rule["field"])
    predicate = rule["predicate"]
    target_value = rule["value"]

    if field_value is None:
        return False

    if rule["field"] == "received_at" and isinstance(field_value, str):
        field_value = datetime.fromisoformat(field_value)

    if predicate == "contains":
        return target_value.lower() in field_value.lower()
    elif predicate == "does_not_contain":
        return target_value.lower() not in field_value.lower()
    elif predicate == "equals":
        return field_value.lower() == target_value.lower()
    elif predicate == "does_not_equal":
        return field_value.lower() != target_value.lower()
    elif predicate == "newer_than_x_days":
        return field_value > (datetime.now() - timedelta(days=int(target_value)))
    elif predicate == "older_than_x_days":
        # print(f"field_value: {field_value} | target_value: {(datetime.now() - timedelta(days=int(target_value)))}")
        return field_value < datetime.now() - timedelta(days=int(target_value))
    else:
        return False


def evaluate_rule_group(group, email):
    group_predicate_type = group["group_predicate"].lower()
    results = [evaluate_rule(rule, email) for rule in group["rules"]]

    return all(results) if group_predicate_type == "all" else any(results)


def apply_rules_to_email(rules, email):
    actions = []

    for group in rules:
        if evaluate_rule_group(group, email):
            actions.extend(group["actions"])
            break

    if not actions:
        actions.append("No action email would remain in Inbox")
    return actions


if __name__ == '__main__':
    with open("rules.json") as rulesFile:
        rules = json.load(rulesFile)
    emails = fetch_emails()
    for email in emails:
        actions = apply_rules_to_email(rules, email)
        print(f"Actions: {actions} | Subject: {email.get("subject")}  | Date: {email.get("received_at")}")
