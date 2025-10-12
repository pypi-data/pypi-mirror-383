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


class UpdateBotSubscriptionExpire(TLObject):  # type: ignore
    """

    Constructor of :obj:`~pyrogram.raw.base.Update`.

    Details:
        - Layer: ``216``
        - ID: ``A8AE3EB1``

    Parameters:
        user_id (``int`` ``64-bit``):
            N/A

        payload (``str``):
            N/A

        until_date (``int`` ``32-bit``):
            N/A

        qts (``int`` ``32-bit``):
            N/A

    """

    __slots__: List[str] = ["user_id", "payload", "until_date", "qts"]

    ID = 0xa8ae3eb1
    QUALNAME = "types.UpdateBotSubscriptionExpire"

    def __init__(self, *, user_id: int, payload: str, until_date: int, qts: int) -> None:
        self.user_id = user_id  # long
        self.payload = payload  # string
        self.until_date = until_date  # int
        self.qts = qts  # int

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "UpdateBotSubscriptionExpire":
        # No flags
        
        user_id = Long.read(b)
        
        payload = String.read(b)
        
        until_date = Int.read(b)
        
        qts = Int.read(b)
        
        return UpdateBotSubscriptionExpire(user_id=user_id, payload=payload, until_date=until_date, qts=qts)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        # No flags
        
        b.write(Long(self.user_id))
        
        b.write(String(self.payload))
        
        b.write(Int(self.until_date))
        
        b.write(Int(self.qts))
        
        return b.getvalue()
