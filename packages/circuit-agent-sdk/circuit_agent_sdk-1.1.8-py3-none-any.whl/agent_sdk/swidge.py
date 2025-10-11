"""
Swidge cross-chain swap operations.

This module provides the SwidgeApi class for cross-chain swaps and bridges
using the Swidge protocol.
"""

from typing import TYPE_CHECKING

from .types import (
    SwidgeExecuteResponse,
    SwidgeExecuteResponseData,
    SwidgeQuoteData,
    SwidgeQuoteRequest,
    SwidgeQuoteResponse,
)

if TYPE_CHECKING:
    from .agent_sdk import AgentSdk


class SwidgeApi:
    """Cross-chain swap operations using Swidge.

    Workflow: quote() -> execute(quote.data) -> check result.data.status
    """

    def __init__(self, sdk: "AgentSdk"):
        self._sdk = sdk

    def quote(self, request: SwidgeQuoteRequest | dict) -> SwidgeQuoteResponse:
        """Get a cross-chain swap or bridge quote.

        Args:
            request: Quote parameters with wallet info, amount, and optional tokens/slippage.
                from: Source wallet {"network": "ethereum:1", "address": "0x..."}
                to: Destination wallet {"network": "ethereum:42161", "address": "0x..."}
                amount: Amount in smallest unit (e.g., "1000000000000000000" for 1 ETH)
                fromToken: Source token address (optional, omit for native tokens)
                toToken: Destination token address (optional, omit for native tokens)
                slippage: Slippage tolerance % as string (default: "0.5")
                priceImpact: Max price impact % as string (default: "0.5")

        Returns:
            SwidgeQuoteResponse with pricing, fees, and transaction steps.

        Example:
            quote = sdk.swidge.quote({
                "from": {"network": "ethereum:1", "address": user_address},
                "to": {"network": "ethereum:42161", "address": user_address},
                "amount": "1000000000000000000",  # 1 ETH
                "toToken": "0x2f2a2543B76A4166549F7aaB2e75BEF0aefC5b0f"  # WBTC
            })
        """
        return self._handle_swidge_quote(request)

    def execute(self, quote_data: SwidgeQuoteData) -> SwidgeExecuteResponse:
        """Execute a cross-chain swap or bridge using a quote.

        Args:
            quote_data: Complete quote object from sdk.swidge.quote().

        Returns:
            SwidgeExecuteResponse with transaction status and details.

        Example:
            quote = sdk.swidge.quote({...})
            if quote.success and quote.data:
                result = sdk.swidge.execute(quote.data)
        """
        return self._handle_swidge_execute(quote_data)

    def _handle_swidge_quote(
        self, request: SwidgeQuoteRequest | dict
    ) -> SwidgeQuoteResponse:
        """Handle swidge quote requests."""
        self._sdk._log("=== SWIDGE QUOTE ===")
        self._sdk._log("Request:", request)
        self._sdk._log("Testing mode:", self._sdk.config.testing)
        self._sdk._log("===================")

        try:
            # Handle both dict and Pydantic model inputs
            if isinstance(request, dict):
                request_obj = SwidgeQuoteRequest(**request)
            else:
                request_obj = request

            if self._sdk.config.testing:
                test_data = {
                    "engine": "relay",
                    "assetSend": {
                        "network": request_obj.from_.network,
                        "address": request_obj.from_.address,
                        "token": request_obj.fromToken,
                        "name": "Test Asset",
                        "symbol": "TEST",
                        "decimals": 18,
                        "amount": request_obj.amount,
                        "minimumAmount": request_obj.amount,
                        "amountFormatted": "1.0",
                        "amountUsd": "100.00",
                    },
                    "assetReceive": {
                        "network": request_obj.to.network,
                        "address": request_obj.to.address,
                        "token": request_obj.toToken,
                        "name": "Test Asset",
                        "symbol": "TEST",
                        "decimals": 18,
                        "amount": "950000000000000000",
                        "minimumAmount": "950000000000000000",
                        "amountFormatted": "0.95",
                        "amountUsd": "95.00",
                    },
                    "priceImpact": {"percentage": "0.5", "usd": "5.00"},
                    "fees": [
                        {
                            "name": "gas",
                            "amount": "21000000000000000",
                            "amountFormatted": "0.021",
                            "amountUsd": "2.10",
                        }
                    ],
                    "steps": [
                        {
                            "type": "transaction",
                            "description": "Test swap transaction",
                            "transactionDetails": {
                                "type": "evm",
                                "from": "0x1234567890123456789012345678901234567890",
                                "to": "0x1234567890123456789012345678901234567890",
                                "chainId": 1,
                                "value": 0,
                                "data": "0x",
                                "gas": 21000,
                                "maxFeePerGas": 20000000000,
                                "maxPriorityFeePerGas": 1000000000,
                            },
                            "metadata": {"requestId": "test-request-id"},
                        }
                    ],
                }
                return SwidgeQuoteResponse(
                    success=True,
                    error=None,
                    errorDetails=None,
                    data=SwidgeQuoteData.model_validate(test_data),
                )

            response = self._sdk.client.post(
                "/v1/swidge/quote",
                request_obj.model_dump(by_alias=True, exclude_none=True),
            )

            return SwidgeQuoteResponse(
                success=True,
                error=None,
                errorDetails=None,
                data=SwidgeQuoteData(**response),
            )
        except Exception as error:
            self._sdk._log("=== SWIDGE QUOTE ERROR ===")
            self._sdk._log("Error:", error)
            self._sdk._log("=========================")

            error_message = "Failed to get swidge quote"
            status = None
            status_text = None

            if isinstance(error, Exception):
                error_message = str(error)

                # Try to extract HTTP status from error message
                if hasattr(error, "response") and hasattr(
                    error.response, "status_code"
                ):
                    status = error.response.status_code
                    if hasattr(error.response, "reason"):
                        status_text = str(error.response.reason)

            return SwidgeQuoteResponse(
                success=False,
                data=None,
                error=error_message,
                errorDetails={
                    "message": error_message,
                    "status": status,
                    "statusText": status_text,
                },
            )

    def _handle_swidge_execute(
        self, quote_data: SwidgeQuoteData
    ) -> SwidgeExecuteResponse:
        """Handle swidge execute requests."""
        self._sdk._log("=== SWIDGE EXECUTE ===")
        self._sdk._log("Quote:", quote_data)
        self._sdk._log("Testing mode:", self._sdk.config.testing)
        self._sdk._log("=====================")

        try:
            if self._sdk.config.testing:
                import time

                execute_data = {
                    "status": "success",
                    "in": {
                        "network": quote_data.assetSend.network,
                        "txs": [
                            "0x1234567890123456789012345678901234567890123456789012345678901234"
                        ],
                    },
                    "out": {
                        "network": quote_data.assetReceive.network,
                        "txs": [
                            "0x1234567890123456789012345678901234567890123456789012345678901234"
                        ],
                    },
                    "lastUpdated": int(
                        time.time() * 1000
                    ),  # Current timestamp in milliseconds
                }
                return SwidgeExecuteResponse(
                    success=True,
                    error=None,
                    errorDetails=None,
                    data=SwidgeExecuteResponseData.model_validate(execute_data),
                )

            self._sdk._log("Making execute request to /v1/swidge/execute")
            response = self._sdk.client.post(
                "/v1/swidge/execute",
                quote_data.model_dump(by_alias=True, exclude_none=True),
            )
            self._sdk._log("Execute response received:", response)

            return SwidgeExecuteResponse(
                success=True,
                error=None,
                errorDetails=None,
                data=SwidgeExecuteResponseData(**response),
            )
        except Exception as error:
            self._sdk._log("=== SWIDGE EXECUTE ERROR ===")
            self._sdk._log("Error:", error)
            self._sdk._log("============================")

            error_message = "Failed to execute swidge swap"
            status = None
            status_text = None

            if isinstance(error, Exception):
                error_message = str(error)

                # Try to extract HTTP status from error message
                if hasattr(error, "response") and hasattr(
                    error.response, "status_code"
                ):
                    status = error.response.status_code
                    if hasattr(error.response, "reason"):
                        status_text = str(error.response.reason)

            return SwidgeExecuteResponse(
                success=False,
                data=None,
                error=error_message,
                errorDetails={
                    "message": error_message,
                    "status": status,
                    "statusText": status_text,
                },
            )
