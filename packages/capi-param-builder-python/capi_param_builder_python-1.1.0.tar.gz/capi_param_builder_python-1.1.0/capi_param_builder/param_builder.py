# Copyright (c) Meta Platforms, Inc. and affiliates.
# All rights reserved.

# This source code is licensed under the license found in the
# LICENSE file in the root directory of this source tree.

import base64
import os.path
import random
import re
import time
from typing import Final, List, Optional, Union
from urllib.parse import parse_qs, urlparse

from .model import CookieSettings, FbcParamConfigs

from .util import EtldPlusOneResolver

DEFAULT_1PC_AGE: Final[int] = 90 * 24 * 3600  # 90 days
LANGUAGE_TOKEN: Final[str] = "Ag"  # Python
SUPPORTED_LANGUAGES_TOKENS: Final[List[str]] = ["AQ", "Ag", "Aw", "BA", "BQ", "Bg"]
MIN_PAYLOAD_SPLIT_LENGTH: Final[int] = 4
MAX_PAYLOAD_LENGTH_WITH_LANGUAGE_TOKEN: Final[int] = 5
IPV4_REGEX: Final[str] = "^((25[0-5]|(2[0-4]|1\\d|[1-9]|)\\d)\\.?\\b){4}$"
IPV6_SEG_REGEX: Final[str] = "^([0-9a-fA-F]{0,4}:)+"
FBC_COOKIE_NAME: Final[str] = "_fbc"
FBP_COOKIE_NAME: Final[str] = "_fbp"
FBCLID_QUERY_PARAMS: Final[str] = "fbclid"

# Appendix constants - matches JavaScript Constants.js
DEFAULT_FORMAT: Final[int] = 0x01
LANGUAGE_TOKEN_INDEX: Final[int] = 0x02  # Python language token index
APPENDIX_LENGTH_V1: Final[int] = 2
APPENDIX_LENGTH_V2: Final[int] = 8


