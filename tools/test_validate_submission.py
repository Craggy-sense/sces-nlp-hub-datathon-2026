import unittest

from validate_submission import validate_paths


class SubmissionScopeTests(unittest.TestCase):
    def test_one_team(self):
        self.assertEqual(validate_paths([
            {"filename": "teams/team-07/README.md", "status": "modified"},
            {"filename": "teams/team-07/src/app.py", "status": "added"},
        ])[0], "team-07")

    def test_root_and_workflow_changes_rejected(self):
        for path in ("README.md", ".github/workflows/test.yml", "teams/team-25/README.md"):
            with self.subTest(path=path), self.assertRaises(ValueError):
                validate_paths([{"filename": path}])

    def test_two_teams_rejected(self):
        with self.assertRaises(ValueError):
            validate_paths([{"filename": "teams/team-01/README.md"}, {"filename": "teams/team-02/README.md"}])

    def test_cross_team_rename_rejected(self):
        with self.assertRaises(ValueError):
            validate_paths([{"filename": "teams/team-01/README.md", "previous_filename": "teams/team-02/README.md"}])

    def test_readme_deletion_rejected(self):
        with self.assertRaises(ValueError):
            validate_paths([{"filename": "teams/team-01/README.md", "status": "removed"}])


if __name__ == "__main__":
    unittest.main()
