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
    
    All boilerplate handled by factory:
    ✅ Authentication (API key or Cognito)
    ✅ Body parsing (camelCase → snake_case)
    ✅ Service initialization
    ✅ User context extraction
    ✅ CORS and error handling
    """
    payload = event["parsed_body"]
    
    # Get user info from context
    # For contact form: tenant_id/user_id from body or defaults to anonymous
    # For app: tenant_id/user_id from Cognito claims
    tenant_id = user_context.get("tenant_id") or payload.get("tenant_id", "anonymous")
    user_id = user_context.get("user_id") or payload.get("user_id", "anonymous")
    
    # Create message thread
    result = service.create(
        tenant_id=tenant_id,
        user_id=user_id,
        subject=payload.get("subject"),
        participants=payload.get("participants"),
        initial_message=payload.get("initial_message"),
        type=payload.get("type", "general"),
        event_id=payload.get("event_id"),
        event_title=payload.get("event_title")
    )
    
    # Handler automatically formats response with 201 status
    return result
