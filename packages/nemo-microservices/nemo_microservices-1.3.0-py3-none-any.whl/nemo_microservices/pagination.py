# SPDX-FileCopyrightText: Copyright (c) 2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Generic, TypeVar, Optional, cast
from typing_extensions import override

from ._models import BaseModel
from ._base_client import BasePage, PageInfo, BaseSyncPage, BaseAsyncPage

__all__ = [
    "DefaultPaginationPagination",
    "SyncDefaultPagination",
    "AsyncDefaultPagination",
    "SyncLogsPagination",
    "AsyncLogsPagination",
]

_T = TypeVar("_T")


class DefaultPaginationPagination(BaseModel):
    current_page_size: Optional[int] = None
    """The size for the current page."""

    page: Optional[int] = None
    """The current page number."""

    page_size: Optional[int] = None
    """The page size used for the query."""

    total_pages: Optional[int] = None
    """The total number of pages."""

    total_results: Optional[int] = None
    """The total number of results."""


class SyncDefaultPagination(BaseSyncPage[_T], BasePage[_T], Generic[_T]):
    object: Optional[str] = None
    data: List[_T]
    sort: Optional[str] = None
    pagination: Optional[DefaultPaginationPagination] = None

    @override
    def _get_page_items(self) -> List[_T]:
        data = self.data
        if not data:
            return []
        return data

    @override
    def next_page_info(self) -> Optional[PageInfo]:
        last_page = cast("int | None", self._options.params.get("page")) or 1

        return PageInfo(params={"page": last_page + 1})


class AsyncDefaultPagination(BaseAsyncPage[_T], BasePage[_T], Generic[_T]):
    object: Optional[str] = None
    data: List[_T]
    sort: Optional[str] = None
    pagination: Optional[DefaultPaginationPagination] = None

    @override
    def _get_page_items(self) -> List[_T]:
        data = self.data
        if not data:
            return []
        return data

    @override
    def next_page_info(self) -> Optional[PageInfo]:
        last_page = cast("int | None", self._options.params.get("page")) or 1

        return PageInfo(params={"page": last_page + 1})


class SyncLogsPagination(BaseSyncPage[_T], BasePage[_T], Generic[_T]):
    object: Optional[str] = None
    data: List[_T]
    next_page: Optional[str] = None

    @override
    def _get_page_items(self) -> List[_T]:
        data = self.data
        if not data:
            return []
        return data

    @override
    def next_page_info(self) -> Optional[PageInfo]:
        next_page = self.next_page
        if not next_page:
            return None

        return PageInfo(params={"page_cursor": next_page})


class AsyncLogsPagination(BaseAsyncPage[_T], BasePage[_T], Generic[_T]):
    object: Optional[str] = None
    data: List[_T]
    next_page: Optional[str] = None

    @override
    def _get_page_items(self) -> List[_T]:
        data = self.data
        if not data:
            return []
        return data

    @override
    def next_page_info(self) -> Optional[PageInfo]:
        next_page = self.next_page
        if not next_page:
            return None

        return PageInfo(params={"page_cursor": next_page})
