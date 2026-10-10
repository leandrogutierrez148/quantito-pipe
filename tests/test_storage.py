import os
import unittest
from unittest import mock

from storage.bigquery import BigQueryStorage


class StorageTests(unittest.TestCase):
    def test_storage_is_not_configured_when_no_dataset(self):
        with mock.patch.dict(os.environ, {}, clear=True):
            storage = BigQueryStorage(dataset_name=None)
            self.assertFalse(storage.is_configured)
            # Should safely return without error
            storage.store_delayed_quotes([{"symbol": "AAPL.US"}])
            storage.store_eod_data([{"symbol": "AAPL.US"}])
            storage.store_real_time_quotes([{"code": "AAPL.US"}])

    def test_storage_is_configured_with_dataset_env(self):
        with mock.patch.dict(os.environ, {"BIGQUERY_DATASET": "test_dataset"}):
            storage = BigQueryStorage()
            self.assertTrue(storage.is_configured)
            self.assertEqual(storage.dataset_name, "test_dataset")
            self.assertEqual(storage.location, "US")
