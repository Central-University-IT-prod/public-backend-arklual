"""Mocked bot."""
from collections import deque
from datetime import datetime
from typing import TYPE_CHECKING

from aiogram import Bot
from aiogram.client.session.base import BaseSession
from aiogram.methods import TelegramMethod
from aiogram.methods.base import Request, Response, TelegramType
from aiogram.types import ResponseParameters, User, Chat
from aiogram.types.base import UNSET_PARSE_MODE


class MockedSession(BaseSession):
    """Mocked session for tests."""

    def __init__(self):
        """Mocked session is used for offline integration tests."""
        super().__init__()
        self.responses: deque[Response[TelegramType]] = deque()
        self.requests: deque[Request] = deque()
        self.closed = True

    def add_result(
            self, response: Response[TelegramType]
    ) -> Response[TelegramType]:
        """Mocked method for add result.

        :param response: Response to add
        :return: this Response.
        """
        self.responses.append(response)
        return response

    def get_request(self) -> Request:
        """Mocked method for get request.

        :return: Request.
        """
        return self.requests.pop()

    async def close(self):
        """Mocked method for closing the session.

        :return: Nothing.
        """
        self.closed = True

    async def make_request(
            self,
            bot: Bot,
            method: TelegramMethod[TelegramType],
            timeout=UNSET_PARSE_MODE,
    ) -> TelegramType:
        '''self.closed = False
        self.requests.append(method)
        response: Response[TelegramType] = self.responses.pop()
        self.check_response(
            bot=bot,
            method=method,
            status_code=response.error_code,
            content=response.model_dump_json(),
        )
        return response.result  # type: ignore'''
        return method

    async def stream_content(
            self,
            url: str,
            headers=None,
            timeout: int = 30,
            chunk_size: int = 65536,
            raise_for_status: bool = True,
    ):
        """Just mocked and shutted down method."""
        b''


class MockedBot(Bot):
    """Mocked bot for tests."""

    if TYPE_CHECKING:
        session: MockedSession

    def __init__(self, **kwargs):
        """Mocked session init."""
        super().__init__(
            kwargs.pop('token', '42:TEST'), session=MockedSession(), **kwargs
        )
        self._me = User(
            id=self.id,
            is_bot=True,
            first_name='FirstName',
            last_name='LastName',
            username='tbot',
            language_code='uk-UA',
        )

    def add_result_for(
            self,
            method: type[TelegramMethod[TelegramType]],
            ok: bool,
            result: TelegramType = None,
            description: str | None = None,
            error_code: int = 200,
            migrate_to_chat_id: int | None = None,
            retry_after: int | None = None,
    ) -> Response[TelegramType]:
        """The mocked add_result_for function adds a result to the session.

        :param self: Access the class instance
        :param method: Get the return type of the method
        :param ok: Indicate whether the request was successful or not
        :param result: Define the type of the result
        :param description: Provide a description of the result
        :param error_code: Indicate that the request was successful
        :param migrate_to_chat_id: Migrate to chat update
        :param retry_after: Specify the time to wait before a request can be repeated
        :return: A response object, which is a subclass of namedtuple
        :doc-author: Trelent.
        """
        response = Response[method.__returning__](  # type: ignore
            ok=ok,
            result=result,
            description=description,
            error_code=error_code,
            parameters=ResponseParameters(
                migrate_to_chat_id=migrate_to_chat_id,
                retry_after=retry_after,
            ),
        )
        self.session.add_result(response)
        return response

    def get_request(self) -> Request:
        """Get last request.

        The get_request function returns a Request object that has been created
        by the Session object. The get_request function is called when the user
        wants to make a request to an endpoint.

        :param self: Access the class attributes and methods
        :return: A request object
        :doc-author: Trelent.
        """
        return self.session.get_request()


TEST_USER = User(
    id=123,
    is_bot=False,
    first_name='Test',
    last_name='Bot',
    username='testbot',
    language_code='ru-RU',
    is_premium=True,
    added_to_attachment_menu=None,
    can_join_groups=None,
    can_read_all_group_messages=None,
    supports_inline_queries=None,
)

TEST_CHAT = Chat(
    id=12,
    type='private',
    title=None,
    username=TEST_USER.username,
    first_name=TEST_USER.first_name,
    last_name=TEST_USER.last_name,
    photo=None,
    bio=None,
    has_private_forwards=None,
    join_to_send_messages=None,
    join_by_request=None,
    description=None,
    invite_link=None,
    pinned_message=None,
    permissions=None,
    slow_mode_delay=None,
    message_auto_delete_time=None,
    has_protected_content=None,
    sticker_set_name=None,
    can_set_sticker_set=None,
    linked_chat_id=None,
    location=None,
)
from aiogram.filters.callback_data import CallbackData
from aiogram.types import CallbackQuery, Message, Update

TEST_MESSAGE = Message(message_id=123, date=datetime.now(), chat=TEST_CHAT)


def get_message(text: str, chat=TEST_CHAT, from_user=TEST_USER, **kwargs):
    """Get message update for tests."""
    return Message(
        message_id=123,
        date=datetime.now(),
        chat=chat,
        from_user=from_user,
        sender_chat=TEST_CHAT,
        text=text,
        **kwargs
    )


def get_chat(
        chat_id: int = None,
        chat_type: str = 'private',
        title: str = 'TEST_TITLE',
        username: str = TEST_CHAT.username,
        **kwargs
) -> Chat:
    """Get chat object for tests."""
    return Chat(
        id=chat_id,
        type=chat_type,
        title=title,
        username=username,
        first_name=TEST_USER.first_name,
        last_name=TEST_USER.last_name,
        **kwargs
    )


def get_callback_query(
        data: str | CallbackData, from_user=TEST_USER, message=None, **kwargs
):
    """Get callback query update for tests."""
    return CallbackQuery(
        id='test',
        from_user=from_user,
        chat_instance='test',
        message=message or TEST_MESSAGE,
        data=data,
        **kwargs
    )


def get_update(
        message: Message = None, callback_query: CallbackQuery = None, **kwargs
):
    """Get mocked update for tests."""
    return Update(
        update_id=187,
        message=message,
        callback_query=callback_query or None,
        **kwargs
    )
