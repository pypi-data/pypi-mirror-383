# -*- coding: utf-8 -*-

from ..utils import RequestManager, RequestMiddleware, RequestNotFound
from . import BaseTestCase


class RequestManagerTest(BaseTestCase):
    """Test request manager"""
    
    def test_get_request(self):
        """retrieve request"""
        request1 = {'user': "joe"}
        def fake_view(*args, **kwargs):
            request2 = RequestManager().get_request()
            self.assertEqual(request1, request2)
        RequestMiddleware(fake_view)(request1)

    def test_get_request_no_middleware(self):
        """if no request"""
        RequestManager().clean()
        self.assertRaises(RequestNotFound, RequestManager().get_request)
