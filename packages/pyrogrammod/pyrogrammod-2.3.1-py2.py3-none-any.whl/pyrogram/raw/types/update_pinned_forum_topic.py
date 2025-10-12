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


class UpdatePinnedForumTopic(TLObject):  # type: ignore
    """

    Constructor of :obj:`~pyrogram.raw.base.Update`.

    Details:
        - Layer: ``216``
        - ID: ``683B2C52``

    Parameters:
        peer (:obj:`Peer <pyrogram.raw.base.Peer>`):
            N/A

        topic_id (``int`` ``32-bit``):
            N/A

        pinned (``int`` ``32-bit``, *optional*):
            N/A

    """

    __slots__: List[str] = ["peer", "topic_id", "pinned"]

    ID = 0x683b2c52
    QUALNAME = "types.UpdatePinnedForumTopic"

    def __init__(self, *, peer: "raw.base.Peer", topic_id: int, pinned: Optional[int] = None) -> None:
        self.peer = peer  # Peer
        self.topic_id = topic_id  # int
        self.pinned = pinned  # flags.0?int

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "UpdatePinnedForumTopic":
        
        flags = Int.read(b)
        
        pinned = Int.read(b) if flags & (1 << 0) else None
        peer = TLObject.read(b)
        
        topic_id = Int.read(b)
        
        return UpdatePinnedForumTopic(peer=peer, topic_id=topic_id, pinned=pinned)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        flags = 0
        flags |= (1 << 0) if self.pinned is not None else 0
        b.write(Int(flags))
        
        if self.pinned is not None:
            b.write(Int(self.pinned))
        
        b.write(self.peer.write())
        
        b.write(Int(self.topic_id))
        
        return b.getvalue()
