#  Pyrogram - Telegram MTProto API Client Library for Python
#  Copyright (C) 2017-present Dan <https://github.com/delivrance>
#
#  This file is part of Pyrogram.
#
#  Pyrogram is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Lesser General Public License as published
#  by the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  Pyrogram is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Lesser General Public License for more details.
#
#  You should have received a copy of the GNU Lesser General Public License
#  along with Pyrogram.  If not, see <http://www.gnu.org/licenses/>.

from io import BytesIO

from pyrogram.raw.core.primitives import Int, Long, Int128, Int256, Bool, Bytes, String, Double, Vector
from pyrogram.raw.core import TLObject
from pyrogram import raw
from typing import List, Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


class SearchResultsPositions(TLObject):  # type: ignore
    """Information about sparse positions of messages

    Constructor of :obj:`~pyrogram.raw.base.messages.SearchResultsPositions`.

    Details:
        - Layer: ``216``
        - ID: ``53B22BAF``

    Parameters:
        count (``int`` ``32-bit``):
            Total number of found messages

        positions (List of :obj:`SearchResultsPosition <pyrogram.raw.base.SearchResultsPosition>`):
            List of message positions

    Functions:
        This object can be returned by 1 function.

        .. currentmodule:: pyrogram.raw.functions

        .. autosummary::
            :nosignatures:

            messages.GetSearchResultsPositions
    """

    __slots__: List[str] = ["count", "positions"]

    ID = 0x53b22baf
    QUALNAME = "types.messages.SearchResultsPositions"

    def __init__(self, *, count: int, positions: List["raw.base.SearchResultsPosition"]) -> None:
        self.count = count  # int
        self.positions = positions  # Vector<SearchResultsPosition>

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "SearchResultsPositions":
        # No flags
        
        count = Int.read(b)
        
        positions = TLObject.read(b)
        
        return SearchResultsPositions(count=count, positions=positions)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        # No flags
        
        b.write(Int(self.count))
        
        b.write(Vector(self.positions))
        
        return b.getvalue()
