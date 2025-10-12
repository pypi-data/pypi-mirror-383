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


class BotApp(TLObject):  # type: ignore
    """Contains information about a direct link Mini App

    Constructor of :obj:`~pyrogram.raw.base.messages.BotApp`.

    Details:
        - Layer: ``216``
        - ID: ``EB50ADF5``

    Parameters:
        app (:obj:`BotApp <pyrogram.raw.base.BotApp>`):
            Bot app information

        inactive (``bool``, *optional*):
            Whether the web app was never used by the user, and confirmation must be asked from the user before opening it.

        request_write_access (``bool``, *optional*):
            The bot is asking permission to send messages to the user: if the user agrees, set the write_allowed flag when invoking messages.requestAppWebView.

        has_settings (``bool``, *optional*):
            Deprecated flag, can be ignored.

    Functions:
        This object can be returned by 1 function.

        .. currentmodule:: pyrogram.raw.functions

        .. autosummary::
            :nosignatures:

            messages.GetBotApp
    """

    __slots__: List[str] = ["app", "inactive", "request_write_access", "has_settings"]

    ID = 0xeb50adf5
    QUALNAME = "types.messages.BotApp"

    def __init__(self, *, app: "raw.base.BotApp", inactive: Optional[bool] = None, request_write_access: Optional[bool] = None, has_settings: Optional[bool] = None) -> None:
        self.app = app  # BotApp
        self.inactive = inactive  # flags.0?true
        self.request_write_access = request_write_access  # flags.1?true
        self.has_settings = has_settings  # flags.2?true

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "BotApp":
        
        flags = Int.read(b)
        
        inactive = True if flags & (1 << 0) else False
        request_write_access = True if flags & (1 << 1) else False
        has_settings = True if flags & (1 << 2) else False
        app = TLObject.read(b)
        
        return BotApp(app=app, inactive=inactive, request_write_access=request_write_access, has_settings=has_settings)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        flags = 0
        flags |= (1 << 0) if self.inactive else 0
        flags |= (1 << 1) if self.request_write_access else 0
        flags |= (1 << 2) if self.has_settings else 0
        b.write(Int(flags))
        
        b.write(self.app.write())
        
        return b.getvalue()
