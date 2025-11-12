from django.test import TestCase


class SimpleSmokeTest(TestCase):
    def test_smoke(self):
        """Simple smoke test to validate test discovery & setup."""
        self.assertTrue(True)
