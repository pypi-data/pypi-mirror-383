import unittest
from unittest.mock import Mock, patch, MagicMock
from crossmark_jotform_api.jotForm import JotForm, JotFormSubmission


class TestJotFormUnit(unittest.TestCase):
    """Unit tests for JotForm that don't require real API calls"""

    def setUp(self):
        """Set up test fixtures before each test method."""
        self.api_key = "test_api_key"
        self.form_id = "123456"

    def test_build_url(self):
        """Test URL building functionality"""
        expected_url = f"https://api.jotform.com/form/{self.form_id}/submissions?limit=1000&apiKey={self.api_key}"
        result = JotForm.build_url(self.form_id, self.api_key)
        self.assertEqual(result, expected_url)

    @patch("crossmark_jotform_api.jotForm.requests.get")
    def test_get_form_success(self, mock_get):
        """Test successful form retrieval"""
        # Mock the response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "responseCode": 200,
            "content": {"id": self.form_id, "title": "Test Form"},
        }
        mock_get.return_value = mock_response

        # Create JotForm instance with mocked update
        with patch.object(JotForm, "update"):
            jotform = JotForm(self.api_key, self.form_id)
            result = jotform.get_form()

        self.assertEqual(result["responseCode"], 200)
        self.assertEqual(result["content"]["id"], self.form_id)

    @patch("crossmark_jotform_api.jotForm.requests.get")
    def test_get_form_failure(self, mock_get):
        """Test form retrieval failure"""
        # Mock failed response
        mock_response = Mock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response

        with patch.object(JotForm, "update"):
            jotform = JotForm(self.api_key, self.form_id)
            result = jotform.get_form()

        self.assertIsNone(result)

    def test_set_url_param_new_param(self):
        """Test setting a new URL parameter"""
        with patch.object(JotForm, "update"):
            jotform = JotForm(self.api_key, self.form_id)

        initial_url = jotform.url
        jotform.set_url_param("test_param", "test_value")

        self.assertIn("test_param=test_value", jotform.url)

    def test_set_url_param_existing_param(self):
        """Test updating an existing URL parameter"""
        with patch.object(JotForm, "update"):
            jotform = JotForm(self.api_key, self.form_id)

        # First set the parameter
        jotform.set_url_param("offset", "100")
        self.assertIn("offset=100", jotform.url)

        # Update the parameter
        jotform.set_url_param("offset", "200")
        self.assertIn("offset=200", jotform.url)
        self.assertNotIn("offset=100", jotform.url)


class TestJotFormSubmission(unittest.TestCase):
    """Unit tests for JotFormSubmission"""

    def setUp(self):
        """Set up test fixtures"""
        self.api_key = "test_api_key"
        self.sample_submission = {
            "id": "123456789",
            "form_id": "987654321",
            "ip": "192.168.1.1",
            "created_at": "2024-01-01 12:00:00",
            "status": "ACTIVE",
            "new": "1",
            "flag": "0",
            "notes": "",
            "updated_at": "2024-01-01 12:00:00",
            "answers": {
                "1": {
                    "name": "fullName",
                    "answer": "John Doe",
                    "text": "Full Name",
                    "type": "control_textbox",
                },
                "2": {
                    "name": "email",
                    "answer": "john@example.com",
                    "text": "Email Address",
                    "type": "control_email",
                },
            },
        }

    def test_submission_initialization(self):
        """Test JotFormSubmission initialization"""
        submission = JotFormSubmission(self.sample_submission, self.api_key)

        self.assertEqual(submission.id, "123456789")
        self.assertEqual(submission.form_id, "987654321")
        self.assertEqual(submission.ip, "192.168.1.1")
        self.assertEqual(submission.status, "ACTIVE")

    def test_get_answer_by_text(self):
        """Test getting answer by text"""
        submission = JotFormSubmission(self.sample_submission, self.api_key)

        answer = submission.get_answer_by_text("Full Name")
        self.assertEqual(answer["answer"], "John Doe")
        self.assertEqual(answer["name"], "fullName")

    def test_get_answer_by_name(self):
        """Test getting answer by name"""
        submission = JotFormSubmission(self.sample_submission, self.api_key)

        answer = submission.get_answer_by_name("fullName")
        self.assertEqual(answer["answer"], "John Doe")
        self.assertEqual(answer["text"], "Full Name")

    def test_get_answer_by_key(self):
        """Test getting answer by key"""
        submission = JotFormSubmission(self.sample_submission, self.api_key)

        answer = submission.get_answer_by_key("1")
        self.assertEqual(answer["answer"], "John Doe")
        self.assertEqual(answer["name"], "fullName")

    def test_get_emails(self):
        """Test extracting emails from submission"""
        submission = JotFormSubmission(self.sample_submission, self.api_key)

        emails = submission.get_emails()
        self.assertIn("john@example.com", emails)

    def test_get_value_with_string(self):
        """Test get_value with string input"""
        submission = JotFormSubmission(self.sample_submission, self.api_key)

        result = submission.get_value("test string")
        self.assertEqual(result, "test string")

    def test_get_value_with_dict(self):
        """Test get_value with dict input"""
        submission = JotFormSubmission(self.sample_submission, self.api_key)

        test_dict = {"answer": "test answer"}
        result = submission.get_value(test_dict)
        self.assertEqual(result, "test answer")

    def test_make_array_with_string(self):
        """Test make_array with string input"""
        submission = JotFormSubmission(self.sample_submission, self.api_key)

        result = submission.make_array("item1, item2, item3")
        self.assertEqual(result, ["item1", "item2", "item3"])

    def test_make_array_with_list(self):
        """Test make_array with list input"""
        submission = JotFormSubmission(self.sample_submission, self.api_key)

        test_list = ["item1", "item2", "item3"]
        result = submission.make_array(test_list)
        self.assertEqual(result, test_list)

    def test_split_domain_from_email(self):
        """Test splitting domain from email"""
        submission = JotFormSubmission(self.sample_submission, self.api_key)

        result = submission.split_domain_from_email("test@example.com")
        self.assertEqual(result, "test")

    def test_to_dict(self):
        """Test converting submission to dict"""
        submission = JotFormSubmission(self.sample_submission, self.api_key)

        result = submission.to_dict()
        self.assertEqual(result["id"], "123456789")
        self.assertEqual(result["form_id"], "987654321")
        self.assertIn("emails", result)


if __name__ == "__main__":
    unittest.main()
