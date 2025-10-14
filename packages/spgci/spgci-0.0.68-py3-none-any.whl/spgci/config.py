# Copyright 2025 S&P Global Commodity Insights

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#       http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Configure SPGCI settings
"""
import os
from typing import Dict, Union, Optional
from requests.auth import AuthBase
import contextvars

# from requests import _Auth

#: Username to use with the SPGCI API
username: str = os.getenv("SPGCI_USERNAME", "")
#: Password to use with the SPGCI API
password: str = os.getenv("SPGCI_PASSWORD", "")
#: Appkey to use with the SPGCI API. DEPRECATED
appkey: str = os.getenv("SPGCI_APPKEY", "")
#: Enable agent mode to restrict certain behaviors
is_agent: bool = os.getenv("SPGCI_AGENTMODE", "").lower() in ("true", "1", "yes", "on")

#: Token context var
token_ctx = contextvars.ContextVar("token", default=None)


def set_token(token: str):
    """set token"""
    token_ctx.set(token)


def get_token() -> str:
    """get token"""
    return token_ctx.get()


#: Set the base url used when making HTTP calls
base_url = "https://api.platts.com"
#: Set `verify` to `False` when making HTTP calls
verify_ssl = True
#: Add proxy to HTTP calls
proxies: Dict[str, str] = {
    "HTTP_PROXY": os.getenv("HTTP_PROXY", ""),
    "HTTPS_PROXY": os.getenv("HTTPS_PROXY", ""),
}

#: Add special auth mechanism such as requests-kerberos
auth: Union[AuthBase, None] = None

#: Version of the SPGCI Pkg
version = "0.0.68"

#: time to sleep between api calls
sleep_time = 0


def set_credentials(un: str, pw: str, apikey: Optional[str] = "") -> None:
    """
    Set credentials to use when calling the SPGCI API.

    You can avoid calling `set_credentials` by setting environment variables or creating a ``.env`` file with the following structure:\n
    SPGCI_USERNAME=``username``\n
    SPGCI_PASSWORD=``password``\n

    Parameters
    ----------
    un : str
        username
    pw : str
        password
    apikey: Optional[str]
        Deprecated. This parameter is ignored and will be removed in a future version.

    Deprecated:
    ----------
    The `apikey` parameter is deprecated and is no longer required. It will be removed in future versions.
    """
    global username, password, appkey
    username = un
    password = pw
