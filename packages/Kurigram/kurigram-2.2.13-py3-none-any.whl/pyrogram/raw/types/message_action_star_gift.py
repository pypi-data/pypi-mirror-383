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


class MessageActionStarGift(TLObject):  # type: ignore
    """Telegram API type.

    Constructor of :obj:`~pyrogram.raw.base.MessageAction`.

    Details:
        - Layer: ``214``
        - ID: ``F24DE7FA``

    Parameters:
        gift (:obj:`StarGift <pyrogram.raw.base.StarGift>`):
            N/A

        name_hidden (``bool``, *optional*):
            N/A

        saved (``bool``, *optional*):
            N/A

        converted (``bool``, *optional*):
            N/A

        upgraded (``bool``, *optional*):
            N/A

        refunded (``bool``, *optional*):
            N/A

        can_upgrade (``bool``, *optional*):
            N/A

        prepaid_upgrade (``bool``, *optional*):
            N/A

        upgrade_separate (``bool``, *optional*):
            N/A

        message (:obj:`TextWithEntities <pyrogram.raw.base.TextWithEntities>`, *optional*):
            N/A

        convert_stars (``int`` ``64-bit``, *optional*):
            N/A

        upgrade_msg_id (``int`` ``32-bit``, *optional*):
            N/A

        upgrade_stars (``int`` ``64-bit``, *optional*):
            N/A

        from_id (:obj:`Peer <pyrogram.raw.base.Peer>`, *optional*):
            N/A

        peer (:obj:`Peer <pyrogram.raw.base.Peer>`, *optional*):
            N/A

        saved_id (``int`` ``64-bit``, *optional*):
            N/A

        prepaid_upgrade_hash (``str``, *optional*):
            N/A

        gift_msg_id (``int`` ``32-bit``, *optional*):
            N/A

    """

    __slots__: List[str] = ["gift", "name_hidden", "saved", "converted", "upgraded", "refunded", "can_upgrade", "prepaid_upgrade", "upgrade_separate", "message", "convert_stars", "upgrade_msg_id", "upgrade_stars", "from_id", "peer", "saved_id", "prepaid_upgrade_hash", "gift_msg_id"]

    ID = 0xf24de7fa
    QUALNAME = "types.MessageActionStarGift"

    def __init__(self, *, gift: "raw.base.StarGift", name_hidden: Optional[bool] = None, saved: Optional[bool] = None, converted: Optional[bool] = None, upgraded: Optional[bool] = None, refunded: Optional[bool] = None, can_upgrade: Optional[bool] = None, prepaid_upgrade: Optional[bool] = None, upgrade_separate: Optional[bool] = None, message: "raw.base.TextWithEntities" = None, convert_stars: Optional[int] = None, upgrade_msg_id: Optional[int] = None, upgrade_stars: Optional[int] = None, from_id: "raw.base.Peer" = None, peer: "raw.base.Peer" = None, saved_id: Optional[int] = None, prepaid_upgrade_hash: Optional[str] = None, gift_msg_id: Optional[int] = None) -> None:
        self.gift = gift  # StarGift
        self.name_hidden = name_hidden  # flags.0?true
        self.saved = saved  # flags.2?true
        self.converted = converted  # flags.3?true
        self.upgraded = upgraded  # flags.5?true
        self.refunded = refunded  # flags.9?true
        self.can_upgrade = can_upgrade  # flags.10?true
        self.prepaid_upgrade = prepaid_upgrade  # flags.13?true
        self.upgrade_separate = upgrade_separate  # flags.16?true
        self.message = message  # flags.1?TextWithEntities
        self.convert_stars = convert_stars  # flags.4?long
        self.upgrade_msg_id = upgrade_msg_id  # flags.5?int
        self.upgrade_stars = upgrade_stars  # flags.8?long
        self.from_id = from_id  # flags.11?Peer
        self.peer = peer  # flags.12?Peer
        self.saved_id = saved_id  # flags.12?long
        self.prepaid_upgrade_hash = prepaid_upgrade_hash  # flags.14?string
        self.gift_msg_id = gift_msg_id  # flags.15?int

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "MessageActionStarGift":
        
        flags = Int.read(b)
        
        name_hidden = True if flags & (1 << 0) else False
        saved = True if flags & (1 << 2) else False
        converted = True if flags & (1 << 3) else False
        upgraded = True if flags & (1 << 5) else False
        refunded = True if flags & (1 << 9) else False
        can_upgrade = True if flags & (1 << 10) else False
        prepaid_upgrade = True if flags & (1 << 13) else False
        upgrade_separate = True if flags & (1 << 16) else False
        gift = TLObject.read(b)
        
        message = TLObject.read(b) if flags & (1 << 1) else None
        
        convert_stars = Long.read(b) if flags & (1 << 4) else None
        upgrade_msg_id = Int.read(b) if flags & (1 << 5) else None
        upgrade_stars = Long.read(b) if flags & (1 << 8) else None
        from_id = TLObject.read(b) if flags & (1 << 11) else None
        
        peer = TLObject.read(b) if flags & (1 << 12) else None
        
        saved_id = Long.read(b) if flags & (1 << 12) else None
        prepaid_upgrade_hash = String.read(b) if flags & (1 << 14) else None
        gift_msg_id = Int.read(b) if flags & (1 << 15) else None
        return MessageActionStarGift(gift=gift, name_hidden=name_hidden, saved=saved, converted=converted, upgraded=upgraded, refunded=refunded, can_upgrade=can_upgrade, prepaid_upgrade=prepaid_upgrade, upgrade_separate=upgrade_separate, message=message, convert_stars=convert_stars, upgrade_msg_id=upgrade_msg_id, upgrade_stars=upgrade_stars, from_id=from_id, peer=peer, saved_id=saved_id, prepaid_upgrade_hash=prepaid_upgrade_hash, gift_msg_id=gift_msg_id)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        flags = 0
        flags |= (1 << 0) if self.name_hidden else 0
        flags |= (1 << 2) if self.saved else 0
        flags |= (1 << 3) if self.converted else 0
        flags |= (1 << 5) if self.upgraded else 0
        flags |= (1 << 9) if self.refunded else 0
        flags |= (1 << 10) if self.can_upgrade else 0
        flags |= (1 << 13) if self.prepaid_upgrade else 0
        flags |= (1 << 16) if self.upgrade_separate else 0
        flags |= (1 << 1) if self.message is not None else 0
        flags |= (1 << 4) if self.convert_stars is not None else 0
        flags |= (1 << 5) if self.upgrade_msg_id is not None else 0
        flags |= (1 << 8) if self.upgrade_stars is not None else 0
        flags |= (1 << 11) if self.from_id is not None else 0
        flags |= (1 << 12) if self.peer is not None else 0
        flags |= (1 << 12) if self.saved_id is not None else 0
        flags |= (1 << 14) if self.prepaid_upgrade_hash is not None else 0
        flags |= (1 << 15) if self.gift_msg_id is not None else 0
        b.write(Int(flags))
        
        b.write(self.gift.write())
        
        if self.message is not None:
            b.write(self.message.write())
        
        if self.convert_stars is not None:
            b.write(Long(self.convert_stars))
        
        if self.upgrade_msg_id is not None:
            b.write(Int(self.upgrade_msg_id))
        
        if self.upgrade_stars is not None:
            b.write(Long(self.upgrade_stars))
        
        if self.from_id is not None:
            b.write(self.from_id.write())
        
        if self.peer is not None:
            b.write(self.peer.write())
        
        if self.saved_id is not None:
            b.write(Long(self.saved_id))
        
        if self.prepaid_upgrade_hash is not None:
            b.write(String(self.prepaid_upgrade_hash))
        
        if self.gift_msg_id is not None:
            b.write(Int(self.gift_msg_id))
        
        return b.getvalue()
