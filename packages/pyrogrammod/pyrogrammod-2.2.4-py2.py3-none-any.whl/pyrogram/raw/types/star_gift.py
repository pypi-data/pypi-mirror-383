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


class StarGift(TLObject):  # type: ignore
    """Represents a star gift, see here » for more info.

    Constructor of :obj:`~pyrogram.raw.base.StarGift`.

    Details:
        - Layer: ``216``
        - ID: ``80AC53C3``

    Parameters:
        id (``int`` ``64-bit``):
            Identifier of the gift

        sticker (:obj:`Document <pyrogram.raw.base.Document>`):
            Sticker that represents the gift.

        stars (``int`` ``64-bit``):
            Price of the gift in Telegram Stars.

        convert_stars (``int`` ``64-bit``):
            The receiver of this gift may convert it to this many Telegram Stars, instead of displaying it on their profile page.convert_stars will be equal to stars only if the gift was bought using recently bought Telegram Stars, otherwise it will be less than stars.

        limited (``bool``, *optional*):
            Whether this is a limited-supply gift.

        sold_out (``bool``, *optional*):
            Whether this gift sold out and cannot be bought anymore.

        birthday (``bool``, *optional*):
            Whether this is a birthday-themed gift

        can_upgrade (``bool``, *optional*):
            N/A

        require_premium (``bool``, *optional*):
            This gift can only be bought by users with a Premium subscription.

        limited_per_user (``bool``, *optional*):
            If set, the maximum number of gifts of this type that can be owned by a single user is limited and specified in per_user_total, and the remaining slots for the current user in per_user_remains.

        peer_color_available (``bool``, *optional*):
            N/A

        availability_remains (``int`` ``32-bit``, *optional*):
            For limited-supply gifts: the remaining number of gifts that may be bought.

        availability_total (``int`` ``32-bit``, *optional*):
            For limited-supply gifts: the total number of gifts that was available in the initial supply.

        availability_resale (``int`` ``64-bit``, *optional*):
            The total number of (upgraded to collectibles) gifts of this type currently on resale

        first_sale_date (``int`` ``32-bit``, *optional*):
            For sold out gifts only: when was the gift first bought.

        last_sale_date (``int`` ``32-bit``, *optional*):
            For sold out gifts only: when was the gift last bought.

        upgrade_stars (``int`` ``64-bit``, *optional*):
            The number of Telegram Stars the user can pay to convert the gift into a collectible gift ».

        resell_min_stars (``int`` ``64-bit``, *optional*):
            The minimum price in Stars for gifts of this type currently on resale.

        title (``str``, *optional*):
            Title of the gift

        released_by (:obj:`Peer <pyrogram.raw.base.Peer>`, *optional*):
            This gift was released by the specified peer.

        per_user_total (``int`` ``32-bit``, *optional*):
            Maximum number of gifts of this type that can be owned by any user.

        per_user_remains (``int`` ``32-bit``, *optional*):
            Remaining number of gifts of this type that can be owned by the current user.

        locked_until_date (``int`` ``32-bit``, *optional*):
            If set, the specified gift possibly cannot be sent until the specified date, see here » for the full flow.

    """

    __slots__: List[str] = ["id", "sticker", "stars", "convert_stars", "limited", "sold_out", "birthday", "can_upgrade", "require_premium", "limited_per_user", "peer_color_available", "availability_remains", "availability_total", "availability_resale", "first_sale_date", "last_sale_date", "upgrade_stars", "resell_min_stars", "title", "released_by", "per_user_total", "per_user_remains", "locked_until_date"]

    ID = 0x80ac53c3
    QUALNAME = "types.StarGift"

    def __init__(self, *, id: int, sticker: "raw.base.Document", stars: int, convert_stars: int, limited: Optional[bool] = None, sold_out: Optional[bool] = None, birthday: Optional[bool] = None, can_upgrade: Optional[bool] = None, require_premium: Optional[bool] = None, limited_per_user: Optional[bool] = None, peer_color_available: Optional[bool] = None, availability_remains: Optional[int] = None, availability_total: Optional[int] = None, availability_resale: Optional[int] = None, first_sale_date: Optional[int] = None, last_sale_date: Optional[int] = None, upgrade_stars: Optional[int] = None, resell_min_stars: Optional[int] = None, title: Optional[str] = None, released_by: "raw.base.Peer" = None, per_user_total: Optional[int] = None, per_user_remains: Optional[int] = None, locked_until_date: Optional[int] = None) -> None:
        self.id = id  # long
        self.sticker = sticker  # Document
        self.stars = stars  # long
        self.convert_stars = convert_stars  # long
        self.limited = limited  # flags.0?true
        self.sold_out = sold_out  # flags.1?true
        self.birthday = birthday  # flags.2?true
        self.can_upgrade = can_upgrade  # flags.3?true
        self.require_premium = require_premium  # flags.7?true
        self.limited_per_user = limited_per_user  # flags.8?true
        self.peer_color_available = peer_color_available  # flags.10?true
        self.availability_remains = availability_remains  # flags.0?int
        self.availability_total = availability_total  # flags.0?int
        self.availability_resale = availability_resale  # flags.4?long
        self.first_sale_date = first_sale_date  # flags.1?int
        self.last_sale_date = last_sale_date  # flags.1?int
        self.upgrade_stars = upgrade_stars  # flags.3?long
        self.resell_min_stars = resell_min_stars  # flags.4?long
        self.title = title  # flags.5?string
        self.released_by = released_by  # flags.6?Peer
        self.per_user_total = per_user_total  # flags.8?int
        self.per_user_remains = per_user_remains  # flags.8?int
        self.locked_until_date = locked_until_date  # flags.9?int

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "StarGift":
        
        flags = Int.read(b)
        
        limited = True if flags & (1 << 0) else False
        sold_out = True if flags & (1 << 1) else False
        birthday = True if flags & (1 << 2) else False
        can_upgrade = True if flags & (1 << 3) else False
        require_premium = True if flags & (1 << 7) else False
        limited_per_user = True if flags & (1 << 8) else False
        peer_color_available = True if flags & (1 << 10) else False
        id = Long.read(b)
        
        sticker = TLObject.read(b)
        
        stars = Long.read(b)
        
        availability_remains = Int.read(b) if flags & (1 << 0) else None
        availability_total = Int.read(b) if flags & (1 << 0) else None
        availability_resale = Long.read(b) if flags & (1 << 4) else None
        convert_stars = Long.read(b)
        
        first_sale_date = Int.read(b) if flags & (1 << 1) else None
        last_sale_date = Int.read(b) if flags & (1 << 1) else None
        upgrade_stars = Long.read(b) if flags & (1 << 3) else None
        resell_min_stars = Long.read(b) if flags & (1 << 4) else None
        title = String.read(b) if flags & (1 << 5) else None
        released_by = TLObject.read(b) if flags & (1 << 6) else None
        
        per_user_total = Int.read(b) if flags & (1 << 8) else None
        per_user_remains = Int.read(b) if flags & (1 << 8) else None
        locked_until_date = Int.read(b) if flags & (1 << 9) else None
        return StarGift(id=id, sticker=sticker, stars=stars, convert_stars=convert_stars, limited=limited, sold_out=sold_out, birthday=birthday, can_upgrade=can_upgrade, require_premium=require_premium, limited_per_user=limited_per_user, peer_color_available=peer_color_available, availability_remains=availability_remains, availability_total=availability_total, availability_resale=availability_resale, first_sale_date=first_sale_date, last_sale_date=last_sale_date, upgrade_stars=upgrade_stars, resell_min_stars=resell_min_stars, title=title, released_by=released_by, per_user_total=per_user_total, per_user_remains=per_user_remains, locked_until_date=locked_until_date)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        flags = 0
        flags |= (1 << 0) if self.limited else 0
        flags |= (1 << 1) if self.sold_out else 0
        flags |= (1 << 2) if self.birthday else 0
        flags |= (1 << 3) if self.can_upgrade else 0
        flags |= (1 << 7) if self.require_premium else 0
        flags |= (1 << 8) if self.limited_per_user else 0
        flags |= (1 << 10) if self.peer_color_available else 0
        flags |= (1 << 0) if self.availability_remains is not None else 0
        flags |= (1 << 0) if self.availability_total is not None else 0
        flags |= (1 << 4) if self.availability_resale is not None else 0
        flags |= (1 << 1) if self.first_sale_date is not None else 0
        flags |= (1 << 1) if self.last_sale_date is not None else 0
        flags |= (1 << 3) if self.upgrade_stars is not None else 0
        flags |= (1 << 4) if self.resell_min_stars is not None else 0
        flags |= (1 << 5) if self.title is not None else 0
        flags |= (1 << 6) if self.released_by is not None else 0
        flags |= (1 << 8) if self.per_user_total is not None else 0
        flags |= (1 << 8) if self.per_user_remains is not None else 0
        flags |= (1 << 9) if self.locked_until_date is not None else 0
        b.write(Int(flags))
        
        b.write(Long(self.id))
        
        b.write(self.sticker.write())
        
        b.write(Long(self.stars))
        
        if self.availability_remains is not None:
            b.write(Int(self.availability_remains))
        
        if self.availability_total is not None:
            b.write(Int(self.availability_total))
        
        if self.availability_resale is not None:
            b.write(Long(self.availability_resale))
        
        b.write(Long(self.convert_stars))
        
        if self.first_sale_date is not None:
            b.write(Int(self.first_sale_date))
        
        if self.last_sale_date is not None:
            b.write(Int(self.last_sale_date))
        
        if self.upgrade_stars is not None:
            b.write(Long(self.upgrade_stars))
        
        if self.resell_min_stars is not None:
            b.write(Long(self.resell_min_stars))
        
        if self.title is not None:
            b.write(String(self.title))
        
        if self.released_by is not None:
            b.write(self.released_by.write())
        
        if self.per_user_total is not None:
            b.write(Int(self.per_user_total))
        
        if self.per_user_remains is not None:
            b.write(Int(self.per_user_remains))
        
        if self.locked_until_date is not None:
            b.write(Int(self.locked_until_date))
        
        return b.getvalue()
