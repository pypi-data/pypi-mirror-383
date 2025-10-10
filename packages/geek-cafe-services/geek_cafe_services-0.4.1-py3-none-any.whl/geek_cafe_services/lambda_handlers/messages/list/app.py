"""
Lambda handler for listing message threads.

REFACTORED to use Factory Pattern.
Auth controlled by AUTH_TYPE environment variable (defaults to secure).
"""

from typing import Dict, Any
from geek_cafe_services.lambda_handlers import create_handler
from geek_cafe_services.services import MessageThreadService

# Factory creates handler based on AUTH_TYPE (defaults to secure)
handler_wrapper = create_handler(
    service_class=MessageThreadService,
    require_body=False
)


def handler(event: Dict[str, Any], context: Any, injected_service=None) -> Dict[str, Any]:
    """
    List message threads for the authenticated user.
    
    Args:
        event: Lambda event
        context: Lambda context
        injected_service: Optional MessageThreadService for testing (Moto)
    
    Returns threads where the user is a participant.
    """
    return handler_wrapper.execute(event, context, list_messages, injected_service)


def list_messages(
    event: Dict[str, Any],
    service: MessageThreadService,
    user_context: Dict[str, str]
) -> Any:
    """Business logic for listing message threads."""
    # List threads where user is a participant
    return service.list_by_participant(
        participant_id=user_context["user_id"],
        tenant_id=user_context["tenant_id"]
    )
