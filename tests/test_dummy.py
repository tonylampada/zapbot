import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'app'))) 

import unittest
from fastapi.testclient import TestClient
from app.main import app
client = TestClient(app)
from collections import defaultdict

class Bunch(defaultdict):
    def __init__(self, *args, **kwargs):
        super().__init__(Bunch, *args, **kwargs)

class TestDummy(unittest.TestCase):
    def test_dummy(self):
        self.assertTrue(True)
    
    def test_read_root(self):
        response = client.get("/") # TODO use client when we have a connection to pip install!
        assert response.json() == {"message": "Hello, World!"}
