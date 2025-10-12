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


class InvokeWithGooglePlayIntegrity(TLObject):  # type: ignore
    """Official clients only, invoke with Google Play Integrity token.


    Details:
        - Layer: ``216``
        - ID: ``1DF92984``

    Parameters:
        nonce (``str``):
            Nonce.

        token (``str``):
            Token.

        query (Any function from :obj:`~pyrogram.raw.functions`):
            Query.

    Returns:
        Any object from :obj:`~pyrogram.raw.types`
    """

    __slots__: List[str] = ["nonce", "token", "query"]

    ID = 0x1df92984
    QUALNAME = "functions.InvokeWithGooglePlayIntegrity"

    def __init__(self, *, nonce: str, token: str, query: TLObject) -> None:
        self.nonce = nonce  # string
        self.token = token  # string
        self.query = query  # !X

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "InvokeWithGooglePlayIntegrity":
        # No flags
        
        nonce = String.read(b)
        
        token = String.read(b)
        
        query = TLObject.read(b)
        
        return InvokeWithGooglePlayIntegrity(nonce=nonce, token=token, query=query)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        # No flags
        
        b.write(String(self.nonce))
        
        b.write(String(self.token))
        
        b.write(self.query.write())
        
        return b.getvalue()
