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


class GetSavedMusicByID(TLObject):  # type: ignore
    """Check if the passed songs are still pinned to the user's profile, or refresh the file references of songs pinned on a user's profile see here » for more info.


    Details:
        - Layer: ``216``
        - ID: ``7573A4E9``

    Parameters:
        id (:obj:`InputUser <pyrogram.raw.base.InputUser>`):
            The ID of the user.

        documents (List of :obj:`InputDocument <pyrogram.raw.base.InputDocument>`):
            The songs (here, file_reference can be empty to refresh file references).

    Returns:
        :obj:`users.SavedMusic <pyrogram.raw.base.users.SavedMusic>`
    """

    __slots__: List[str] = ["id", "documents"]

    ID = 0x7573a4e9
    QUALNAME = "functions.users.GetSavedMusicByID"

    def __init__(self, *, id: "raw.base.InputUser", documents: List["raw.base.InputDocument"]) -> None:
        self.id = id  # InputUser
        self.documents = documents  # Vector<InputDocument>

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "GetSavedMusicByID":
        # No flags
        
        id = TLObject.read(b)
        
        documents = TLObject.read(b)
        
        return GetSavedMusicByID(id=id, documents=documents)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        # No flags
        
        b.write(self.id.write())
        
        b.write(Vector(self.documents))
        
        return b.getvalue()
