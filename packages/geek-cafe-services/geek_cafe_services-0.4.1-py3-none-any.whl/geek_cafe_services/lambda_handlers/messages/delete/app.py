"""
Lambda handler for deleting a message thread.

REFACTORED to use Factory Pattern.
Auth controlled by AUTH_TYPE environment variable (defaults to secure).
"""

from typing import Dict, Any
from geek_cafe_services.lambda_handlers import create_handler
from geek_cafe_services.services import MessageThreadService
from geek_cafe_services.utilities.response import error_response

# Factory creates handler based on AUTH_TYPE (defaults to secure)
handler_wrapper = create_handler(
    service_class=MessageThreadService,
    require_body=False
)


def handler(event: Dict[str, Any], context: Any, injected_service=None) -> Dict[str, Any]:
    """
    Delete a message thread.
    
    Args:
        event: Lambda event
        context: Lambda context
        injected_service: Optional MessageThreadService for testing (Moto)
    
    Path parameter: id (message thread ID)
    """
    return handler_wrapper.execute(event, context, delete_message, injected_service)


def delete_message(
    event: Dict[str, Any],
    service: MessageThreadService,
    user_context: Dict[str, str]
) -> Any:
    """Business logic for deleting message thread."""
    resource_id = event.get('pathParameters', {}).get('id')
    
    if not resource_id:
        return error_response("Message thread ID is required in the path", 400)
    
    return service.delete(
        resource_id=resource_id,
        tenant_id=user_context["tenant_id"],
        user_id=user_context["user_id"]
    )
