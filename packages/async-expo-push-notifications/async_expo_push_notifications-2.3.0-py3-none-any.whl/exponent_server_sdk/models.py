"""
Pydantic models for Expo push notifications.
"""

from typing import Any, ClassVar, Dict, List, Optional, Union
from pydantic import BaseModel, Field, field_validator, ConfigDict

from .exceptions import (
    DeviceNotRegisteredError,
    MessageTooBigError,
    MessageRateExceededError,
    InvalidCredentialsError,
    PushTicketError,
)


class PushMessage(BaseModel):
    """An object that describes a push notification request.

    You can override this class to provide your own custom validation before
    sending these to the Exponent push servers. You can also override the
    get_payload function itself to take advantage of any hidden or new
    arguments before this library updates upstream.

        Args:
            to: A token of the form ExponentPushToken[xxxxxxx] or a list of tokens
            data: A dict of extra data to pass inside of the push notification.
                The total notification payload must be at most 4096 bytes.
            title: The title to display in the notification. On iOS, this is
                displayed only on Apple Watch.
            body: The message to display in the notification.
            sound: A sound to play when the recipient receives this
                notification. Specify "default" to play the device's default
                notification sound, or omit this field to play no sound.
            ttl: The number of seconds for which the message may be kept around
                for redelivery if it hasn't been delivered yet. Defaults to 0.
            expiration: UNIX timestamp for when this message expires. It has
                the same effect as ttl, and is just an absolute timestamp
                instead of a relative one.
            priority: Delivery priority of the message. 'default', 'normal',
                and 'high' are the only valid values.
            badge: An integer representing the unread notification count. This
                currently only affects iOS. Specify 0 to clear the badge count.
            category: ID of the Notification Category through which to display
                 this notification.
            channel_id: ID of the Notification Channel through which to display
                this notification on Android devices.
            display_in_foreground: Displays the notification when the app is
                foregrounded. Defaults to `false`. No longer available?
            subtitle: The subtitle to display in the notification below the
                title (iOS only).
            richContent: Currently supports setting a notification image.
                Provide an object with key image and value of type string, which is the image URL.
                Android will show the image out of the box.
            mutable_content: Specifies whether this notification can be
                intercepted by the client app. In Expo Go, defaults to true.
                In standalone and bare apps, defaults to false. (iOS Only)

    """
    model_config = ConfigDict(populate_by_name=True)

    to: Union[str, List[str]]
    data: Optional[Dict[str, Any]] = None
    title: Optional[str] = None
    body: Optional[str] = None
    sound: Optional[str] = None
    ttl: Optional[int] = None
    expiration: Optional[int] = None
    priority: Optional[str] = None
    badge: Optional[int] = None
    category: Optional[str] = None
    display_in_foreground: Optional[bool] = None
    channel_id: Optional[str] = None
    subtitle: Optional[str] = None
    richContent: Optional[Dict[str, Any]] = Field(None, alias='rich_content')
    mutable_content: Optional[bool] = None

    @field_validator('to')
    @classmethod
    def validate_token(cls, v: Union[str, List[str]]) -> Union[str, List[str]]:
        """Validate that the push token(s) are in the correct format."""
        def is_valid_token(token: str) -> bool:
            return isinstance(token, str) and token.startswith('ExponentPushToken')

        if isinstance(v, list):
            for token in v:
                if not is_valid_token(token):
                    raise ValueError(f'Invalid push token: {token}')
        else:
            if not is_valid_token(v):
                raise ValueError(f'Invalid push token: {v}')
        return v

    @field_validator('priority')
    @classmethod
    def validate_priority(cls, v: Optional[str]) -> Optional[str]:
        """Validate priority values."""
        if v is not None and v not in ['default', 'normal', 'high']:
            raise ValueError(f'Priority must be one of: default, normal, high. Got: {v}')
        return v

    def get_payload(self) -> Dict[str, Any]:
        """Convert the PushMessage to a dictionary payload for the API."""
        # There is only one required field.
        payload: Dict[str, Any] = {
            'to': self.to,
        }

        # All of these fields are optional.
        if self.data is not None:
            payload['data'] = self.data
        if self.title is not None:
            payload['title'] = self.title
        if self.body is not None:
            payload['body'] = self.body
        if self.ttl is not None:
            payload['ttl'] = self.ttl
        if self.expiration is not None:
            payload['expiration'] = self.expiration
        if self.priority is not None:
            payload['priority'] = self.priority
        if self.subtitle is not None:
            payload['subtitle'] = self.subtitle
        if self.sound is not None:
            payload['sound'] = self.sound
        if self.badge is not None:
            payload['badge'] = self.badge
        if self.channel_id is not None:
            payload['channelId'] = self.channel_id
        if self.category is not None:
            payload['categoryId'] = self.category
        if self.mutable_content is not None:
            payload['mutableContent'] = self.mutable_content
        if self.richContent is not None:
            payload['richContent'] = self.richContent

        # here for legacy reasons
        if self.display_in_foreground is not None:
            payload['_displayInForeground'] = self.display_in_foreground
        return payload


