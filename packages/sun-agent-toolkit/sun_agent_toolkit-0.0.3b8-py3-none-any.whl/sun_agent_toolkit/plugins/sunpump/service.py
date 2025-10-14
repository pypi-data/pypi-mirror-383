import json
import logging
from typing import Any

import aiohttp

from sun_agent_toolkit.core.decorators.tool import Tool
from sun_agent_toolkit.core.types.token import Token
from sun_agent_toolkit.wallets.tron.tron_wallet_client import TronWalletClient

from .abi import LAUNCH_PAD_ABI
from .parameters import (
    GetTokenLaunchStatusParameters,
    SearchTokenParameters,
)

logger = logging.getLogger(__name__)


class SunPumpService:
    def __init__(
        self,
        api_key: str | None = None,
        base_url: str = "https://tmopenapi.endjgfsv.link/apiv2",
        pump_contract: str = "",
    ):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")  # Remove trailing slash if present
        self.pump_contract = pump_contract

    async def _make_request(self, endpoint: str, parameters: dict[str, Any]) -> dict[str, Any]:
        """Make a request to the SunPump API."""
        url = f"{self.base_url}/{endpoint}"

        headers: dict[str, Any] = {}

        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url, params=parameters, headers=headers) as response:
                    response_text = await response.text()
                    try:
                        response_json = json.loads(response_text)
                    except json.JSONDecodeError as e:
                        raise Exception(f"Invalid JSON response from {endpoint}: {response_text}") from e

                    logger.debug(f"\nAPI Response for {endpoint}:")
                    logger.debug(f"Status: {response.status}")
                    logger.debug(f"Headers: {dict(response.headers)}")
                    logger.debug(f"Body: {response_text}")

                    if not response.ok or response_json.get("code", -1) != 0:
                        error = response_json.get("msg", "Unknown error")
                        raise Exception(error)

                    return response_json
            except aiohttp.ClientError as e:
                raise Exception(f"Network error while accessing {endpoint}: {str(e)}") from e

    @Tool(
        {
            "name": "sunpump_search_token_by_symbol",
            "description": "search sunpump token by token symbol",
            "parameters_schema": SearchTokenParameters,
        }
    )
    async def search_token(self, parameters: dict[str, Any]) -> dict[str, Any]:
        """search sunio token by token symbol"""
        try:
            response = await self._make_request(
                "token/searchV2",
                {
                    "query": parameters["symbol"],
                    "sort": "marketCap:DESC",
                    "size": parameters["top_n"],
                    "page": "1",
                },
            )

            # If no approval data is returned, the token is already approved
            if not response or "data" not in response or not response["data"]["tokens"]:
                return {"success": True, "tokens": []}

            tokens: list[Token] = [
                {
                    "name": token["name"],
                    "symbol": token["symbol"],
                    "address": token["contractAddress"],
                    "decimals": token["decimals"],
                }
                for token in response["data"]["tokens"]
            ]
            return {"success": True, "tokens": tokens}
        except Exception as error:
            raise Exception(f"Failed to search token: {error}") from error

    @Tool(
        {
            "name": "sunpump_get_token_launch_status",
            "description": "get the launch status of a sunpump token",
            "parameters_schema": GetTokenLaunchStatusParameters,
        }
    )
    async def get_token_launch_status(
        self, wallet_client: TronWalletClient, parameters: dict[str, Any]
    ) -> dict[str, Any]:
        """get the status of sunpump token"""
        STATE_MAP = ["NEVER_CREATED", "ONSALE", "PENDING", "LAUNCHED"]
        try:
            token_state = int(
                wallet_client.read(
                    {
                        "address": self.pump_contract,
                        "abi": LAUNCH_PAD_ABI,
                        "functionName": "getTokenState",
                        "args": [parameters["token_address"]],
                    }
                )["value"]
            )
            return {"token_address": parameters["token_address"], "token_status": STATE_MAP[token_state]}
        except Exception as e:
            raise ValueError(f"Failed to fetch token state: {str(e)}") from e
