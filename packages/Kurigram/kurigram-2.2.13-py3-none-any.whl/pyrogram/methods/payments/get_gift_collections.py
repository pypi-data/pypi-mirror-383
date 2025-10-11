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
from typing import List, Union

import pyrogram
from pyrogram import raw, types


class GetGiftCollections:
    async def get_gift_collections(
        self: "pyrogram.Client",
        owner_id: Union[int, str]
    ) -> List["types.GiftCollection"]:
        """Returns collections of gifts owned by the given user or chat.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            owner_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the target chat.
                For your personal cloud (Saved Messages) you can simply use "me" or "self".

        Returns:
            List of :obj:`~pyrogram.types.GiftCollection`: On success, a list of collections is returned.
        """
        r = await self.invoke(
            raw.functions.payments.GetStarGiftCollections(
                peer=await self.resolve_peer(owner_id),
                hash=0
            )
        )

        return types.List(
            [
                await types.GiftCollection._parse(self, collection)
                for collection in r.collections
            ]
        )
