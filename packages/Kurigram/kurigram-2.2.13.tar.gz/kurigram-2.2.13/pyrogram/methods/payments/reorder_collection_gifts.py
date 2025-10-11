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
import re
from typing import List, Union

import pyrogram
from pyrogram import raw, types


class ReorderCollectionGifts:
    async def reorder_collection_gifts(
        self: "pyrogram.Client",
        owner_id: Union[int, str],
        collection_id: int,
        gift_ids: List[str]
    ) -> "types.GiftCollection":
        """Changes order of gifts in a collection.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            owner_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the target chat.
                For your personal cloud (Saved Messages) you can simply use "me" or "self".

            collection_id (``int``):
                Identifier of the gift collection.

            gift_ids (List of ``str``):
                Identifier of the gifts to move to the beginning of the collection.
                All other gifts are placed in the current order after the specified gifts

        Returns:
            :obj:`~pyrogram.types.GiftCollection`: On success, a updated collection is returned.

        Example:
            .. code-block:: python

                await app.reorder_collection_gifts("me", 123, ["https://t.me/nft/NekoHelmet-9215", "https://t.me/nft/JellyBunny-729"])
        """
        stargifts = []

        for gift in gift_ids:
            if not isinstance(gift, str):
                raise ValueError(f"gift id has to be str, but {type(gift)} was provided")

            saved_gift_match = re.match(r"^(-\d+)_(\d+)$", gift)
            slug_match = self.UPGRADED_GIFT_RE.match(gift)

            if saved_gift_match:
                stargifts.append(
                    raw.types.InputSavedStarGiftChat(
                        peer=await self.resolve_peer(saved_gift_match.group(1)),
                        saved_id=int(saved_gift_match.group(2))
                    )
                )
            elif slug_match:
                stargifts.append(
                    raw.types.InputSavedStarGiftSlug(
                        slug=slug_match.group(1)
                    )
                )
            else:
                stargifts.append(
                    raw.types.InputSavedStarGiftUser(
                        msg_id=int(gift)
                    )
                )

        r = await self.invoke(
            raw.functions.payments.UpdateStarGiftCollection(
                peer=await self.resolve_peer(owner_id),
                collection_id=collection_id,
                order=stargifts
            )
        )

        return await types.GiftCollection._parse(self, r)
