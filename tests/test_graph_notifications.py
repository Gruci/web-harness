"""AI notices persist without requiring a host API or repeating every save."""

import json
from harness_test_support import TemporaryRootTestCase
from kernel import graph_notifications


class GraphNotificationTests(TemporaryRootTestCase):
    def test_same_issue_once_per_session_and_recovered_next_session(self) -> None:
        issues = ["pricing/rules.py: unclassified source; needs_decision"]
        first = graph_notifications.report(self.root, issues, "first")
        self.assertEqual(len(first), 1)
        self.assertEqual(graph_notifications.report(self.root, issues, "first"), [])
        restored = graph_notifications.report(self.root, issues, "next")
        self.assertEqual(first[0]["id"], restored[0]["id"])
        queue = json.loads((self.root / graph_notifications.QUEUE).read_text(encoding="utf-8"))
        self.assertEqual(queue[first[0]["id"]]["state"], "awaiting_user")

    def test_resolved_issue_is_not_a_new_pending_decision(self) -> None:
        issue = ["first code requires classification; needs_decision"]
        notice = graph_notifications.report(self.root, issue, "first")[0]
        self.assertEqual(graph_notifications.report(self.root, [], "first"), [])
        queue = json.loads((self.root / graph_notifications.QUEUE).read_text(encoding="utf-8"))
        self.assertEqual(queue[notice["id"]]["state"], "resolved")

    def test_reappearing_issue_reopens_and_notifies_same_session(self) -> None:
        issues = ["new component; needs_decision"]
        first = graph_notifications.report(self.root, issues, "session")[0]
        graph_notifications.report(self.root, [], "session")
        notices = graph_notifications.report(self.root, issues, "session")
        self.assertEqual(len(notices), 1)
        self.assertEqual(notices[0]["id"], first["id"])
