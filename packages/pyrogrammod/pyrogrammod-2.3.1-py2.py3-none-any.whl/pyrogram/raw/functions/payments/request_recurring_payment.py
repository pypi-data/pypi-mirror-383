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


class RequestRecurringPayment(TLObject):  # type: ignore
    """{schema}


    Details:
        - Layer: ``216``
        - ID: ``146E958D``

    Parameters:
        user_id (:obj:`InputUser <pyrogram.raw.base.InputUser>`):
            

        recurring_init_charge (``str``):
            

        invoice_media (:obj:`InputMedia <pyrogram.raw.base.InputMedia>`):
            

    Returns:
        :obj:`Updates <pyrogram.raw.base.Updates>`
    """

    __slots__: List[str] = ["user_id", "recurring_init_charge", "invoice_media"]

    ID = 0x146e958d
    QUALNAME = "functions.payments.RequestRecurringPayment"

    def __init__(self, *, user_id: "raw.base.InputUser", recurring_init_charge: str, invoice_media: "raw.base.InputMedia") -> None:
        self.user_id = user_id  # InputUser
        self.recurring_init_charge = recurring_init_charge  # string
        self.invoice_media = invoice_media  # InputMedia

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "RequestRecurringPayment":
        # No flags
        
        user_id = TLObject.read(b)
        
        recurring_init_charge = String.read(b)
        
        invoice_media = TLObject.read(b)
        
        return RequestRecurringPayment(user_id=user_id, recurring_init_charge=recurring_init_charge, invoice_media=invoice_media)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        # No flags
        
        b.write(self.user_id.write())
        
        b.write(String(self.recurring_init_charge))
        
        b.write(self.invoice_media.write())
        
        return b.getvalue()
