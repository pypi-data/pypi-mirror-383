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


class ToggleChatStarGiftNotifications(TLObject):  # type: ignore
    """Enables or disables the reception of notifications every time a gift » is received by the specified channel, can only be invoked by admins with post_messages admin rights.


    Details:
        - Layer: ``216``
        - ID: ``60EAEFA1``

    Parameters:
        peer (:obj:`InputPeer <pyrogram.raw.base.InputPeer>`):
            The channel for which to receive or not receive notifications.

        enabled (``bool``, *optional*):
            Whether to enable or disable reception of notifications in the form of messageActionStarGiftUnique and messageActionStarGift service messages from the channel.

    Returns:
        ``bool``
    """

    __slots__: List[str] = ["peer", "enabled"]

    ID = 0x60eaefa1
    QUALNAME = "functions.payments.ToggleChatStarGiftNotifications"

    def __init__(self, *, peer: "raw.base.InputPeer", enabled: Optional[bool] = None) -> None:
        self.peer = peer  # InputPeer
        self.enabled = enabled  # flags.0?true

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "ToggleChatStarGiftNotifications":
        
        flags = Int.read(b)
        
        enabled = True if flags & (1 << 0) else False
        peer = TLObject.read(b)
        
        return ToggleChatStarGiftNotifications(peer=peer, enabled=enabled)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        flags = 0
        flags |= (1 << 0) if self.enabled else 0
        b.write(Int(flags))
        
        b.write(self.peer.write())
        
        return b.getvalue()
