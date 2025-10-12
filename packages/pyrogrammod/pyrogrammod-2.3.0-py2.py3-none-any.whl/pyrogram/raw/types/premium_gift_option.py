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


class PremiumGiftOption(TLObject):  # type: ignore
    """Telegram Premium gift option

    Constructor of :obj:`~pyrogram.raw.base.PremiumGiftOption`.

    Details:
        - Layer: ``216``
        - ID: ``79C059F7``

    Parameters:
        months (``int`` ``32-bit``):
            N/A

        currency (``str``):
            N/A

        amount (``int`` ``64-bit``):
            N/A

        bot_url (``str``, *optional*):
            N/A

        store_product (``str``, *optional*):
            N/A

    """

    __slots__: List[str] = ["months", "currency", "amount", "bot_url", "store_product"]

    ID = 0x79c059f7
    QUALNAME = "types.PremiumGiftOption"

    def __init__(self, *, months: int, currency: str, amount: int, bot_url: Optional[str] = None, store_product: Optional[str] = None) -> None:
        self.months = months  # int
        self.currency = currency  # string
        self.amount = amount  # long
        self.bot_url = bot_url  # flags.1?string
        self.store_product = store_product  # flags.0?string

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "PremiumGiftOption":
        
        flags = Int.read(b)
        
        months = Int.read(b)
        
        currency = String.read(b)
        
        amount = Long.read(b)
        
        bot_url = String.read(b) if flags & (1 << 1) else None
        store_product = String.read(b) if flags & (1 << 0) else None
        return PremiumGiftOption(months=months, currency=currency, amount=amount, bot_url=bot_url, store_product=store_product)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        flags = 0
        flags |= (1 << 1) if self.bot_url is not None else 0
        flags |= (1 << 0) if self.store_product is not None else 0
        b.write(Int(flags))
        
        b.write(Int(self.months))
        
        b.write(String(self.currency))
        
        b.write(Long(self.amount))
        
        if self.bot_url is not None:
            b.write(String(self.bot_url))
        
        if self.store_product is not None:
            b.write(String(self.store_product))
        
        return b.getvalue()
