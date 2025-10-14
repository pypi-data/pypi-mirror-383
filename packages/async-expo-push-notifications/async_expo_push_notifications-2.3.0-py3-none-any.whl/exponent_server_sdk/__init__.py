import json
import itertools
from typing import Any, ClassVar, Dict, List, Optional, Union, Protocol
import requests
import httpx
from urllib.parse import urljoin, urlencode
from pydantic import BaseModel, Field, field_validator, ConfigDict


class PushTicketError(Exception):
    """Base class for all push ticket errors"""
    def __init__(self, push_response: 'PushTicket') -> None:
        if push_response.message:
            self.message: str = push_response.message
        else:
            self.message = 'Unknown push ticket error'
        super(PushTicketError, self).__init__(self.message)

        self.push_response: 'PushTicket' = push_response


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


# HTTP Client Protocol for Dependency Injection
class HTTPClientProtocol(Protocol):
    """Protocol for HTTP clients that can be injected into PushClient."""

    def post(
        self,
        url: str,
        data: Optional[str] = None,
        json: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[float] = None,
    ) -> requests.Response:
        """Make a POST request."""
        ...


class AsyncHTTPClientProtocol(Protocol):
    """Protocol for async HTTP clients that can be injected into AsyncPushClient."""

    async def post(
        self,
        url: str,
        data: Optional[str] = None,
        json: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[float] = None,
    ) -> httpx.Response:
        """Make an async POST request."""
        ...