class PushTicket(BaseModel):
    """Wrapper class for a push notification response.

    A successful single push notification:
        {'status': 'ok'}

    An invalid push token
        {'status': 'error',
         'message': '"adsf" is not a registered push notification recipient'}
    """
    model_config = ConfigDict(arbitrary_types_allowed=True)

    push_message: Optional[PushMessage] = None
    status: str
    message: str = ''
    details: Optional[Dict[str, Any]] = None
    id: str = ''

    # Known status codes
    ERROR_STATUS: ClassVar[str] = 'error'
    SUCCESS_STATUS: ClassVar[str] = 'ok'

    # Known error strings
    ERROR_DEVICE_NOT_REGISTERED: ClassVar[str] = 'DeviceNotRegistered'
    ERROR_MESSAGE_TOO_BIG: ClassVar[str] = 'MessageTooBig'
    ERROR_MESSAGE_RATE_EXCEEDED: ClassVar[str] = 'MessageRateExceeded'

    def is_success(self) -> bool:
        """Returns True if this push notification successfully sent."""
        return self.status == self.SUCCESS_STATUS

    def validate_response(self) -> None:
        """Raises an exception if there was an error. Otherwise, do nothing.

        Clients should handle these errors, since these require custom handling
        to properly resolve.
        """
        if self.is_success():
            return

        # Handle the error if we have any information
        if self.details:
            error = self.details.get('error', None)

            if error == self.ERROR_DEVICE_NOT_REGISTERED:
                raise DeviceNotRegisteredError(self)
            elif error == self.ERROR_MESSAGE_TOO_BIG:
                raise MessageTooBigError(self)
            elif error == self.ERROR_MESSAGE_RATE_EXCEEDED:
                raise MessageRateExceededError(self)

        # No known error information, so let's raise a generic error.
        raise PushTicketError(self)


class PushReceipt(BaseModel):
    """Wrapper class for a PushReceipt response. Similar to a PushResponse

    A successful single push notification:
        'data': {
            'id': {'status': 'ok'}
        }
    Errors contain 'errors'

    """
    id: str
    status: str
    message: str = ''
    details: Optional[Dict[str, Any]] = None

    # Known status codes
    ERROR_STATUS: ClassVar[str] = 'error'
    SUCCESS_STATUS: ClassVar[str] = 'ok'

    # Known error strings
    ERROR_DEVICE_NOT_REGISTERED: ClassVar[str] = 'DeviceNotRegistered'
    ERROR_MESSAGE_TOO_BIG: ClassVar[str] = 'MessageTooBig'
    ERROR_MESSAGE_RATE_EXCEEDED: ClassVar[str] = 'MessageRateExceeded'
    INVALID_CREDENTIALS: ClassVar[str] = 'InvalidCredentials'

    def is_success(self) -> bool:
        """Returns True if this push notification successfully sent."""
        return self.status == self.SUCCESS_STATUS

    def validate_response(self) -> None:
        """Raises an exception if there was an error. Otherwise, do nothing.

        Clients should handle these errors, since these require custom handling
        to properly resolve.
        """
        if self.is_success():
            return

        # Handle the error if we have any information
        if self.details:
            error = self.details.get('error', None)

            if error == self.ERROR_DEVICE_NOT_REGISTERED:
                raise DeviceNotRegisteredError(self)
            elif error == self.ERROR_MESSAGE_TOO_BIG:
                raise MessageTooBigError(self)
            elif error == self.ERROR_MESSAGE_RATE_EXCEEDED:
                raise MessageRateExceededError(self)
            elif error == self.INVALID_CREDENTIALS:
                raise InvalidCredentialsError(self)

        # No known error information, so let's raise a generic error.
        raise PushTicketError(self)
