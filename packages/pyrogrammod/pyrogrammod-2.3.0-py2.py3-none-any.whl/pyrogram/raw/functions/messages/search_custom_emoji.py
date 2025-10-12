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


class SearchCustomEmoji(TLObject):  # type: ignore
    """Look for custom emojis associated to a UTF8 emoji


    Details:
        - Layer: ``216``
        - ID: ``2C11C0D7``

    Parameters:
        emoticon (``str``):
            The emoji

        hash (``int`` ``64-bit``):
            Hash used for caching, for more info click here.

    Returns:
        :obj:`EmojiList <pyrogram.raw.base.EmojiList>`
    """

    __slots__: List[str] = ["emoticon", "hash"]

    ID = 0x2c11c0d7
    QUALNAME = "functions.messages.SearchCustomEmoji"

    def __init__(self, *, emoticon: str, hash: int) -> None:
        self.emoticon = emoticon  # string
        self.hash = hash  # long

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "SearchCustomEmoji":
        # No flags
        
        emoticon = String.read(b)
        
        hash = Long.read(b)
        
        return SearchCustomEmoji(emoticon=emoticon, hash=hash)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        # No flags
        
        b.write(String(self.emoticon))
        
        b.write(Long(self.hash))
        
        return b.getvalue()
