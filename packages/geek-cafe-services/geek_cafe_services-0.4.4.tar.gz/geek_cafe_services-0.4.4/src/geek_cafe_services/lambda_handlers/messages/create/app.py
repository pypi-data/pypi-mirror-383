"""
Lambda handler for creating message threads.

REFACTORED to use Factory Pattern.
Auth strategy is controlled by AUTH_TYPE environment variable:
- AUTH_TYPE=api_key - For public contact forms (validates x-api-key)
- AUTH_TYPE=secure - For authenticated app users (API Gateway authorizer)

This handler works for BOTH use cases based on environment configuration.
"""

from typing import Dict, Any
from geek_cafe_services.lambda_handlers import create_handler
from geek_cafe_services.services import MessageThreadService

# Factory automatically selects handler based on AUTH_TYPE env var:
#   - api_key: Public contact form with API key validation
#   - secure: Authenticated app users with API Gateway authorizer
handler_wrapper = create_handler(
    service_class=MessageThreadService,
    require_body=True,
    convert_case=True
)


def handler(event: Dict[str, Any], context: Any, injected_service=None) -> Dict[str, Any]:
    """
    Create a new message thread.
    
    Two deployment modes:
    
    1. Public Contact Form (AUTH_TYPE=api_key):
       - Validates x-api-key header
       - Creates message from anonymous/public user
       - Used for website contact forms
    
    2. Authenticated App (AUTH_TYPE=secure):
       - Trusts API Gateway Cognito authorizer
       - Creates message from logged-in user
       - Used for in-app messaging
    
    Args:
        event: Lambda event from API Gateway
        context: Lambda context
        injected_service: Optional MessageThreadService for testing (Moto)
    
    Expected body (camelCase from frontend):
    {
        "subject": "Contact inquiry",
        "participants": ["user1", "user2"],
        "initialMessage": "Message content",
        "type": "general" | "event",
        "eventId": "event-123" (optional),
        "eventTitle": "Event name" (optional)
    }
    """
    return handler_wrapper.execute(event, context, create_message, injected_service)


def create_message(
    event: Dict[str, Any],
    service: MessageThreadService,
    user_context: Dict[str, str]
) -> Any:
    """
    Business logic for creating message threads.

    Handles both authenticated users (from Cognito) and unauthenticated
    users (from public contact forms with API keys).
    """
    payload = event["parsed_body"]

    # Determine Tenant and User ID with clear priority:
    # 1. Use authenticated user from Cognito if available (most secure).
    # 2. Fall back to payload for API key/public requests.
    # 3. Default to 'anonymous' if nothing is provided.
    tenant_id = user_context.get("tenant_id") or payload.get("tenant_id", "anonymous")
    
    # For the user ID, we MUST ensure the creator is a participant.
    # If authenticated, the user_id from the token is the source of truth.
    # If public, the user_id can be passed in the payload (e.g., a session ID).
    authenticated_user_id = user_context.get("user_id")
    if authenticated_user_id:
        user_id = authenticated_user_id
    else:
        # For API key requests, allow userId to be specified in the body
        user_id = payload.get("user_id", "anonymous")

    # The service's create method expects keyword arguments that match the
    # MessageThread model properties.
    create_kwargs = {
        "subject": payload.get("subject"),
        "participants": payload.get("participants"),
        "initial_message": payload.get("initial_message"),
        "type": payload.get("type", "general"),
        "event_id": payload.get("event_id"),
        "event_title": payload.get("event_title")
    }

    # Create message thread
    result = service.create(
        tenant_id=tenant_id,
        user_id=user_id,  # This is the creator ID
        **create_kwargs
    )

    # Handler automatically formats the response with a 201 status code on success
    return result
