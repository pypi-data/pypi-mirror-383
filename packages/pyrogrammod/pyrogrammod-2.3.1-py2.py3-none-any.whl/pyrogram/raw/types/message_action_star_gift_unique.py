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


class MessageActionStarGiftUnique(TLObject):  # type: ignore
    """A gift » was upgraded to a collectible gift ».

    Constructor of :obj:`~pyrogram.raw.base.MessageAction`.

    Details:
        - Layer: ``216``
        - ID: ``95728543``

    Parameters:
        gift (:obj:`StarGift <pyrogram.raw.base.StarGift>`):
            The collectible gift.

        upgrade (``bool``, *optional*):
            If set, this collectible was upgraded » to a collectible gift from a previously received or sent (depending on the out flag of the containing messageService) non-collectible gift.

        transferred (``bool``, *optional*):
            If set, this collectible was transferred (either to the current user or by the current user to the other user in the private chat, depending on the out flag of the containing messageService).

        saved (``bool``, *optional*):
            If set, this gift is visible on the user or channel's profile page; can only be set for the receiver of a gift.

        refunded (``bool``, *optional*):
            This gift was upgraded to a collectible gift » and then re-downgraded to a regular gift because a request to refund the payment related to the upgrade was made, and the money was returned.

        prepaid_upgrade (``bool``, *optional*):
            The sender has pre-paid for the upgrade of this gift to a collectible gift.

        assigned (``bool``, *optional*):
            N/A

        can_export_at (``int`` ``32-bit``, *optional*):
            If set, indicates that the current gift can't be exported to the TON blockchain » yet: the owner will be able to export it at the specified unixtime.

        transfer_stars (``int`` ``64-bit``, *optional*):
            If set, indicates that the gift can be transferred » to another user by paying the specified amount of stars.

        from_id (:obj:`Peer <pyrogram.raw.base.Peer>`, *optional*):
            Sender of the gift (unset for anonymous gifts).

        peer (:obj:`Peer <pyrogram.raw.base.Peer>`, *optional*):
            Receiver of the gift.

        saved_id (``int`` ``64-bit``, *optional*):
            For channel gifts, ID to use in inputSavedStarGiftChat constructors.

        resale_amount (:obj:`StarsAmount <pyrogram.raw.base.StarsAmount>`, *optional*):
            Resale price of the gift.

        can_transfer_at (``int`` ``32-bit``, *optional*):
            If set, indicates that the current gift can't be transferred » yet: the owner will be able to transfer it at the specified unixtime.

        can_resell_at (``int`` ``32-bit``, *optional*):
            If set, indicates that the current gift can't be resold » yet: the owner will be able to put it up for sale at the specified unixtime.

        drop_original_details_stars (``int`` ``64-bit``, *optional*):
            N/A

    """

    __slots__: List[str] = ["gift", "upgrade", "transferred", "saved", "refunded", "prepaid_upgrade", "assigned", "can_export_at", "transfer_stars", "from_id", "peer", "saved_id", "resale_amount", "can_transfer_at", "can_resell_at", "drop_original_details_stars"]

    ID = 0x95728543
    QUALNAME = "types.MessageActionStarGiftUnique"

    def __init__(self, *, gift: "raw.base.StarGift", upgrade: Optional[bool] = None, transferred: Optional[bool] = None, saved: Optional[bool] = None, refunded: Optional[bool] = None, prepaid_upgrade: Optional[bool] = None, assigned: Optional[bool] = None, can_export_at: Optional[int] = None, transfer_stars: Optional[int] = None, from_id: "raw.base.Peer" = None, peer: "raw.base.Peer" = None, saved_id: Optional[int] = None, resale_amount: "raw.base.StarsAmount" = None, can_transfer_at: Optional[int] = None, can_resell_at: Optional[int] = None, drop_original_details_stars: Optional[int] = None) -> None:
        self.gift = gift  # StarGift
        self.upgrade = upgrade  # flags.0?true
        self.transferred = transferred  # flags.1?true
        self.saved = saved  # flags.2?true
        self.refunded = refunded  # flags.5?true
        self.prepaid_upgrade = prepaid_upgrade  # flags.11?true
        self.assigned = assigned  # flags.13?true
        self.can_export_at = can_export_at  # flags.3?int
        self.transfer_stars = transfer_stars  # flags.4?long
        self.from_id = from_id  # flags.6?Peer
        self.peer = peer  # flags.7?Peer
        self.saved_id = saved_id  # flags.7?long
        self.resale_amount = resale_amount  # flags.8?StarsAmount
        self.can_transfer_at = can_transfer_at  # flags.9?int
        self.can_resell_at = can_resell_at  # flags.10?int
        self.drop_original_details_stars = drop_original_details_stars  # flags.12?long

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "MessageActionStarGiftUnique":
        
        flags = Int.read(b)
        
        upgrade = True if flags & (1 << 0) else False
        transferred = True if flags & (1 << 1) else False
        saved = True if flags & (1 << 2) else False
        refunded = True if flags & (1 << 5) else False
        prepaid_upgrade = True if flags & (1 << 11) else False
        assigned = True if flags & (1 << 13) else False
        gift = TLObject.read(b)
        
        can_export_at = Int.read(b) if flags & (1 << 3) else None
        transfer_stars = Long.read(b) if flags & (1 << 4) else None
        from_id = TLObject.read(b) if flags & (1 << 6) else None
        
        peer = TLObject.read(b) if flags & (1 << 7) else None
        
        saved_id = Long.read(b) if flags & (1 << 7) else None
        resale_amount = TLObject.read(b) if flags & (1 << 8) else None
        
        can_transfer_at = Int.read(b) if flags & (1 << 9) else None
        can_resell_at = Int.read(b) if flags & (1 << 10) else None
        drop_original_details_stars = Long.read(b) if flags & (1 << 12) else None
        return MessageActionStarGiftUnique(gift=gift, upgrade=upgrade, transferred=transferred, saved=saved, refunded=refunded, prepaid_upgrade=prepaid_upgrade, assigned=assigned, can_export_at=can_export_at, transfer_stars=transfer_stars, from_id=from_id, peer=peer, saved_id=saved_id, resale_amount=resale_amount, can_transfer_at=can_transfer_at, can_resell_at=can_resell_at, drop_original_details_stars=drop_original_details_stars)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        flags = 0
        flags |= (1 << 0) if self.upgrade else 0
        flags |= (1 << 1) if self.transferred else 0
        flags |= (1 << 2) if self.saved else 0
        flags |= (1 << 5) if self.refunded else 0
        flags |= (1 << 11) if self.prepaid_upgrade else 0
        flags |= (1 << 13) if self.assigned else 0
        flags |= (1 << 3) if self.can_export_at is not None else 0
        flags |= (1 << 4) if self.transfer_stars is not None else 0
        flags |= (1 << 6) if self.from_id is not None else 0
        flags |= (1 << 7) if self.peer is not None else 0
        flags |= (1 << 7) if self.saved_id is not None else 0
        flags |= (1 << 8) if self.resale_amount is not None else 0
        flags |= (1 << 9) if self.can_transfer_at is not None else 0
        flags |= (1 << 10) if self.can_resell_at is not None else 0
        flags |= (1 << 12) if self.drop_original_details_stars is not None else 0
        b.write(Int(flags))
        
        b.write(self.gift.write())
        
        if self.can_export_at is not None:
            b.write(Int(self.can_export_at))
        
        if self.transfer_stars is not None:
            b.write(Long(self.transfer_stars))
        
        if self.from_id is not None:
            b.write(self.from_id.write())
        
        if self.peer is not None:
            b.write(self.peer.write())
        
        if self.saved_id is not None:
            b.write(Long(self.saved_id))
        
        if self.resale_amount is not None:
            b.write(self.resale_amount.write())
        
        if self.can_transfer_at is not None:
            b.write(Int(self.can_transfer_at))
        
        if self.can_resell_at is not None:
            b.write(Int(self.can_resell_at))
        
        if self.drop_original_details_stars is not None:
            b.write(Long(self.drop_original_details_stars))
        
        return b.getvalue()
