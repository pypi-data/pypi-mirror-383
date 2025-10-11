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

from typing import List, Optional

import pyrogram
from pyrogram import enums, raw, types, utils


class TranslateText:
    async def translate_text(
        self: "pyrogram.Client",
        text: str,
        to_language_code: str,
        parse_mode: Optional["enums.ParseMode"] = None,
        entities: List["types.MessageEntity"] = None,
    ) -> "types.FormattedText":
        """Translate a text to the given language.

        If the current user is a Telegram Premium user, then text formatting is preserved.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            text (``str``):
                Text to translate.

            to_language_code (``str``):
                Language code of the language to which the message is translated.
                Must be one of "af", "sq", "am", "ar", "hy", "az", "eu", "be", "bn", "bs", "bg", "ca", "ceb", "zh-CN", "zh", "zh-Hans", "zh-TW", "zh-Hant", "co", "hr", "cs", "da", "nl", "en", "eo", "et",
                "fi", "fr", "fy", "gl", "ka", "de", "el", "gu", "ht", "ha", "haw", "he", "iw", "hi", "hmn", "hu", "is", "ig", "id", "in", "ga", "it", "ja", "jv", "kn", "kk", "km", "rw", "ko",
                "ku", "ky", "lo", "la", "lv", "lt", "lb", "mk", "mg", "ms", "ml", "mt", "mi", "mr", "mn", "my", "ne", "no", "ny", "or", "ps", "fa", "pl", "pt", "pa", "ro", "ru", "sm", "gd", "sr",
                "st", "sn", "sd", "si", "sk", "sl", "so", "es", "su", "sw", "sv", "tl", "tg", "ta", "tt", "te", "th", "tr", "tk", "uk", "ur", "ug", "uz", "vi", "cy", "xh", "yi", "ji", "yo", "zu"

        Returns:
            :obj:`~pyrogram.types.FormattedText`: On success, information about the translated text is returned.

        Example:
            .. code-block:: python

                await app.translate_text("Hello!", "ru")
        """
        message, entities = (await utils.parse_text_entities(self, text, parse_mode, entities)).values()

        r = await self.invoke(
            raw.functions.messages.TranslateText(
                to_lang=to_language_code,
                text=[
                    raw.types.TextWithEntities(
                        text=message,
                        entities=entities or []
                    )
                ]
            )
        )

        return types.FormattedText._parse(self, r.result[0])
