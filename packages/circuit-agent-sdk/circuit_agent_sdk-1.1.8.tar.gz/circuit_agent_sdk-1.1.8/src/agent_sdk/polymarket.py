"""
Polymarket prediction market operations.

This module provides the PolymarketApi class for interacting with Polymarket
prediction markets, including position management, market orders, and redemptions.
"""

from typing import TYPE_CHECKING, Any

from .types import (
    PolymarketMarketOrderData,
    PolymarketMarketOrderRequest,
    PolymarketMarketOrderResponse,
    PolymarketPositionsData,
    PolymarketPositionsResponse,
    PolymarketRedeemPositionsRequest,
    PolymarketRedeemPositionsResponse,
)

if TYPE_CHECKING:
    from .agent_sdk import AgentSdk


class PolymarketApi:
    """
    Polymarket prediction market operations.

    Provides access to positions, market orders, and position redemptions
    on the Polymarket platform using your session wallet.
    """

    def __init__(self, sdk: "AgentSdk"):
        self._sdk = sdk

    def positions(self) -> PolymarketPositionsResponse:
        """
        Get current positions on Polymarket.

        Fetches all open positions for the session wallet, including value, PNL, and market details.

        **Input**: None (GET request)

        **Output**: `PolymarketPositionsResponse`
            - `success` (bool): Whether the operation was successful
            - `data` (PolymarketPositionsData | None): Positions data (only present on success)
                - `totalValue` (float): Total portfolio value in USD
                - `positions` (list[PolymarketPosition]): List of position objects, each containing:
                    - `contractAddress` (str): ERC1155 contract address
                    - `tokenId` (str | None): Token ID for the outcome
                    - `decimals` (int): Token decimals
                    - `conditionId` (str): Unique condition identifier
                    - `formattedShares` (str): Human-readable share count
                    - `shares` (str): Raw share count in smallest unit
                    - `valueUsd` (str): Current position value in USD
                    - `question` (str): Market question text
                    - `outcome` (str): Outcome name (e.g., "Yes", "No")
                    - `priceUsd` (str): Current price per share in USD
                    - `averagePriceUsd` (str): Average purchase price per share in USD
                    - `isRedeemable` (bool): Whether position can be redeemed
                    - `imageUrl` (str): Market image URL
                    - `initialValue` (str): Initial position value in USD
                    - `pnlUsd` (str): Unrealized profit/loss in USD
                    - `pnlPercent` (str): Unrealized profit/loss percentage
                    - `pnlRealizedUsd` (str): Realized profit/loss in USD
                    - `pnlRealizedPercent` (str): Realized profit/loss percentage
                    - `endDate` (str): Market end date (ISO 8601 string)
            - `error` (str | None): Error message (only present on failure)
            - `errorDetails` (dict | None): Detailed error information (only present on failure)

        **Key Functionality**:
            - Retrieves all active positions across all markets
            - Includes real-time pricing and PNL calculations
            - Identifies redeemable positions from settled markets

        **Example**:
            ```python
            # Get all positions
            result = sdk.polymarket.positions()

            if result.success and result.data:
                print(f"Total portfolio value: ${result.data.totalValue}")
                for pos in result.data.positions:
                    print(f"{pos.question} - {pos.outcome}: ${pos.valueUsd} (PNL: {pos.pnlUsd})")
            else:
                print(f"Error: {result.error}")
            ```

        **Success Case**:
            ```python
            {
                "success": True,
                "data": {
                    "totalValue": 150.75,
                    "positions": [
                        {
                            "contractAddress": "0x...",
                            "tokenId": "123456",
                            "decimals": 6,
                            "conditionId": "0x...",
                            "formattedShares": "10.0",
                            "shares": "10000000",
                            "valueUsd": "10.5",
                            "question": "Will event X happen?",
                            "outcome": "Yes",
                            "priceUsd": "1.05",
                            "averagePriceUsd": "0.95",
                            "isRedeemable": False,
                            "imageUrl": "https://...",
                            "initialValue": "9.5",
                            "pnlUsd": "1.0",
                            "pnlPercent": "10.53",
                            "pnlRealizedUsd": "0",
                            "pnlRealizedPercent": "0",
                            "endDate": "2024-12-31"
                        }
                    ]
                },
                "error": None,
                "errorDetails": None
            }
            ```

        **Error Case**:
            ```python
            {
                "success": False,
                "data": None,
                "error": "Could not get positions",
                "errorDetails": {"message": "Wallet not found", "status": 400}
            }
            ```

        Returns:
            PolymarketPositionsResponse: Wrapped response with positions array and total value
        """
        return self._handle_polymarket_positions()

    def market_order(
        self, request: PolymarketMarketOrderRequest | dict
    ) -> PolymarketMarketOrderResponse:
        """
        Execute a market order on Polymarket.

        Places a buy or sell market order for the specified token and size. Handles approvals,
        signing, and submission automatically.

        ⚠️ **Important**: The `size` parameter meaning differs by order side:
        - **BUY**: `size` is the USD amount to spend (e.g., 10 = $10 worth of shares)
        - **SELL**: `size` is the number of shares/tokens to sell (e.g., 10 = 10 shares)

        **Input**: `PolymarketMarketOrderRequest`
            - `tokenId` (str): Market token ID for the position
            - `size` (float): For BUY: USD amount to spend. For SELL: Number of shares to sell
            - `side` (Literal["BUY", "SELL"]): Order side

        **Output**: `PolymarketMarketOrderResponse`
            - `success` (bool): Whether the operation was successful
            - `data` (PolymarketMarketOrderData | None): Market order data (only present on success)
                - `success` (bool): Whether the order was successfully submitted
                - `orderInfo` (PolymarketOrderInfo): Order information with transaction details
                    - `orderId` (str): Unique order identifier
                    - `side` (str): Order side ("BUY" or "SELL")
                    - `size` (str): Order size
                    - `priceUsd` (str): Price per share in USD
                    - `totalPriceUsd` (str): Total order value in USD
                    - `txHashes` (list[str]): List of transaction hashes
            - `error` (str | None): Error message (only present on failure)
            - `errorDetails` (dict | None): Detailed error information (only present on failure)

        **Key Functionality**:
            - Automatic approval handling for token spending
            - EIP-712 signature generation for order placement
            - Real-time order submission and confirmation
            - Support for both buy and sell orders

        **Example**:
            ```python
            # BUY order - size is USD amount
            buy_result = sdk.polymarket.market_order({
                "tokenId": "123456",
                "size": 10,  # Spend $10 to buy shares
                "side": "BUY"
            })

            # SELL order - size is number of shares
            sell_result = sdk.polymarket.market_order({
                "tokenId": "123456",
                "size": 5,  # Sell 5 shares
                "side": "SELL"
            })

            if buy_result.success and buy_result.data:
                print(f"Order Success: {buy_result.data.success}")
                print(f"Order ID: {buy_result.data.orderInfo.orderId}")
                print(f"Total Price: ${buy_result.data.orderInfo.totalPriceUsd}")
            else:
                print(f"Error: {buy_result.error}")
            ```

        **Success Case**:
            ```python
            {
                "success": True,
                "data": {
                    "success": True,
                    "orderInfo": {
                        "orderId": "abc123",
                        "side": "BUY",
                        "size": "10.0",
                        "priceUsd": "0.52",
                        "totalPriceUsd": "5.20",
                        "txHashes": ["0xabc..."]
                    }
                },
                "error": None,
                "errorDetails": None
            }
            ```

        **Error Case**:
            ```python
            {
                "success": False,
                "data": None,
                "error": "Could not get order",
                "errorDetails": {"message": "Invalid request", "status": 400}
            }
            ```

        Args:
            request: Order parameters (tokenId, size, side)

        Returns:
            PolymarketMarketOrderResponse: Wrapped response with order details and submission result
        """
        return self._handle_polymarket_market_order(request)

    def redeem_positions(
        self, request: PolymarketRedeemPositionsRequest | dict | None = None
    ) -> PolymarketRedeemPositionsResponse:
        """
        Redeem settled positions on Polymarket.

        Redeems one or all redeemable positions, claiming winnings. Handles multiple transactions if needed.

        **Input**: `PolymarketRedeemPositionsRequest` (optional, defaults to redeem all)
            - `tokenIds` (list[str], optional): List of token IDs to redeem specific positions. Empty or omitted redeems all redeemable positions.

        **Output**: `PolymarketRedeemPositionsResponse`
            - `success` (bool): Whether the operation was successful
            - `data` (list[PolymarketRedeemPositionResult] | None): Redeem positions data (only present on success)
                Each result contains:
                    - `success` (bool): Whether redemption was successful
                    - `position` (PolymarketPosition): Position that was redeemed (full position details)
                    - `transactionHash` (str | None): Transaction hash (null if redemption failed)
            - `error` (str | None): Error message (only present on failure)
            - `errorDetails` (dict | None): Detailed error information (only present on failure)

        **Key Functionality**:
            - Automatic detection of redeemable positions
            - Batch redemption support for multiple positions
            - Single position redemption by token ID
            - Transaction tracking for each redemption

        **Example**:
            ```python
            # Redeem all positions (no arguments - default behavior)
            all_result = sdk.polymarket.redeem_positions()

            # Redeem specific positions
            specific_result = sdk.polymarket.redeem_positions({"tokenIds": ["123456", "789012"]})

            if all_result.success and all_result.data:
                for tx in all_result.data:
                    if tx.success and tx.position:
                        print(f"Redeemed {tx.position.question}: Tx {tx.transactionHash}")
                    elif tx.success:
                        print(f"Unwrapped collateral: Tx {tx.transactionHash}")
                    elif tx.position:
                        print(f"Failed to redeem {tx.position.question}")
            else:
                print(f"Error: {all_result.error}")
            ```

        **Success Case (Multiple Redemptions)**:
            ```python
            {
                "success": True,
                "data": [
                    {
                        "success": True,
                        "position": {
                            "contractAddress": "0x...",
                            "tokenId": "123456",
                            "question": "Will event X happen?",
                            "outcome": "Yes",
                            # ... full position details
                        },
                        "transactionHash": "0xabc123..."
                    },
                    {
                        "success": True,
                        "position": {
                            "contractAddress": "0x...",
                            "tokenId": "789012",
                            "question": "Will event Y happen?",
                            "outcome": "No",
                            # ... full position details
                        },
                        "transactionHash": "0xdef456..."
                    },
                    {
                        "success": True,
                        "position": None,  # None for unwrap collateral transactions
                        "transactionHash": "0xghi789..."
                    }
                ],
                "error": None,
                "errorDetails": None
            }
            ```

        **Error Case**:
            ```python
            {
                "success": False,
                "data": None,
                "error": "Could not get positions",
                "errorDetails": {"message": "No redeemable positions", "status": 404}
            }
            ```

        Args:
            request: Redemption parameters (tokenIds list for specific positions, empty for all)

        Returns:
            PolymarketRedeemPositionsResponse: Wrapped response with per-position redemption results
        """
        return self._handle_polymarket_redeem_positions(request)

    def _handle_polymarket_positions(self) -> PolymarketPositionsResponse:
        """Handle polymarket positions requests."""
        self._sdk._log("=== POLYMARKET POSITIONS ===")
        self._sdk._log("Testing mode:", self._sdk.config.testing)
        self._sdk._log("===========================")

        try:
            if self._sdk.config.testing:
                return PolymarketPositionsResponse(
                    success=True,
                    data=PolymarketPositionsData(totalValue=0, positions=[]),
                    error=None,
                    errorDetails=None,
                )

            response = self._sdk.client.get("/v1/platforms/polymarket/positions")

            return PolymarketPositionsResponse(
                success=True,
                data=PolymarketPositionsData(**response),
                error=None,
                errorDetails=None,
            )
        except Exception as error:
            self._sdk._log("=== POLYMARKET POSITIONS ERROR ===")
            self._sdk._log("Error:", error)
            self._sdk._log("=================================")

            error_message = "Failed to get polymarket positions"
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

            return PolymarketPositionsResponse(
                success=False,
                data=None,
                error=error_message,
                errorDetails={
                    "message": error_message,
                    "status": status,
                    "statusText": status_text,
                },
            )

    def _handle_polymarket_market_order(
        self, request: PolymarketMarketOrderRequest | dict
    ) -> PolymarketMarketOrderResponse:
        """Handle polymarket market order requests."""
        self._sdk._log("=== POLYMARKET MARKET ORDER ===")
        self._sdk._log("Request:", request)
        self._sdk._log("Testing mode:", self._sdk.config.testing)
        self._sdk._log("==============================")

        try:
            # Handle both dict and Pydantic model inputs
            if isinstance(request, dict):
                request_obj = PolymarketMarketOrderRequest(**request)
            else:
                request_obj = request

            if self._sdk.config.testing:
                from .types.polymarket import PolymarketOrderInfo

                test_data = PolymarketMarketOrderData(
                    success=True,
                    orderInfo=PolymarketOrderInfo(
                        orderId="test-order-id",
                        side="BUY",
                        size="1.0",
                        priceUsd="0.50",
                        totalPriceUsd="0.50",
                        txHashes=["0xtest"],
                    ),
                )
                return PolymarketMarketOrderResponse(
                    success=True,
                    data=test_data,
                    error=None,
                    errorDetails=None,
                )

            response = self._sdk.client.post(
                "/v1/platforms/polymarket/market-order",
                request_obj.model_dump(exclude_none=True),
            )

            return PolymarketMarketOrderResponse(
                success=True,
                data=PolymarketMarketOrderData(**response),
                error=None,
                errorDetails=None,
            )
        except Exception as error:
            self._sdk._log("=== POLYMARKET MARKET ORDER ERROR ===")
            self._sdk._log("Error:", error)
            self._sdk._log("====================================")

            error_message = "Failed to execute polymarket market order"
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

            return PolymarketMarketOrderResponse(
                success=False,
                data=None,
                error=error_message,
                errorDetails={
                    "message": error_message,
                    "status": status,
                    "statusText": status_text,
                },
            )

    def _handle_polymarket_redeem_positions(
        self, request: PolymarketRedeemPositionsRequest | dict | None
    ) -> PolymarketRedeemPositionsResponse:
        """Handle polymarket redeem positions requests."""
        self._sdk._log("=== POLYMARKET REDEEM POSITIONS ===")
        self._sdk._log("Request:", request)
        self._sdk._log("Testing mode:", self._sdk.config.testing)
        self._sdk._log("==================================")

        try:
            # Handle None, dict, and Pydantic model inputs
            if request is None:
                request_obj = PolymarketRedeemPositionsRequest()
            elif isinstance(request, dict):
                request_obj = PolymarketRedeemPositionsRequest(**request)
            else:
                request_obj = request

            if self._sdk.config.testing:
                return PolymarketRedeemPositionsResponse(
                    success=True,
                    data=[],
                    error=None,
                    errorDetails=None,
                )

            response = self._sdk.client.post(
                "/v1/platforms/polymarket/redeem-positions",
                request_obj.model_dump(exclude_none=True),
            )

            # Parse response data into list of PolymarketRedeemPositionResult
            # Note: API returns a list, not a dict, for this endpoint
            from typing import cast

            from .types.polymarket import PolymarketRedeemPositionResult

            parsed_data: list[PolymarketRedeemPositionResult] | None = None
            if response:
                # Cast because client.post is typed as returning dict, but this endpoint returns list
                response_list = cast(list[dict[str, Any]], response)
                parsed_data = [
                    PolymarketRedeemPositionResult(**item) for item in response_list
                ]

            return PolymarketRedeemPositionsResponse(
                success=True,
                data=parsed_data,
                error=None,
                errorDetails=None,
            )
        except Exception as error:
            self._sdk._log("=== POLYMARKET REDEEM POSITIONS ERROR ===")
            self._sdk._log("Error:", error)
            self._sdk._log("========================================")

            error_message = "Failed to redeem polymarket positions"
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

            return PolymarketRedeemPositionsResponse(
                success=False,
                data=None,
                error=error_message,
                errorDetails={
                    "message": error_message,
                    "status": status,
                    "statusText": status_text,
                },
            )
