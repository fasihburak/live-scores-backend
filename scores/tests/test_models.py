import datetime

from django.test import TestCase
from django.utils import timezone

from ..models import Competition


class TestDatabase(TestCase):
    def test_writing_to_database(self):
        """
        Test writing to the database.
        """
        competition = Competition(name="Test Competition")
        competition.save()
        self.assertIsNotNone(competition.id)
      