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


class CheckCanSendGift(TLObject):  # type: ignore
    """Telegram API function.

    Details:
        - Layer: ``214``
        - ID: ``C0C4EDC9``

    Parameters:
        gift_id (``int`` ``64-bit``):
            N/A

    Returns:
        :obj:`payments.CheckCanSendGiftResult <pyrogram.raw.base.payments.CheckCanSendGiftResult>`
    """

    __slots__: List[str] = ["gift_id"]

    ID = 0xc0c4edc9
    QUALNAME = "functions.payments.CheckCanSendGift"

    def __init__(self, *, gift_id: int) -> None:
        self.gift_id = gift_id  # long

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "CheckCanSendGift":
        # No flags
        
        gift_id = Long.read(b)
        
        return CheckCanSendGift(gift_id=gift_id)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        # No flags
        
        b.write(Long(self.gift_id))
        
        return b.getvalue()
