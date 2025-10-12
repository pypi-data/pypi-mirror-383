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


class GetStatsURL(TLObject):  # type: ignore
    """Returns URL with the chat statistics. Currently this method can be used only for channels


    Details:
        - Layer: ``216``
        - ID: ``812C2AE6``

    Parameters:
        peer (:obj:`InputPeer <pyrogram.raw.base.InputPeer>`):
            Chat identifier

        params (``str``):
            Parameters from tg://statsrefresh?params=****** link

        dark (``bool``, *optional*):
            Pass true if a URL with the dark theme must be returned

    Returns:
        :obj:`StatsURL <pyrogram.raw.base.StatsURL>`
    """

    __slots__: List[str] = ["peer", "params", "dark"]

    ID = 0x812c2ae6
    QUALNAME = "functions.messages.GetStatsURL"

    def __init__(self, *, peer: "raw.base.InputPeer", params: str, dark: Optional[bool] = None) -> None:
        self.peer = peer  # InputPeer
        self.params = params  # string
        self.dark = dark  # flags.0?true

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "GetStatsURL":
        
        flags = Int.read(b)
        
        dark = True if flags & (1 << 0) else False
        peer = TLObject.read(b)
        
        params = String.read(b)
        
        return GetStatsURL(peer=peer, params=params, dark=dark)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        flags = 0
        flags |= (1 << 0) if self.dark else 0
        b.write(Int(flags))
        
        b.write(self.peer.write())
        
        b.write(String(self.params))
        
        return b.getvalue()