class SyncPushClient:
    """Exponent push client (synchronous)

    See full API docs at https://docs.expo.io/versions/latest/guides/push-notifications.html#http2-api
    """
    DEFAULT_HOST = "https://exp.host"
    DEFAULT_BASE_API_URL = "/--/api/v2"
    DEFAULT_MAX_MESSAGE_COUNT = 100
    DEFAULT_MAX_RECEIPT_COUNT = 1000

    def __init__(
        self,
        host: Optional[str] = None,
        api_url: Optional[str] = None,
        session: Optional[requests.Session] = None,
        force_fcm_v1: Optional[bool] = None,
        **kwargs: Any
    ) -> None:
        """Construct a new SyncPushClient object.

        Args:
            host: The server protocol, hostname, and port.
            api_url: The api url at the host.
            session: Pass in your own requests.Session object if you prefer
                to customize
            force_fcm_v1: If True, send Android notifications via FCM V1, regardless
                of whether a valid credential exists.
        """
        self.host: str = host if host else self.DEFAULT_HOST
        self.api_url: str = api_url if api_url else self.DEFAULT_BASE_API_URL
        self.force_fcm_v1: Optional[bool] = force_fcm_v1

        self.max_message_count: int = kwargs.get('max_message_count', self.DEFAULT_MAX_MESSAGE_COUNT)
        self.max_receipt_count: int = kwargs.get('max_receipt_count', self.DEFAULT_MAX_RECEIPT_COUNT)
        self.timeout: Optional[float] = kwargs.get('timeout', None)

        self.session: requests.Session
        if session:
            self.session = session
        else:
            self.session = requests.Session()
            self.session.headers.update({
                'accept': 'application/json',
                'accept-encoding': 'gzip, deflate',
                'content-type': 'application/json',
            })

    @classmethod
    def is_exponent_push_token(cls, token: Union[str, List[str]]) -> bool:
        """Returns `True` if the token is an Exponent push token"""
        if isinstance(token, list):
            return all(isinstance(t, str) and t.startswith('ExponentPushToken') for t in token)
        return isinstance(token, str) and token.startswith('ExponentPushToken')

    def _publish_internal(self, push_messages: List[PushMessage]) -> List[PushTicket]:
        """Send push notifications

        The server will validate any type of syntax errors and the client will
        raise the proper exceptions for the user to handle.

        Each notification is of the form:
        {
          'to': 'ExponentPushToken[xxx]',
          'body': 'This text gets display in the notification',
          'badge': 1,
          'data': {'any': 'json object'},
        }
        or
        {
          'to': ['ExponentPushToken[xxx]', 'ExponentPushToken[yyy]'],
          'body': 'This text gets display in the notification',
          'badge': 1,
          'data': {'any': 'json object'},
        }

        Args:
            push_messages: An array of PushMessage objects.
        """

        url = urljoin(self.host, self.api_url + '/push/send')
        if self.force_fcm_v1 is not None:
            query_params = {'useFcmV1': 'true' if self.force_fcm_v1 else 'false'}
            url += '?' + urlencode(query_params)

        response = self.session.post(
            url,
            data=json.dumps([pm.get_payload() for pm in push_messages]),
            timeout=self.timeout)

        # Let's validate the response format first.
        try:
            response_data = response.json()
        except ValueError:
            # The response isn't json. First, let's attempt to raise a normal
            # http error. If it's a 200, then we'll raise our own error.
            response.raise_for_status()

            raise PushServerError('Invalid server response', response)

        # If there are errors with the entire request, raise an error now.
        if 'errors' in response_data:
            raise PushServerError('Request failed',
                                  response,
                                  response_data=response_data,
                                  errors=response_data['errors'])

        # We expect the response to have a 'data' field with the responses.
        if 'data' not in response_data:
            raise PushServerError('Invalid server response',
                                  response,
                                  response_data=response_data)

        # Use the requests library's built-in exceptions for any remaining 4xx
        # and 5xx errors.
        response.raise_for_status()

        # Sanity check the response
        expected_data_length = 0
        for push_message in push_messages:
            expected_data_length += len(push_message.to) if isinstance(push_message.to, list) else 1
        # Note : expected_data_length may exceed max_message_count
        if expected_data_length != len(response_data['data']):
            raise PushServerError(
                ('Mismatched response length. Expected %d %s but only '
                 'received %d' %
                 (expected_data_length, 'receipt' if expected_data_length == 1 else
                  'receipts', len(response_data['data']))),
                response,
                response_data=response_data)

        # At this point, we know it's a 200 and the response format is correct.
        # Now let's parse the responses(push_tickets) per push notification.
        push_tickets = []
        for i, push_ticket in enumerate(response_data['data']):
            push_tickets.append(
                PushTicket(
                    push_message=push_messages[i],
                    # If there is no status, assume error.
                    status=push_ticket.get('status', PushTicket.ERROR_STATUS),
                    message=push_ticket.get('message', ''),
                    details=push_ticket.get('details', None),
                    id=push_ticket.get('id', '')))

        return push_tickets

    def publish(self, push_message: PushMessage) -> PushTicket:
        """Sends a single push notification

        Args:
            push_message: A single PushMessage object.

        Returns:
           A PushTicket object which contains the results.
        """
        if isinstance(push_message.to, list) and len(push_message.to) > 1:
            raise ValueError("Sending notification to multiple recipients is not allowed "
                             "with publish method. Use publish_multiple method instead.")
        return self.publish_multiple([push_message])[0]

    def publish_multiple(self, push_messages: List[PushMessage]) -> List[PushTicket]:
        """Sends multiple push notifications at once

        Args:
            push_messages: An array of PushMessage objects.

        Returns:
           An array of PushTicket objects which contains the results.
        """
        push_tickets: List[PushTicket] = []
        for start in itertools.count(0, self.max_message_count):
            # Todo : Check if len(push_message.to) check is required here as well
            # If yes : We will divide the push_message with len(to) > max_message_count
            # into multiple push messages.
            chunk = list(
                itertools.islice(push_messages, start,
                                 start + self.max_message_count))
            if not chunk:
                break
            push_tickets.extend(self._publish_internal(chunk))
        return push_tickets

    def check_receipts_multiple(self, push_tickets: List[PushTicket]) -> List[PushReceipt]:
        """
        Check receipts in batches of 1000 as per expo docs
        """
        receipts: List[PushReceipt] = []
        for start in itertools.count(0, self.max_receipt_count):
            chunk = list(
                itertools.islice(push_tickets, start,
                                 start + self.max_receipt_count))
            if not chunk:
                break
            receipts.extend(self._check_receipts_internal(chunk))
        return receipts

    def _check_receipts_internal(self, push_tickets: List[PushTicket]) -> List[PushReceipt]:
        """
        Helper function for check_receipts_multiple
        """
        response = self.session.post(
            self.host + self.api_url + '/push/getReceipts',
            json={'ids': [push_ticket.id for push_ticket in push_tickets]},
            timeout=self.timeout)

        receipts = self.validate_and_get_receipts(response)
        return receipts

    def check_receipts(self, push_tickets: List[PushTicket]) -> List[PushReceipt]:
        """  Checks the push receipts of the given push tickets """
        response = requests.post(
            self.host + self.api_url + '/push/getReceipts',
            data=json.dumps(
                {'ids': [push_ticket.id for push_ticket in push_tickets]}),
            headers={
                'accept': 'application/json',
                'accept-encoding': 'gzip, deflate',
                'content-type': 'application/json',
            },
            timeout=self.timeout)
        receipts = self.validate_and_get_receipts(response)
        return receipts

    def validate_and_get_receipts(self, response: requests.Response) -> List[PushReceipt]:
        """
        Validate and get receipts for requests
        """
        # Let's validate the response format first.
        try:
            response_data: Dict[str, Any] = response.json()
        except ValueError:
            # The response isn't json. First, let's attempt to raise a normal
            # http error. If it's a 200, then we'll raise our own error.
            response.raise_for_status()
            raise PushServerError('Invalid server response', response)

        # If there are errors with the entire request, raise an error now.
        if 'errors' in response_data:
            raise PushServerError('Request failed',
                                  response,
                                  response_data=response_data,
                                  errors=response_data['errors'])

        # We expect the response to have a 'data' field with the responses.
        if 'data' not in response_data:
            raise PushServerError('Invalid server response',
                                  response,
                                  response_data=response_data)

        # Use the requests library's built-in exceptions for any remaining 4xx
        # and 5xx errors.
        response.raise_for_status()

        # At this point, we know it's a 200 and the response format is correct.
        # Now let's parse the responses per push notification.
        response_data_items: Dict[str, Any] = response_data['data']
        ret: List[PushReceipt] = []
        for r_id, val in response_data_items.items():
            ret.append(
                PushReceipt(
                    status=val.get('status', PushReceipt.ERROR_STATUS),
                    message=val.get('message', ''),
                    details=val.get('details', None),
                    id=r_id
                )
            )
        return ret


