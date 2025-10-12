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


class GetBotBusinessConnection(TLObject):  # type: ignore
    """Bots may invoke this method to re-fetch the updateBotBusinessConnect constructor associated with a specific business connection_id, see here » for more info on connected business bots.
This is needed for example for freshly logged in bots that are receiving some updateBotNewBusinessMessage, etc. updates because some users have already connected to the bot before it could login.
In this case, the bot is receiving messages from the business connection, but it hasn't cached the associated updateBotBusinessConnect with info about the connection (can it reply to messages? etc.) yet, and cannot receive the old ones because they were sent when the bot wasn't logged into the session yet.
This method can be used to fetch info about a not-yet-cached business connection, and should not be invoked if the info is already cached or to fetch changes, as eventual changes will automatically be sent as new updateBotBusinessConnect updates to the bot using the usual update delivery methods ».


    Details:
        - Layer: ``216``
        - ID: ``76A86270``

    Parameters:
        connection_id (``str``):
            Business connection ID ».

    Returns:
        :obj:`Updates <pyrogram.raw.base.Updates>`
    """

    __slots__: List[str] = ["connection_id"]

    ID = 0x76a86270
    QUALNAME = "functions.account.GetBotBusinessConnection"

    def __init__(self, *, connection_id: str) -> None:
        self.connection_id = connection_id  # string

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "GetBotBusinessConnection":
        # No flags
        
        connection_id = String.read(b)
        
        return GetBotBusinessConnection(connection_id=connection_id)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        # No flags
        
        b.write(String(self.connection_id))
        
        return b.getvalue()
