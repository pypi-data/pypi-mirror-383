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

import pyrogram
from pyrogram import raw, types


class GetBusinessConnection:
    async def get_business_connection(
        self: "pyrogram.Client",
        business_connection_id: str
    ):
        """Use this method to get information about the connection of the bot with a business account.

        .. include:: /_includes/usable-by/bots.rst

        Parameters:
            connection_id (``str``):
                Unique identifier of the business connection.

        Returns:
            :obj:`~pyrogram.types.BusinessConnection`: On success the business connection is returned.

        Example:
            .. code-block:: python

                # Get a business connection information
                await app.get_business_connection(connection_id)
        """
        r = await self.invoke(
            raw.functions.account.GetBotBusinessConnection(
                connection_id=business_connection_id
            )
        )

        users = {i.id: i for i in r.users}

        return types.BusinessConnection._parse(self, r.updates[0].connection, users)