# Backward compatibility alias
PushClient = SyncPushClient


class AsyncPushClient:
    """Exponent push client (asynchronous)

    Supports dependency injection of async HTTP clients.
    By default, uses httpx.AsyncClient.

    See full API docs at https://docs.expo.io/versions/latest/guides/push-notifications.html#http2-api
    """
    DEFAULT_HOST = "https://exp.host"
    DEFAULT_BASE_API_URL = "/--/api/v2"
    DEFAULT_MAX_MESSAGE_COUNT = 100
    DEFAULT_MAX_RECEIPT_COUNT = 1000

    def __init__(
        self,
        host: Optional[str] = None,
        api_url: Optional[str] = None,
        http_client: Optional[httpx.AsyncClient] = None,
        force_fcm_v1: Optional[bool] = None,
        **kwargs: Any
    ) -> None:
        """Construct a new AsyncPushClient object.

        Args:
            host: The server protocol, hostname, and port.
            api_url: The api url at the host.
            http_client: Pass in your own httpx.AsyncClient if you prefer
                to customize (dependency injection support)
            force_fcm_v1: If True, send Android notifications via FCM V1, regardless
                of whether a valid credential exists.
        """
        self.host: str = host if host else self.DEFAULT_HOST
        self.api_url: str = api_url if api_url else self.DEFAULT_BASE_API_URL
        self.force_fcm_v1: Optional[bool] = force_fcm_v1

        self.max_message_count: int = kwargs.get('max_message_count', self.DEFAULT_MAX_MESSAGE_COUNT)
        self.max_receipt_count: int = kwargs.get('max_receipt_count', self.DEFAULT_MAX_RECEIPT_COUNT)
        self.timeout: Optional[float] = kwargs.get('timeout', None)

        self._http_client: Optional[httpx.AsyncClient] = http_client
        self._owns_http_client: bool = http_client is None

    async def __aenter__(self) -> 'AsyncPushClient':
        """Async context manager entry."""
        if self._owns_http_client:
            self._http_client = httpx.AsyncClient(
                headers={
                    'accept': 'application/json',
                    'accept-encoding': 'gzip, deflate',
                    'content-type': 'application/json',
                },
                timeout=self.timeout
            )
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Async context manager exit."""
        if self._owns_http_client and self._http_client:
            await self._http_client.aclose()

    @property
    def http_client(self) -> httpx.AsyncClient:
        """Get or create the HTTP client."""
        if self._http_client is None:
            self._http_client = httpx.AsyncClient(
                headers={
                    'accept': 'application/json',
                    'accept-encoding': 'gzip, deflate',
                    'content-type': 'application/json',
                },
                timeout=self.timeout
            )
        return self._http_client

    @classmethod
    def is_exponent_push_token(cls, token: Union[str, List[str]]) -> bool:
        """Returns `True` if the token is an Exponent push token"""
        if isinstance(token, list):
            return all(isinstance(t, str) and t.startswith('ExponentPushToken') for t in token)
        return isinstance(token, str) and token.startswith('ExponentPushToken')

    async def _publish_internal(self, push_messages: List[PushMessage]) -> List[PushTicket]:
        """Send push notifications asynchronously

        The server will validate any type of syntax errors and the client will
        raise the proper exceptions for the user to handle.

        Args:
            push_messages: An array of PushMessage objects.
        """
        url = urljoin(self.host, self.api_url + '/push/send')
        if self.force_fcm_v1 is not None:
            query_params = {'useFcmV1': 'true' if self.force_fcm_v1 else 'false'}
            url += '?' + urlencode(query_params)

        response = await self.http_client.post(
            url,
            content=json.dumps([pm.get_payload() for pm in push_messages]),
            timeout=self.timeout
        )

        # Let's validate the response format first.
        try:
            response_data: Dict[str, Any] = response.json()
        except ValueError:
            # The response isn't json. First, let's attempt to raise a normal
            # http error. If it's a 200, then we'll raise our own error.
            response.raise_for_status()
            raise PushServerError('Invalid server response', response)

        # If there are errors with the entire request, raise an error now.
        if 'errors' in response_data:
            raise PushServerError('Request failed',
                                  response,
                                  response_data=response_data,
                                  errors=response_data['errors'])

        # We expect the response to have a 'data' field with the responses.
        if 'data' not in response_data:
            raise PushServerError('Invalid server response',
                                  response,
                                  response_data=response_data)

        # Use the httpx library's built-in exceptions for any remaining 4xx
        # and 5xx errors.
        response.raise_for_status()

        # Sanity check the response
        expected_data_length = 0
        for push_message in push_messages:
            expected_data_length += len(push_message.to) if isinstance(push_message.to, list) else 1
        # Note : expected_data_length may exceed max_message_count
        if expected_data_length != len(response_data['data']):
            raise PushServerError(
                ('Mismatched response length. Expected %d %s but only '
                 'received %d' %
                 (expected_data_length, 'receipt' if expected_data_length == 1 else
                  'receipts', len(response_data['data']))),
                response,
                response_data=response_data)

        # At this point, we know it's a 200 and the response format is correct.
        # Now let's parse the responses(push_tickets) per push notification.
        push_tickets: List[PushTicket] = []
        for i, push_ticket in enumerate(response_data['data']):
            push_tickets.append(
                PushTicket(
                    push_message=push_messages[i],
                    # If there is no status, assume error.
                    status=push_ticket.get('status', PushTicket.ERROR_STATUS),
                    message=push_ticket.get('message', ''),
                    details=push_ticket.get('details', None),
                    id=push_ticket.get('id', '')))

        return push_tickets

    async def publish(self, push_message: PushMessage) -> PushTicket:
        """Sends a single push notification asynchronously

        Args:
            push_message: A single PushMessage object.

        Returns:
           A PushTicket object which contains the results.
        """
        if isinstance(push_message.to, list) and len(push_message.to) > 1:
            raise ValueError("Sending notification to multiple recipients is not allowed "
                             "with publish method. Use publish_multiple method instead.")
        results = await self.publish_multiple([push_message])
        return results[0]

    async def publish_multiple(self, push_messages: List[PushMessage]) -> List[PushTicket]:
        """Sends multiple push notifications at once asynchronously

        Args:
            push_messages: An array of PushMessage objects.

        Returns:
           An array of PushTicket objects which contains the results.
        """
        push_tickets: List[PushTicket] = []
        for start in itertools.count(0, self.max_message_count):
            chunk = list(
                itertools.islice(push_messages, start,
                                 start + self.max_message_count))
            if not chunk:
                break
            push_tickets.extend(await self._publish_internal(chunk))
        return push_tickets

    async def check_receipts_multiple(self, push_tickets: List[PushTicket]) -> List[PushReceipt]:
        """
        Check receipts in batches of 1000 as per expo docs (asynchronously)
        """
        receipts: List[PushReceipt] = []
        for start in itertools.count(0, self.max_receipt_count):
            chunk = list(
                itertools.islice(push_tickets, start,
                                 start + self.max_receipt_count))
            if not chunk:
                break
            receipts.extend(await self._check_receipts_internal(chunk))
        return receipts

    async def _check_receipts_internal(self, push_tickets: List[PushTicket]) -> List[PushReceipt]:
        """
        Helper function for check_receipts_multiple (asynchronous)
        """
        response = await self.http_client.post(
            self.host + self.api_url + '/push/getReceipts',
            json={'ids': [push_ticket.id for push_ticket in push_tickets]},
            timeout=self.timeout)

        receipts = await self.validate_and_get_receipts(response)
        return receipts

    async def check_receipts(self, push_tickets: List[PushTicket]) -> List[PushReceipt]:
        """Checks the push receipts of the given push tickets (asynchronously)"""
        response = await self.http_client.post(
            self.host + self.api_url + '/push/getReceipts',
            json={'ids': [push_ticket.id for push_ticket in push_tickets]},
            timeout=self.timeout)
        receipts = await self.validate_and_get_receipts(response)
        return receipts

    async def validate_and_get_receipts(self, response: httpx.Response) -> List[PushReceipt]:
        """
        Validate and get receipts for requests (asynchronous)
        """
        # Let's validate the response format first.
        try:
            response_data: Dict[str, Any] = response.json()
        except ValueError:
            # The response isn't json. First, let's attempt to raise a normal
            # http error. If it's a 200, then we'll raise our own error.
            response.raise_for_status()
            raise PushServerError('Invalid server response', response)

        # If there are errors with the entire request, raise an error now.
        if 'errors' in response_data:
            raise PushServerError('Request failed',
                                  response,
                                  response_data=response_data,
                                  errors=response_data['errors'])

        # We expect the response to have a 'data' field with the responses.
        if 'data' not in response_data:
            raise PushServerError('Invalid server response',
                                  response,
                                  response_data=response_data)

        # Use the httpx library's built-in exceptions for any remaining 4xx
        # and 5xx errors.
        response.raise_for_status()

        # At this point, we know it's a 200 and the response format is correct.
        # Now let's parse the responses per push notification.
        response_data_items: Dict[str, Any] = response_data['data']
        ret: List[PushReceipt] = []
        for r_id, val in response_data_items.items():
            ret.append(
                PushReceipt(
                    status=val.get('status', PushReceipt.ERROR_STATUS),
                    message=val.get('message', ''),
                    details=val.get('details', None),
                    id=r_id
                )
            )
        return ret
