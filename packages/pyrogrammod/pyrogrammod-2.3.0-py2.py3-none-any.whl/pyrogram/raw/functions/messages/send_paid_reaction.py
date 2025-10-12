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


class SendPaidReaction(TLObject):  # type: ignore
    """Sends one or more paid Telegram Star reactions », transferring Telegram Stars » to a channel's balance.


    Details:
        - Layer: ``216``
        - ID: ``58BBCB50``

    Parameters:
        peer (:obj:`InputPeer <pyrogram.raw.base.InputPeer>`):
            The channel

        msg_id (``int`` ``32-bit``):
            The message to react to

        count (``int`` ``32-bit``):
            The number of stars to send (each will increment the reaction counter by one).

        random_id (``int`` ``64-bit``):
            Unique client message ID required to prevent message resending. Note: this argument must be composed of a 64-bit integer where the lower 32 bits are random, and the higher 32 bits are equal to the current unixtime, i.e. uint64_t random_id = (time() << 32) | ((uint64_t)random_uint32_t()): this differs from the random_id format of all other methods in the API, which just take 64 random bits.

        private (:obj:`PaidReactionPrivacy <pyrogram.raw.base.PaidReactionPrivacy>`, *optional*):
            Each post with star reactions has a leaderboard with the top senders, but users can opt out of appearing there if they prefer more privacy. Not populating this field will use the default reaction privacy, stored on the server and synced to clients using updatePaidReactionPrivacy (see here for more info).

    Returns:
        :obj:`Updates <pyrogram.raw.base.Updates>`
    """

    __slots__: List[str] = ["peer", "msg_id", "count", "random_id", "private"]

    ID = 0x58bbcb50
    QUALNAME = "functions.messages.SendPaidReaction"

    def __init__(self, *, peer: "raw.base.InputPeer", msg_id: int, count: int, random_id: int, private: "raw.base.PaidReactionPrivacy" = None) -> None:
        self.peer = peer  # InputPeer
        self.msg_id = msg_id  # int
        self.count = count  # int
        self.random_id = random_id  # long
        self.private = private  # flags.0?PaidReactionPrivacy

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "SendPaidReaction":
        
        flags = Int.read(b)
        
        peer = TLObject.read(b)
        
        msg_id = Int.read(b)
        
        count = Int.read(b)
        
        random_id = Long.read(b)
        
        private = TLObject.read(b) if flags & (1 << 0) else None
        
        return SendPaidReaction(peer=peer, msg_id=msg_id, count=count, random_id=random_id, private=private)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        flags = 0
        flags |= (1 << 0) if self.private is not None else 0
        b.write(Int(flags))
        
        b.write(self.peer.write())
        
        b.write(Int(self.msg_id))
        
        b.write(Int(self.count))
        
        b.write(Long(self.random_id))
        
        if self.private is not None:
            b.write(self.private.write())
        
        return b.getvalue()
