"""
Webhook verification utilities for Simplex webhooks.

This module provides functions to verify the authenticity of webhook requests
from Simplex using HMAC-SHA256 signature verification.

Example usage:
    >>> from simplex import verify_simplex_webhook, WebhookVerificationError
    >>>
    >>> try:
    >>>     verify_simplex_webhook(
    >>>         body=request.body,
    >>>         signature=request.headers.get('X-Simplex-Signature'),
    >>>         webhook_secret='your-webhook-secret'
    >>>     )
    >>>     # Webhook verified, safe to process
    >>> except WebhookVerificationError as e:
    >>>     # Invalid webhook
    >>>     print(f"Verification failed: {e}")
"""

import hmac
import hashlib
from typing import Optional, Union, Dict


class WebhookVerificationError(Exception):
    """
    Exception raised when webhook verification fails.

    This error is raised when:
    - The signature header is missing
    - The signature is invalid
    - The signature doesn't match the expected value
    """

    def __init__(self, message: str):
        """
        Initialize a WebhookVerificationError.

        Args:
            message: Description of the verification failure
        """
        super().__init__(message)
        self.message = message


def verify_simplex_webhook(
    body: Union[str, bytes],
    signature: Optional[str],
    webhook_secret: str
) -> None:
    """
    Verify a Simplex webhook request using HMAC-SHA256 signature verification.

    This function ensures that webhook requests are authentic and haven't been
    tampered with in transit. It uses the same pattern as GitHub webhooks.

    The signature is computed as: HMAC-SHA256(webhook_secret, request_body)

    Args:
        body: Raw request body as string or bytes (must be the original unparsed body)
        signature: The X-Simplex-Signature header value from the request
        webhook_secret: Your webhook secret from the Simplex dashboard

    Raises:
        WebhookVerificationError: If signature is missing, invalid, or verification fails

    Example:
        >>> # Flask example
        >>> from flask import Flask, request, jsonify
        >>> from simplex import verify_simplex_webhook, WebhookVerificationError
        >>>
        >>> app = Flask(__name__)
        >>>
        >>> @app.route('/webhook', methods=['POST'])
        >>> def webhook():
        >>>     try:
        >>>         verify_simplex_webhook(
        >>>             body=request.get_data(as_text=True),
        >>>             signature=request.headers.get('X-Simplex-Signature'),
        >>>             webhook_secret='your-webhook-secret'
        >>>         )
        >>>
        >>>         # Webhook verified, safe to process
        >>>         payload = request.get_json()
        >>>         print(f"Received webhook: {payload['session_id']}")
        >>>         return jsonify({'received': True})
        >>>
        >>>     except WebhookVerificationError as e:
        >>>         return jsonify({'error': str(e)}), 401

    Example:
        >>> # FastAPI example
        >>> from fastapi import FastAPI, Request, HTTPException
        >>> from simplex import verify_simplex_webhook, WebhookVerificationError
        >>>
        >>> app = FastAPI()
        >>>
        >>> @app.post("/webhook")
        >>> async def webhook(request: Request):
        >>>     body = await request.body()
        >>>     signature = request.headers.get('X-Simplex-Signature')
        >>>
        >>>     try:
        >>>         verify_simplex_webhook(
        >>>             body=body,
        >>>             signature=signature,
        >>>             webhook_secret='your-webhook-secret'
        >>>         )
        >>>
        >>>         payload = await request.json()
        >>>         return {'received': True}
        >>>
        >>>     except WebhookVerificationError as e:
        >>>         raise HTTPException(status_code=401, detail=str(e))
    """
    # 1. Check required signature
    if not signature:
        raise WebhookVerificationError('Missing X-Simplex-Signature header')

    # 2. Ensure body is bytes for HMAC computation
    if isinstance(body, str):
        body_bytes = body.encode('utf-8')
    else:
        body_bytes = body

    # 3. Compute expected signature
    expected_signature = hmac.new(
        webhook_secret.encode('utf-8'),
        body_bytes,
        hashlib.sha256
    ).hexdigest()

    # 4. Compare signatures using constant-time comparison to prevent timing attacks
    if not hmac.compare_digest(expected_signature, signature):
        raise WebhookVerificationError('Invalid webhook signature')

    # Webhook verified successfully!


def verify_simplex_webhook_dict(
    body: Union[str, bytes],
    headers: Dict[str, str],
    webhook_secret: str
) -> None:
    """
    Verify a Simplex webhook request using a headers dictionary.

    This is a convenience wrapper around verify_simplex_webhook() that accepts
    a headers dictionary and handles case-insensitive header lookup.

    Args:
        body: Raw request body as string or bytes
        headers: Dictionary of request headers
        webhook_secret: Your webhook secret from the Simplex dashboard

    Raises:
        WebhookVerificationError: If verification fails

    Example:
        >>> verify_simplex_webhook_dict(
        >>>     body=request.body,
        >>>     headers=dict(request.headers),
        >>>     webhook_secret='your-secret'
        >>> )
    """
    # Try to find the signature header (case-insensitive)
    signature = None
    for key, value in headers.items():
        if key.lower() == 'x-simplex-signature':
            signature = value
            break

    verify_simplex_webhook(body, signature, webhook_secret)
