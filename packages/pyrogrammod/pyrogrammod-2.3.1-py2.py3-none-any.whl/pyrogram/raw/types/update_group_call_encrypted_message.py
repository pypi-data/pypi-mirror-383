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


class UpdateGroupCallEncryptedMessage(TLObject):  # type: ignore
    """

    Constructor of :obj:`~pyrogram.raw.base.Update`.

    Details:
        - Layer: ``216``
        - ID: ``C957A766``

    Parameters:
        call (:obj:`InputGroupCall <pyrogram.raw.base.InputGroupCall>`):
            N/A

        from_id (:obj:`Peer <pyrogram.raw.base.Peer>`):
            N/A

        encrypted_message (``bytes``):
            N/A

    """

    __slots__: List[str] = ["call", "from_id", "encrypted_message"]

    ID = 0xc957a766
    QUALNAME = "types.UpdateGroupCallEncryptedMessage"

    def __init__(self, *, call: "raw.base.InputGroupCall", from_id: "raw.base.Peer", encrypted_message: bytes) -> None:
        self.call = call  # InputGroupCall
        self.from_id = from_id  # Peer
        self.encrypted_message = encrypted_message  # bytes

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "UpdateGroupCallEncryptedMessage":
        # No flags
        
        call = TLObject.read(b)
        
        from_id = TLObject.read(b)
        
        encrypted_message = Bytes.read(b)
        
        return UpdateGroupCallEncryptedMessage(call=call, from_id=from_id, encrypted_message=encrypted_message)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        # No flags
        
        b.write(self.call.write())
        
        b.write(self.from_id.write())
        
        b.write(Bytes(self.encrypted_message))
        
        return b.getvalue()
