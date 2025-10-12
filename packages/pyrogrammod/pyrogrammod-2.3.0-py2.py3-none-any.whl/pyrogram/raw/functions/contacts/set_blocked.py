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


class SetBlocked(TLObject):  # type: ignore
    """Replace the contents of an entire blocklist, see here for more info ».


    Details:
        - Layer: ``216``
        - ID: ``94C65C76``

    Parameters:
        id (List of :obj:`InputPeer <pyrogram.raw.base.InputPeer>`):
            Full content of the blocklist.

        limit (``int`` ``32-bit``):
            Maximum number of results to return, see pagination

        my_stories_from (``bool``, *optional*):
            Whether to edit the story blocklist; if not set, will edit the main blocklist. See here » for differences between the two.

    Returns:
        ``bool``
    """

    __slots__: List[str] = ["id", "limit", "my_stories_from"]

    ID = 0x94c65c76
    QUALNAME = "functions.contacts.SetBlocked"

    def __init__(self, *, id: List["raw.base.InputPeer"], limit: int, my_stories_from: Optional[bool] = None) -> None:
        self.id = id  # Vector<InputPeer>
        self.limit = limit  # int
        self.my_stories_from = my_stories_from  # flags.0?true

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "SetBlocked":
        
        flags = Int.read(b)
        
        my_stories_from = True if flags & (1 << 0) else False
        id = TLObject.read(b)
        
        limit = Int.read(b)
        
        return SetBlocked(id=id, limit=limit, my_stories_from=my_stories_from)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        flags = 0
        flags |= (1 << 0) if self.my_stories_from else 0
        b.write(Int(flags))
        
        b.write(Vector(self.id))
        
        b.write(Int(self.limit))
        
        return b.getvalue()
