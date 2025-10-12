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


class SearchPosts(TLObject):  # type: ignore
    """Globally search for posts from public channels » (including those we aren't a member of) containing either a specific hashtag, or a full text query.


    Details:
        - Layer: ``216``
        - ID: ``F2C4F24D``

    Parameters:
        offset_rate (``int`` ``32-bit``):
            Initially 0, then set to the next_rate parameter of messages.messagesSlice, or if that is absent, the date of the last returned message.

        offset_peer (:obj:`InputPeer <pyrogram.raw.base.InputPeer>`):
            Offsets for pagination, for more info click here

        offset_id (``int`` ``32-bit``):
            Offsets for pagination, for more info click here

        limit (``int`` ``32-bit``):
            Maximum number of results to return, see pagination

        hashtag (``str``, *optional*):
            The hashtag to search, without the # character.

        query (``str``, *optional*):
            The full text query: each user has a limited amount of free full text search slots, after which payment is required, see here » for more info on the full flow.

        allow_paid_stars (``int`` ``64-bit``, *optional*):
            For full text post searches (query), allows payment of the specified amount of Stars for the search, see here » for more info on the full flow.

    Returns:
        :obj:`messages.Messages <pyrogram.raw.base.messages.Messages>`
    """

    __slots__: List[str] = ["offset_rate", "offset_peer", "offset_id", "limit", "hashtag", "query", "allow_paid_stars"]

    ID = 0xf2c4f24d
    QUALNAME = "functions.channels.SearchPosts"

    def __init__(self, *, offset_rate: int, offset_peer: "raw.base.InputPeer", offset_id: int, limit: int, hashtag: Optional[str] = None, query: Optional[str] = None, allow_paid_stars: Optional[int] = None) -> None:
        self.offset_rate = offset_rate  # int
        self.offset_peer = offset_peer  # InputPeer
        self.offset_id = offset_id  # int
        self.limit = limit  # int
        self.hashtag = hashtag  # flags.0?string
        self.query = query  # flags.1?string
        self.allow_paid_stars = allow_paid_stars  # flags.2?long

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "SearchPosts":
        
        flags = Int.read(b)
        
        hashtag = String.read(b) if flags & (1 << 0) else None
        query = String.read(b) if flags & (1 << 1) else None
        offset_rate = Int.read(b)
        
        offset_peer = TLObject.read(b)
        
        offset_id = Int.read(b)
        
        limit = Int.read(b)
        
        allow_paid_stars = Long.read(b) if flags & (1 << 2) else None
        return SearchPosts(offset_rate=offset_rate, offset_peer=offset_peer, offset_id=offset_id, limit=limit, hashtag=hashtag, query=query, allow_paid_stars=allow_paid_stars)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        flags = 0
        flags |= (1 << 0) if self.hashtag is not None else 0
        flags |= (1 << 1) if self.query is not None else 0
        flags |= (1 << 2) if self.allow_paid_stars is not None else 0
        b.write(Int(flags))
        
        if self.hashtag is not None:
            b.write(String(self.hashtag))
        
        if self.query is not None:
            b.write(String(self.query))
        
        b.write(Int(self.offset_rate))
        
        b.write(self.offset_peer.write())
        
        b.write(Int(self.offset_id))
        
        b.write(Int(self.limit))
        
        if self.allow_paid_stars is not None:
            b.write(Long(self.allow_paid_stars))
        
        return b.getvalue()
