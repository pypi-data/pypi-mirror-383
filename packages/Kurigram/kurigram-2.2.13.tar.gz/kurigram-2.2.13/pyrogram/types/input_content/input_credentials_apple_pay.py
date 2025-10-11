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
from pyrogram import raw

from .input_credentials import InputCredentials


class InputCredentialsApplePay(InputCredentials):
    """Applies if a user enters new credentials using Apple Pay.

    Parameters:
        data (``str``):
            JSON-encoded data with the credential identifier.
    """
    def __init__(
        self,
        data: str,
    ):
        super().__init__()

        self.data = data

    async def write(self, client: "pyrogram.Client"):
        return raw.types.InputPaymentCredentialsApplePay(
            payment_data=raw.types.DataJSON(data=self.data)
        )
