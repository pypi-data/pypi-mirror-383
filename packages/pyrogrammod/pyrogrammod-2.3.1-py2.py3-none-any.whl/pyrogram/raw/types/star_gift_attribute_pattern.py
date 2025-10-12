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


class StarGiftAttributePattern(TLObject):  # type: ignore
    """A sticker applied on the backdrop of a collectible gift » using a repeating pattern.

    Constructor of :obj:`~pyrogram.raw.base.StarGiftAttribute`.

    Details:
        - Layer: ``216``
        - ID: ``13ACFF19``

    Parameters:
        name (``str``):
            Name of the symbol

        document (:obj:`Document <pyrogram.raw.base.Document>`):
            The symbol

        rarity_permille (``int`` ``32-bit``):
            The number of upgraded gifts that receive this backdrop for each 1000 gifts upgraded.

    """

    __slots__: List[str] = ["name", "document", "rarity_permille"]

    ID = 0x13acff19
    QUALNAME = "types.StarGiftAttributePattern"

    def __init__(self, *, name: str, document: "raw.base.Document", rarity_permille: int) -> None:
        self.name = name  # string
        self.document = document  # Document
        self.rarity_permille = rarity_permille  # int

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "StarGiftAttributePattern":
        # No flags
        
        name = String.read(b)
        
        document = TLObject.read(b)
        
        rarity_permille = Int.read(b)
        
        return StarGiftAttributePattern(name=name, document=document, rarity_permille=rarity_permille)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        # No flags
        
        b.write(String(self.name))
        
        b.write(self.document.write())
        
        b.write(Int(self.rarity_permille))
        
        return b.getvalue()
