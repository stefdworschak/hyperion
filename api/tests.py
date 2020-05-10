from django.test import TestCase, tag

from api.views import (create_hash_string, store_file_in_bucket, 
                       hash_and_store_file)

@tag('unit')
class ApiUnitTestCase(TestCase):
    def test_create_hash_string(self):
        validate_hash = 'dffd6021bb2bd5b0af676290809ec3a53191dd81c7f70a4b28688a362182986f'
        hash_string = create_hash_string(b"Hello, World!")
        self.assertEqual(validate_hash, hash_string)
    
    def test_hash_and_store_file(self):
        validate_hash = '7d02dff638611cb87a5d6fb219785b45191bfce5dc0ed46e2f7b8930cd2b2560'
        session_record = "{'session_id': 1, 'session_shared'; 0}"
        file_hash = hash_and_store_file(
            byte_object=bytes(session_record, 'utf-8'), extension='.json', 
            attachment=False)
        self.assertEqual(validate_hash, file_hash)

    def test_store_file_in_bucket(self):
        session_record = "{'session_id': 1, 'session_shared'; 0}"
        filename = '7d02dff638611cb87a5d6fb219785b45191bfce5dc0ed46e2f7b8930cd2b2560.json'
        byte_object = bytes(session_record, 'utf-8')
        path = store_file_in_bucket(byte_object.decode('utf-8'), filename)
        self.assertEqual(filename, path)
    