class ParamBuilder:
    """
    Core class to process fbc, fbp
    """

    def __init__(self, input: Union[EtldPlusOneResolver, List, None] = None) -> None:
        """
        Initial the params
        """
        self.fbc_param_configs: List[FbcParamConfigs] = [
            FbcParamConfigs(FBCLID_QUERY_PARAMS, "", "clickID")
        ]
        self.fbc: Optional[str] = None
        self.fbp: Optional[str] = None
        self.sub_domain_index: int = 0
        self.cookies_to_set: set[CookieSettings] = set()
        self.cookies_to_set_dict: dict[str, CookieSettings] = {}
        self.host: Optional[str] = None
        self.etld_plus_one: Optional[str] = None
        self.domain_list: Optional[List] = None
        self.etld_plus_one_resolver: Optional[EtldPlusOneResolver] = None
        ## Appendix with version number
        self.appendix_new: str = self._get_appendix(True)
        self.appendix_normal: str = self._get_appendix(False)

        if isinstance(input, List):
            self.domain_list = []
            for domain in input:
                if domain is not None:
                    self.domain_list.append(self._extract_host_from_http_host(domain))
        elif isinstance(input, EtldPlusOneResolver):
            self.etld_plus_one_resolver = input

    def _get_version(self) -> str:
        """
        Extract version from setup.py file
        """
        try:
            # Get the directory containing this Python file
            current_dir = os.path.dirname(os.path.abspath(__file__))
            # Navigate up to find setup.py
            setup_py_path = os.path.join(current_dir, "..", "..", "setup.py")
            setup_py_path = os.path.normpath(setup_py_path)

            if os.path.exists(setup_py_path):
                with open(setup_py_path, "r") as f:
                    content = f.read()
                    # Extract version using regex
                    import re

                    version_match = re.search(
                        r'version\s*=\s*["\']([^"\']+)["\']', content
                    )
                    if version_match:
                        return version_match.group(1)
            # Fallback version if not found
            return "1.0.1"
        except Exception:
            # Fallback version on any error
            return "1.0.1"

    def _get_appendix(self, is_new: bool) -> str:
        try:
            version = self._get_version()
            version_parts = version.split(".")
            major = int(version_parts[0])
            minor = int(version_parts[1])
            patch = int(version_parts[2])

            is_new_byte = 0x01 if is_new else 0x00

            bytes_array = [
                DEFAULT_FORMAT,
                LANGUAGE_TOKEN_INDEX,
                is_new_byte,
                major,
                minor,
                patch,
            ]

            # Convert to bytes and then to base64url-safe string
            byte_data = bytes(bytes_array)
            base64_encoded = base64.b64encode(byte_data).decode("ascii")
            # Make it URL-safe by replacing characters
            base64url_safe = (
                base64_encoded.replace("+", "-").replace("/", "_").rstrip("=")
            )
            return base64url_safe
        except Exception as e:
            # Fallback to default appendix
            print(f"Unable to parse version number, fallback: {e}")
            return LANGUAGE_TOKEN

    def _pre_process_cookies(
        self, cookies: dict[str, str], cookie_name: str
    ) -> Optional[str]:
        if not cookies or cookie_name not in cookies:
            return None
        cookie_value = cookies.get(cookie_name)
        cookie_split = cookie_value.split(".")
        # Invalid cookie
        if (
            len(cookie_split) < MIN_PAYLOAD_SPLIT_LENGTH
            or len(cookie_split) > MAX_PAYLOAD_LENGTH_WITH_LANGUAGE_TOKEN
        ):
            return None

        # Validation for appendix
        if len(cookie_split) == MAX_PAYLOAD_LENGTH_WITH_LANGUAGE_TOKEN:
            appendix_value = cookie_split[MAX_PAYLOAD_LENGTH_WITH_LANGUAGE_TOKEN - 1]
            # Backward compatible with legacy appendix
            if len(appendix_value) == APPENDIX_LENGTH_V1:
                if appendix_value not in SUPPORTED_LANGUAGES_TOKENS:
                    return None
            elif len(appendix_value) != APPENDIX_LENGTH_V2:
                return None

        if len(cookie_split) == MIN_PAYLOAD_SPLIT_LENGTH:
            updated_cookie = cookie_value + "." + self.appendix_normal
            self.cookies_to_set_dict[cookie_name] = CookieSettings(
                cookie_name, updated_cookie, self.etld_plus_one, DEFAULT_1PC_AGE
            )
            return updated_cookie

        return cookie_value

    def _get_new_fbc_payload_from_url(
        self,
        queries: dict[str, List[str]],
        referer: Optional[str] = None,
    ) -> str:
        referrer_query_params = None
        if referer is not None:
            parsed_url = urlparse(referer)
            referrer_query_params = parse_qs(parsed_url.query)
        elif queries is None:
            return None  # no new fbc payload update
        # new fbc payload
        new_fbc_payload = None
        for config in self.fbc_param_configs:
            if queries and config.query in queries.keys():  # current url
                query_value = queries.get(config.query)
                if isinstance(query_value, list):
                    query_value = query_value[0]
                new_fbc_payload = self._build_param_configs(
                    new_fbc_payload,
                    config.query,
                    config.prefix,
                    query_value,
                )
            elif referrer_query_params and config.query in referrer_query_params.keys():
                query_value = referrer_query_params.get(config.query)
                if isinstance(query_value, list):
                    query_value = query_value[0]
                new_fbc_payload = self._build_param_configs(
                    new_fbc_payload,
                    config.query,
                    config.prefix,
                    query_value,
                )

        return new_fbc_payload

    def _build_param_configs(
        self,
        existing_payload: str,
        current_query: str,
        prefix: str,
        value: str,
    ) -> str:
        is_click_id = current_query == FBCLID_QUERY_PARAMS
        separator = "" if is_click_id else "_"
        # Prevent duplication
        if (
            existing_payload is not None
            and f"{separator}{prefix}{separator}" in existing_payload
        ):
            return existing_payload

        new_segment = f"{prefix}{separator}{value}"

        return (
            f"{existing_payload}{separator}{new_segment}"
            if existing_payload
            else new_segment
        )

    def process_request(
        self,
        host: str,
        queries: dict[str, List[str]],
        cookies: dict[str, str],
        referer: Optional[str] = None,
    ) -> set[CookieSettings]:
        self._compute_etld_plus_one_for_host(host)
        self.cookies_to_set = set()
        self.cookies_to_set_dict = {}
        self.fbc = self._pre_process_cookies(cookies, FBC_COOKIE_NAME)
        self.fbp = self._pre_process_cookies(cookies, FBP_COOKIE_NAME)
        # Get new fbc payload
        new_fbc_payload = self._get_new_fbc_payload_from_url(queries, referer)

        # fbc update
        updated_fbc_cookie = self._get_updated_fbc_cookie(self.fbc, new_fbc_payload)
        if updated_fbc_cookie is not None:
            self.cookies_to_set_dict[FBC_COOKIE_NAME] = updated_fbc_cookie
            self.fbc = updated_fbc_cookie.value
        # fbp update
        updated_fbp_cookie = self._get_updated_fbp_cookie(self.fbp)
        if updated_fbp_cookie is not None:
            self.cookies_to_set_dict[FBP_COOKIE_NAME] = updated_fbp_cookie
            self.fbp = updated_fbp_cookie.value
        self.cookies_to_set = set(self.cookies_to_set_dict.values())
        return self.cookies_to_set

    def get_cookies_to_set(self) -> Optional[set[CookieSettings]]:
        return self.cookies_to_set

    def get_fbc(self) -> Optional[str]:
        return self.fbc

    def get_fbp(self) -> Optional[str]:
        return self.fbp

    def _get_updated_fbc_cookie(
        self, existing_fbc: Optional[str], new_fbc_payload: Optional[str]
    ) -> Optional[CookieSettings]:
        """
        get updated fbc cookie
        """
        if new_fbc_payload is None:
            return None  # no update

        # cookie update
        cookie_update = False
        if existing_fbc is None:
            cookie_update = True
        else:
            parts = existing_fbc.split(".")
            cookie_update = new_fbc_payload != parts[3]

        if cookie_update is False:
            return None

        # Get ms
        now_ts = int(time.time() * 1000)
        new_fbc = (
            "fb."
            + str(self.sub_domain_index)
            + "."
            + str(now_ts)
            + "."
            + new_fbc_payload
            + "."
            + self.appendix_new
        )
        # TODO: update etld+1 to get proper etld+1.
        udpated_cookie_setting = CookieSettings(
            FBC_COOKIE_NAME, new_fbc, self.etld_plus_one, DEFAULT_1PC_AGE
        )
        return udpated_cookie_setting

    def _get_updated_fbp_cookie(
        self, existing_fbp: Optional[str]
    ) -> Optional[CookieSettings]:
        """
        get updated fbp cookie
        """
        if existing_fbp is not None:
            return None

        new_fbp_payload = str(random.randint(0, 2147483647))
        now_ts = int(time.time() * 1000)
        new_fbp = (
            "fb."
            + str(self.sub_domain_index)
            + "."
            + str(now_ts)
            + "."
            + new_fbp_payload
            + "."
            + self.appendix_new
        )
        udpated_cookie_setting = CookieSettings(
            FBP_COOKIE_NAME, new_fbp, self.etld_plus_one, DEFAULT_1PC_AGE
        )
        return udpated_cookie_setting

    def _compute_etld_plus_one_for_host(self, host: str) -> None:
        """
        compute etld+1 for host
        """
        if self.etld_plus_one is None or self.host is None:
            self.host = host
            host_name = self._extract_host_from_http_host(host)

            if self._is_ip_address(host_name):
                self.etld_plus_one = self._maybe_bracket_ipv6(host_name)
                self.sub_domain_index = 0
            else:
                self.etld_plus_one = self._get_etld_plus_one(host_name)
                self.sub_domain_index = len(self.etld_plus_one.split(".")) - 1

    def _get_etld_plus_one(self, host_name: str) -> str:
        if self.etld_plus_one_resolver is not None:
            return self.etld_plus_one_resolver.resolve(host_name)
        elif self.domain_list is not None:
            for domain in self.domain_list:
                if domain == host_name or host_name.endswith("." + domain):
                    return domain
        if len(host_name.split(".")) > 2:
            return host_name.split(".", 1)[1]
        return host_name

    def _extract_host_from_http_host(self, host: str) -> str:
        if host.rfind("://") != -1:
            host = host[host.rfind("://") + 3 :]
        pos_colon = host.rfind(":")
        pos_bracket = host.rfind("]")

        if pos_colon == -1:
            return host
        # if there's no right bracket (not IPv6 host), or colon is after
        # right bracket it's a port separator
        # examples:
        #  [::1]:8080 => trim
        #  google.com:8080 => trim
        if pos_bracket == -1 or pos_colon > pos_bracket:
            host = host[:pos_colon]
        # for IPv6, remove the brackets
        length = len(host)
        if length >= 2 and host[0] == "[" and host[length - 1] == "]":
            return host[1 : length - 1]
        return host

    def _is_ip_address(self, host: str) -> bool:
        ipv4_pattern = re.compile(IPV4_REGEX)
        is_ipv4 = ipv4_pattern.match(host) is not None
        if is_ipv4:
            return True
        ipv6_pattern = re.compile(IPV6_SEG_REGEX)
        is_ipv6 = ipv6_pattern.search(host) is not None
        return is_ipv6

    def _maybe_bracket_ipv6(self, host: str) -> str:
        if host.rfind(":"):
            return "[" + host + "]"
        return host
