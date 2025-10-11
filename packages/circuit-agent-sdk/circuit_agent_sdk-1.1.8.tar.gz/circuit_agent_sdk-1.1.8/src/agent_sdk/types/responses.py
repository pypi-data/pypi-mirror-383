"""
Response type definitions for the Agent SDK.

This module provides all response models returned by SDK operations.
All models use strict Pydantic validation for type safety.
"""

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

from .swidge import SwidgeExecuteResponseData, SwidgeQuoteData


class SignAndSendResponse(BaseModel):
    """
    Standard response from sign_and_send operations.

    This response is returned after attempting to sign and broadcast
    a transaction through the Circuit backend.

    Attributes:
        success: Whether the operation was successful
        internal_transaction_id: Internal transaction ID for tracking (only present on success)
        tx_hash: Transaction hash once broadcast to the network (only present on success)
        transaction_url: Optional transaction URL (explorer link) (only present on success)
        error: Error message (only present on failure)
        error_details: Detailed error information (only present on failure)

    Example:
        ```python
        response = sdk.sign_and_send({
            "network": "ethereum:1",
            "request": {"toAddress": "0x...", "data": "0x", "value": "0"}
        })
        if response.success:
            print(f"Transaction hash: {response.tx_hash}")
            if response.transaction_url:
                print(f"View on explorer: {response.transaction_url}")
        else:
            print(f"Transaction failed: {response.error}")
        ```
    """

    success: bool = Field(..., description="Whether the operation was successful")
    internal_transaction_id: int | None = Field(
        None,
        description="Internal transaction ID for tracking (only present on success)",
    )
    tx_hash: str | None = Field(
        None, description="Transaction hash once broadcast (only present on success)"
    )
    transaction_url: str | None = Field(
        None,
        description="Optional transaction URL (explorer link) (only present on success)",
    )
    error: str | None = Field(
        None, description="Error message (only present on failure)"
    )
    error_details: dict | None = Field(
        None, description="Detailed error information (only present on failure)"
    )

    model_config = ConfigDict(extra="ignore")


class EvmMessageSignResponse(BaseModel):
    """Response from EVM message signing."""

    status: int
    v: int
    r: str
    s: str
    formattedSignature: str
    type: Literal["evm"]


class SwidgeQuoteResponse(BaseModel):
    """
    Swidge quote response wrapper.

    Attributes:
        success: Whether the operation was successful
        data: Quote data (only present on success)
        error: Error message (only present on failure)
        errorDetails: Detailed error information (only present on failure)
    """

    success: bool = Field(..., description="Whether the operation was successful")
    data: SwidgeQuoteData | None = Field(
        None, description="Quote data (only present on success)"
    )
    error: str | None = Field(
        None, description="Error message (only present on failure)"
    )
    errorDetails: dict[str, Any] | None = Field(
        None, description="Detailed error information (only present on failure)"
    )

    model_config = ConfigDict(extra="ignore")


class SwidgeExecuteResponse(BaseModel):
    """
    Swidge execute response wrapper.

    Attributes:
        success: Whether the operation was successful
        data: Execute response data (only present on success)
        error: Error message (only present on failure)
        errorDetails: Detailed error information (only present on failure)
    """

    success: bool = Field(..., description="Whether the operation was successful")
    data: SwidgeExecuteResponseData | None = Field(
        None, description="Execute response data (only present on success)"
    )
    error: str | None = Field(
        None, description="Error message (only present on failure)"
    )
    errorDetails: dict[str, Any] | None = Field(
        None, description="Detailed error information (only present on failure)"
    )

    model_config = ConfigDict(extra="ignore")


class UpdateJobStatusResponse(BaseModel):
    """Response from job status update."""

    status: int = Field(..., description="HTTP status code")
    message: str = Field(..., description="Response message")

    model_config = ConfigDict(extra="ignore")
