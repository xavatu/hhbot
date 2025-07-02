import collections.abc
from typing import (
    Iterable,
    AsyncIterator,
    TypeVar,
    Callable,
    Tuple,
    Optional,
    Awaitable,
    Any,
)

ReturnType = TypeVar("ReturnType")
ResponseType = TypeVar("ResponseType")

__all__ = ["AsyncList", "AsyncPageIterator", "AsyncItemPaged", "async_chunks"]


class AsyncList(AsyncIterator[ReturnType]):
    def __init__(self, iterable: Iterable[ReturnType]) -> None:
        self._iterator = iter(iterable)

    async def __anext__(self) -> ReturnType:
        try:
            return next(self._iterator)
        except StopIteration as err:
            raise StopAsyncIteration() from err


class AsyncPageIterator(AsyncIterator[AsyncIterator[ReturnType]]):
    def __init__(
        self,
        get_next: Callable[[Optional[str]], Awaitable[ResponseType]],
        extract_data: Callable[
            [ResponseType], Awaitable[Tuple[str, AsyncIterator[ReturnType]]]
        ],
        continuation_token: Optional[str] = None,
    ) -> None:
        self._get_next = get_next
        self._extract_data = extract_data
        self.continuation_token = continuation_token
        self._did_a_call_already = False
        self._response: Optional[ResponseType] = None
        self._current_page: Optional[AsyncIterator[ReturnType]] = None

    async def __anext__(self) -> AsyncIterator[ReturnType]:
        if self.continuation_token is None and self._did_a_call_already:
            raise StopAsyncIteration("End of paging")
        try:
            self._response = await self._get_next(self.continuation_token)
        except Exception as e:
            raise e

        self._did_a_call_already = True

        self.continuation_token, self._current_page = await self._extract_data(
            self._response
        )

        if isinstance(self._current_page, collections.abc.Iterable):
            self._current_page = AsyncList(self._current_page)

        return self._current_page


class AsyncItemPaged(AsyncIterator[ReturnType]):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self._args = args
        self._kwargs = kwargs
        self._page_iterator: Optional[
            AsyncIterator[AsyncIterator[ReturnType]]
        ] = None
        self._page: Optional[AsyncIterator[ReturnType]] = None
        self._page_iterator_class = self._kwargs.pop(
            "page_iterator_class", AsyncPageIterator
        )

    def by_page(
        self,
        continuation_token: Optional[str] = None,
    ) -> AsyncIterator[AsyncIterator[ReturnType]]:
        return self._page_iterator_class(
            *self._args, **self._kwargs, continuation_token=continuation_token
        )

    async def __anext__(self) -> ReturnType:
        if self._page_iterator is None:
            self._page_iterator = self.by_page()
            return await self.__anext__()
        if self._page is None:
            self._page = await self._page_iterator.__anext__()
            return await self.__anext__()
        try:
            return await self._page.__anext__()
        except StopAsyncIteration:
            self._page = None
            return await self.__anext__()


async def async_chunks(
    async_iterator: AsyncIterator[ReturnType],
    size: int,
) -> AsyncIterator[list[ReturnType]]:
    finished = False

    while not finished:
        chunk: list[ReturnType] = []

        for _ in range(size):
            try:
                result = await anext(async_iterator)
            except StopAsyncIteration:
                finished = True
            else:
                chunk.append(result)

        if chunk:
            yield chunk
