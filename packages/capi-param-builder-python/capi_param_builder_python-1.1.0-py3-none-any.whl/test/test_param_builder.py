# Copyright (c) Meta Platforms, Inc. and affiliates.
# All rights reserved.

# This source code is licensed under the license found in the
# LICENSE file in the root directory of this source tree.

import unittest
from typing import List
from unittest.mock import patch

from capi_param_builder.model import FbcParamConfigs

from capi_param_builder.param_builder import ParamBuilder

from .test_etld_plus_one_resolver import TestEtldPlusOneResolver

APPENDIX_IS_NEW = "AQIBAQAB"
APPENDIX_IS_NORMAL = "AQIAAQAB"


class TestParamBuilder(unittest.TestCase):
    def setUp(self) -> None:
        super().setUp()
        # Mock _get_version for all tests in this class
        self.version_patcher = patch(
            "capi_param_builder.param_builder.ParamBuilder._get_version"
        )
        self.mock_version = self.version_patcher.start()
        self.mock_version.return_value = "1.0.1"

    def tearDown(self) -> None:
        super().tearDown()
        # Stop the patcher
        self.version_patcher.stop()

    @patch("capi_param_builder.param_builder.ParamBuilder._get_version")
    def test_get_appendix(self, mock_version) -> None:
        # Test with version 0.255.255
        mock_version.return_value = "0.255.255"
        builder = ParamBuilder()
        self.assertEqual(builder._get_appendix(False), "AQIAAP__")
        self.assertEqual(builder._get_appendix(True), "AQIBAP__")
        # Test with version 1.1.0
        mock_version.return_value = "1.1.0"
        builder = ParamBuilder()
        self.assertEqual(builder._get_appendix(False), "AQIAAQEA")
        self.assertEqual(builder._get_appendix(True), "AQIBAQEA")
        # Exception when parsing version
        mock_version.return_value = ""
        builder = ParamBuilder()
        self.assertEqual(builder._get_appendix(False), "Ag")
        self.assertEqual(builder._get_appendix(True), "Ag")
        # Test with version 1.0.1
        mock_version.return_value = "1.0.1"
        builder = ParamBuilder()
        self.assertEqual(builder._get_appendix(False), APPENDIX_IS_NORMAL)
        self.assertEqual(builder._get_appendix(True), APPENDIX_IS_NEW)

    def test_process_request_empty_constructor(self) -> None:
        builder = ParamBuilder()
        res = builder.process_request("example.com", {}, {})
        self.assertEqual(1, len(res))
        fbp = res.pop()
        self.assertEqual("_fbp", fbp.name)
        self.assertEqual("example.com", fbp.domain)
        self.assertTrue((fbp.value).endswith(f".{APPENDIX_IS_NEW}"))
        self.assertEqual(res, builder.get_cookies_to_set())
        pass

    def test_process_request_empty_constructor_with_fbc(self) -> None:
        builder = ParamBuilder()
        res = builder.process_request("test.example.com", {"fbclid": ["testtest"]}, {})
        self.assertEqual(2, len(res))
        for cookie in res:
            if cookie.name == "_fbc":
                self.assertTrue((cookie.value).endswith(f".testtest.{APPENDIX_IS_NEW}"))
                self.assertEqual("example.com", cookie.domain)
            else:
                self.assertEqual("_fbp", cookie.name)
                self.assertTrue((cookie.value).endswith(f".{APPENDIX_IS_NEW}"))
        self.assertEqual(res, builder.get_cookies_to_set())
        pass

    def test_process_request_empty_constructor_with_fbc_cookie(self) -> None:
        builder = ParamBuilder()
        res = builder.process_request(
            "test.example.com",
            {"fbclid": "testtest"},
            {"_fbc": "abcd"},  # invalid fbc
        )
        self.assertEqual(2, len(res))
        for cookie in res:
            if cookie.name == "_fbc":
                self.assertTrue((cookie.value).endswith(f".testtest.{APPENDIX_IS_NEW}"))
                self.assertEqual("example.com", cookie.domain)
            else:
                self.assertEqual("_fbp", cookie.name)
                self.assertTrue((cookie.value).endswith(f".{APPENDIX_IS_NEW}"))
        self.assertEqual(res, builder.get_cookies_to_set())
        pass

    def test_process_request_domain_list_constructor(self) -> None:
        builder = ParamBuilder(["example.com"])
        res = builder.process_request(
            "balabala.test.example.com",
            {},
            {"_fbc": "fb.1.xxx.abcd"},  # valid fbc
        )
        self.assertEqual(2, len(res))
        for cookie in res:
            if cookie.name == "_fbc":
                self.assertEqual(
                    cookie.value, f"fb.1.xxx.abcd.{APPENDIX_IS_NORMAL}"
                )  # normal
                self.assertEqual("example.com", cookie.domain)
            else:
                self.assertEqual("_fbp", cookie.name)
                self.assertTrue((cookie.value).endswith(f".{APPENDIX_IS_NEW}"))  # new
        self.assertEqual(res, builder.get_cookies_to_set())
        pass

    def test_process_request_with_param_config_override(self) -> None:
        builder = ParamBuilder(["example.com"])
        builder.fbc_param_configs: List[FbcParamConfigs] = [
            FbcParamConfigs("fbclid", "", "clickID"),
            FbcParamConfigs("query", "test", "placeholder"),
        ]
        res = builder.process_request(
            "https://balabala.test.example.com",
            {"fbclid": ["test123321"], "query": "anotherTest"},
            None,
        )
        self.assertEqual(2, len(res))
        for cookie in res:
            if cookie.name == "_fbc":
                self.assertTrue(
                    (cookie.value).endswith(
                        f".test123321_test_anotherTest.{APPENDIX_IS_NEW}"
                    )
                )
                self.assertEqual("example.com", cookie.domain)
            else:
                self.assertEqual("_fbp", cookie.name)
                self.assertTrue((cookie.value).endswith(f".{APPENDIX_IS_NEW}"))
        self.assertEqual(res, builder.get_cookies_to_set())
        pass

    def test_process_request_with_param_config_override_with_referral(self) -> None:
        builder = ParamBuilder(["example.com"])
        builder.fbc_param_configs: List[FbcParamConfigs] = [
            FbcParamConfigs("fbclid", "", "clickID"),
            FbcParamConfigs("query", "test", "placeholder"),
            FbcParamConfigs("example", "example1", "example2"),
        ]
        res = builder.process_request(
            "https://balabala.test.example.com",
            {"query": "anotherTest"},
            None,
            "https://balabala.test.example.com?fbclid=testReferral",
        )
        self.assertEqual(2, len(res))
        for cookie in res:
            if cookie.name == "_fbc":
                self.assertTrue(
                    (cookie.value).endswith(
                        f".testReferral_test_anotherTest.{APPENDIX_IS_NEW}"
                    )
                )
                self.assertEqual("example.com", cookie.domain)
            else:
                self.assertEqual("_fbp", cookie.name)
                self.assertTrue((cookie.value).endswith(f".{APPENDIX_IS_NEW}"))
        self.assertEqual(res, builder.get_cookies_to_set())
        pass

    def test_process_request_with_param_config_override_partially_exist(self) -> None:
        builder = ParamBuilder(["example.com"])
        builder.fbc_param_configs: List[FbcParamConfigs] = [
            FbcParamConfigs("fbclid", "", "clickID"),
            FbcParamConfigs("query", "test", "placeholder"),
        ]
        res = builder.process_request(
            "https://balabala.test.example.com",
            {"query": "anotherTest"},
            None,
        )
        self.assertEqual(2, len(res))
        for cookie in res:
            if cookie.name == "_fbc":
                self.assertTrue(
                    (cookie.value).endswith(f".test_anotherTest.{APPENDIX_IS_NEW}")
                )
                self.assertEqual("example.com", cookie.domain)
            else:
                self.assertEqual("_fbp", cookie.name)
                self.assertTrue((cookie.value).endswith(f".{APPENDIX_IS_NEW}"))
        self.assertEqual(res, builder.get_cookies_to_set())
        pass

    def test_process_request_with_param_config_override_duplication(self) -> None:
        builder = ParamBuilder(["example.com"])
        builder.fbc_param_configs: List[FbcParamConfigs] = [
            FbcParamConfigs("fbclid", "", "clickID"),
            FbcParamConfigs("query", "test", "placeholder"),
        ]
        res = builder.process_request(
            "https://balabala.test.example.com",
            {"query": "anotherTest"},
            None,
            "https://balabala.test.example.com?fbclid=testReferral_test_sample",
        )
        self.assertEqual(2, len(res))
        for cookie in res:
            if cookie.name == "_fbc":
                self.assertTrue(
                    (cookie.value).endswith(
                        f".testReferral_test_sample.{APPENDIX_IS_NEW}"
                    )
                )
                self.assertEqual("example.com", cookie.domain)
            else:
                self.assertEqual("_fbp", cookie.name)
                self.assertTrue((cookie.value).endswith(f".{APPENDIX_IS_NEW}"))
        self.assertEqual(res, builder.get_cookies_to_set())
        pass

    def test_process_request_domain_list_constructor_with_fbclid(self) -> None:
        builder = ParamBuilder(["example.com"])
        res = builder.process_request(
            "https://balabala.test.example.com", {"fbclid": ["test123321"]}, {}
        )
        self.assertEqual(2, len(res))
        for cookie in res:
            if cookie.name == "_fbc":
                self.assertTrue(
                    (cookie.value).endswith(f".test123321.{APPENDIX_IS_NEW}")
                )
                self.assertEqual("example.com", cookie.domain)
            else:
                self.assertEqual("_fbp", cookie.name)
                self.assertTrue((cookie.value).endswith(f".{APPENDIX_IS_NEW}"))
        self.assertEqual(res, builder.get_cookies_to_set())
        pass

    def test_process_request_domain_list_constructor_with_language_token(self) -> None:
        builder = ParamBuilder(["example.com"])
        res = builder.process_request(
            "balabala.test.example.com",
            {},
            {"_fbc": "fb.1.xxx.abcd.Bg"},  # valid fbc cookie
        )
        self.assertEqual(1, len(res))
        for cookie in res:
            self.assertEqual("_fbp", cookie.name)
            self.assertEqual("example.com", cookie.domain)
            self.assertTrue((cookie.value).endswith(f".{APPENDIX_IS_NEW}"))  # new fbp
        self.assertEqual("fb.1.xxx.abcd.Bg", builder.get_fbc())  # no change for fbc
        self.assertEqual(res, builder.get_cookies_to_set())
        pass

    def test_process_request_domain_list_constructor_with_protocol(self) -> None:
        builder = ParamBuilder(["https://examplestemp.com", "http://example.co.uk"])
        res = builder.process_request(
            "https://balabala.test.example.co.uk:3000", {"fbclid": ["test123321"]}, {}
        )
        self.assertEqual(2, len(res))
        for cookie in res:
            if cookie.name == "_fbc":
                self.assertTrue("test123321" in cookie.value)
                self.assertEqual("example.co.uk", cookie.domain)
                self.assertTrue(
                    (cookie.value).endswith(f".test123321.{APPENDIX_IS_NEW}")
                )
            else:
                self.assertEqual("_fbp", cookie.name)
                self.assertTrue((cookie.value).endswith(f".{APPENDIX_IS_NEW}"))
        self.assertEqual(res, builder.get_cookies_to_set())
        pass

    def test_process_request_etld_plus_one_resolver(self) -> None:
        builder = ParamBuilder(TestEtldPlusOneResolver())
        res = builder.process_request(
            "balabala.test.example.co.uk",
            {},
            {},
            "example.com?fbclid=test123",
        )

        self.assertEqual(2, len(res))
        for cookie in res:
            if cookie.name == "_fbc":
                self.assertTrue((cookie.value).endswith(f".test123.{APPENDIX_IS_NEW}"))
                self.assertEqual("balabala.test.example.co.uk", cookie.domain)
            else:
                self.assertEqual("_fbp", cookie.name)
                self.assertTrue((cookie.value).endswith(f".{APPENDIX_IS_NEW}"))
        self.assertEqual(res, builder.get_cookies_to_set())
        pass

    def test_process_request_ipv6(self) -> None:
        builder = ParamBuilder()
        res = builder.process_request(
            "[::1]:8080", {"fbclid": "test123"}, {"_fbp": "fb.1.123.fbptest.Ag"}
        )
        self.assertEqual(1, len(res))
        fbc = res.pop()
        self.assertEqual("_fbc", fbc.name)
        self.assertEqual("[::1]", fbc.domain)
        self.assertTrue(f".test123.{APPENDIX_IS_NEW}" in fbc.value)
        self.assertEqual("fb.1.123.fbptest.Ag", builder.get_fbp())
        self.assertEqual(res, builder.get_cookies_to_set())
        pass

    def test_process_request_ipv6_test(self) -> None:
        builder = ParamBuilder(["test.example.com"])
        res = builder.process_request(
            "[2001:db8:4006:812::200e]",
            {"fbclid": "test123"},
            {
                "_fbc": "fb.1.123.test123.test",  # invalid fbc
                "_fbp": "fb.1.123.test.Bg",
            },
            None,
        )
        self.assertEqual(1, len(res))
        fbc = res.pop()
        self.assertEqual("_fbc", fbc.name)
        self.assertEqual("[2001:db8:4006:812::200e]", fbc.domain)
        self.assertTrue(f"test123.{APPENDIX_IS_NEW}" in fbc.value)
        self.assertEqual("fb.1.123.test.Bg", builder.get_fbp())
        self.assertEqual(res, builder.get_cookies_to_set())
        pass

    def test_process_request_ipv4(self) -> None:
        builder = ParamBuilder(TestEtldPlusOneResolver())
        res = builder.process_request(
            "192.168.0.1",
            {"fbclid": "test123"},
            {"_fbp": "fbptest"},  # invalid fbp
            "https://example.com?fbclid=balabala",
        )
        self.assertEqual(2, len(res))

        for cookie in res:
            if cookie.name == "_fbc":
                self.assertTrue((cookie.value).endswith(f".test123.{APPENDIX_IS_NEW}"))
                self.assertEqual("[192.168.0.1]", cookie.domain)
            else:
                self.assertEqual("_fbp", cookie.name)
                self.assertTrue((cookie.value).endswith(f".{APPENDIX_IS_NEW}"))
        self.assertEqual(res, builder.get_cookies_to_set())
        pass

    def test_process_request_localhost(self) -> None:
        builder = ParamBuilder()
        res = builder.process_request(
            "localhost", None, None, "https://test?fbclid=test123"
        )
        self.assertEqual(2, len(res))
        for cookie in res:
            if cookie.name == "_fbc":
                self.assertTrue(f"test123.{APPENDIX_IS_NEW}" in cookie.value)
                self.assertEqual("localhost", cookie.domain)
            else:
                self.assertEqual("_fbp", cookie.name)
                self.assertTrue("fb.0." in cookie.value)
        self.assertEqual(res, builder.get_cookies_to_set())
        pass


if __name__ == "__main__":
    unittest.main()
