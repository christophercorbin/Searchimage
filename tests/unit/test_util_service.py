import unittest

from services.util_service import UtilService

class TestUtilService(unittest.TestCase):
    def test_get_work_email_root_domains_from_mixed_emails(self):
        emails = ['hello@gmail.com', 'world@acme-company.com', 'hello@aol.com', 'world@kitty.com']
        root_domains = UtilService.get_work_email_root_domains(emails)

        self.assertEqual(root_domains, ['acme-company', 'kitty'])

    def test_get_work_email_root_domains_from_common_emails(self):
        emails = ['hello@gmail.com', 'world@outlook.com']
        root_domains = UtilService.get_work_email_root_domains(emails)

        self.assertEqual(root_domains, [])