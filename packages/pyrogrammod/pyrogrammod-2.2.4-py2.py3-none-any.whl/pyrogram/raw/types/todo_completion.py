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


class TodoCompletion(TLObject):  # type: ignore
    """A completed todo list » item.

    Constructor of :obj:`~pyrogram.raw.base.TodoCompletion`.

    Details:
        - Layer: ``216``
        - ID: ``4CC120B7``

    Parameters:
        id (``int`` ``32-bit``):
            The ID of the completed item.

        completed_by (``int`` ``64-bit``):
            ID of the user that completed the item.

        date (``int`` ``32-bit``):
            When was the item completed.

    """

    __slots__: List[str] = ["id", "completed_by", "date"]

    ID = 0x4cc120b7
    QUALNAME = "types.TodoCompletion"

    def __init__(self, *, id: int, completed_by: int, date: int) -> None:
        self.id = id  # int
        self.completed_by = completed_by  # long
        self.date = date  # int

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "TodoCompletion":
        # No flags
        
        id = Int.read(b)
        
        completed_by = Long.read(b)
        
        date = Int.read(b)
        
        return TodoCompletion(id=id, completed_by=completed_by, date=date)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        # No flags
        
        b.write(Int(self.id))
        
        b.write(Long(self.completed_by))
        
        b.write(Int(self.date))
        
        return b.getvalue()
