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


class ReorderPinnedForumTopics(TLObject):  # type: ignore
    """


    Details:
        - Layer: ``216``
        - ID: ``E7841F0``

    Parameters:
        peer (:obj:`InputPeer <pyrogram.raw.base.InputPeer>`):
            N/A

        order (List of ``int`` ``32-bit``):
            N/A

        force (``int`` ``32-bit``, *optional*):
            N/A

    Returns:
        :obj:`Updates <pyrogram.raw.base.Updates>`
    """

    __slots__: List[str] = ["peer", "order", "force"]

    ID = 0xe7841f0
    QUALNAME = "functions.messages.ReorderPinnedForumTopics"

    def __init__(self, *, peer: "raw.base.InputPeer", order: List[int], force: Optional[int] = None) -> None:
        self.peer = peer  # InputPeer
        self.order = order  # Vector<int>
        self.force = force  # flags.0?int

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "ReorderPinnedForumTopics":
        
        flags = Int.read(b)
        
        force = Int.read(b) if flags & (1 << 0) else None
        peer = TLObject.read(b)
        
        order = TLObject.read(b, Int)
        
        return ReorderPinnedForumTopics(peer=peer, order=order, force=force)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        flags = 0
        flags |= (1 << 0) if self.force is not None else 0
        b.write(Int(flags))
        
        if self.force is not None:
            b.write(Int(self.force))
        
        b.write(self.peer.write())
        
        b.write(Vector(self.order, Int))
        
        return b.getvalue()
