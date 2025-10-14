"""
Exception classes for Expo push notifications.
"""

from typing import TYPE_CHECKING, Union, Dict, Any, List, Optional
import requests
import httpx

if TYPE_CHECKING:
    from .models import PushTicket, PushReceipt


class PushTicketError(Exception):
    """Base class for all push ticket errors"""

    def __init__(self, push_response: Union['PushTicket', 'PushReceipt']) -> None:
        if push_response.message:
            self.message: str = push_response.message
        else:
            self.message = 'Unknown push ticket error'
        super(PushTicketError, self).__init__(self.message)

        self.push_response: Union['PushTicket', 'PushReceipt'] = push_response


class DeviceNotRegisteredError(PushTicketError):
    """Raised when the push token is invalid

    To handle this error, you should stop sending messages to this token.
    """
    pass


class MessageTooBigError(PushTicketError):
    """Raised when the notification was too large.

    On Android and iOS, the total payload must be at most 4096 bytes.
    """
    pass


class MessageRateExceededError(PushTicketError):
    """Raised when you are sending messages too frequently to a device

    You should implement exponential backoff and slowly retry sending messages.
    """
    pass


class InvalidCredentialsError(PushTicketError):
    """Raised when our push notification credentials for your standalone app
    are invalid (ex: you may have revoked them).

    Run expo build:ios -c to regenerate new push notification credentials for
    iOS. If you revoke an APN key, all apps that rely on that key will no
    longer be able to send or receive push notifications until you upload a
    new key to replace it. Uploading a new APN key will not change your users'
    Expo Push Tokens.
    """
    pass


class PushServerError(Exception):
    """Raised when the push token server is not behaving as expected

    For example, invalid push notification arguments result in a different
    style of error. Instead of a "data" array containing errors per
    notification, an "error" array is returned.

    {"errors": [
      {"code": "API_ERROR",
       "message": "child \"to\" fails because [\"to\" must be a string]. \"value\" must be an array."
      }
    ]}
    """

    def __init__(
        self,
        message: str,
        response: Union[requests.Response, httpx.Response],
        response_data: Optional[Dict[str, Any]] = None,
        errors: Optional[List[Dict[str, Any]]] = None
    ) -> None:
        self.message: str = message
        self.response: Union[requests.Response, httpx.Response] = response
        self.response_data: Optional[Dict[str, Any]] = response_data
        self.errors: Optional[List[Dict[str, Any]]] = errors
        super(PushServerError, self).__init__(self.message)
