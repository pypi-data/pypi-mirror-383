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

from .add_collection_gifts import AddCollectionGifts
from .apply_gift_code import ApplyGiftCode
from .buy_gift_upgrade import BuyGiftUpgrade
from .check_gift_code import CheckGiftCode
from .convert_gift_to_stars import ConvertGiftToStars
from .create_gift_collection import CreateGiftCollection
from .delete_gift_collection import DeleteGiftCollection
from .get_available_gifts import GetAvailableGifts
from .get_chat_gifts import GetChatGifts
from .get_chat_gifts_count import GetChatGiftsCount
from .get_gift_collections import GetGiftCollections
from .get_gift_upgrade_preview import GetGiftUpgradePreview
from .get_payment_form import GetPaymentForm
from .get_stars_balance import GetStarsBalance
from .get_ton_balance import GetTonBalance
from .get_upgraded_gift import GetUpgradedGift
from .get_upgraded_gift_value_info import GetUpgradedGiftValueInfo
from .gift_premium_with_stars import GiftPremiumWithStars
from .hide_gift import HideGift
from .remove_collection_gifts import RemoveCollectionGifts
from .reorder_collection_gifts import ReorderCollectionGifts
from .reorder_gift_collections import ReorderGiftCollections
from .search_gifts_for_resale import SearchGiftsForResale
from .send_gift import SendGift
from .send_payment_form import SendPaymentForm
from .send_resold_gift import SendResoldGift
from .set_gift_collection_name import SetGiftCollectionName
from .set_gift_resale_price import SetGiftResalePrice
from .set_pinned_gifts import SetPinnedGifts
from .show_gift import ShowGift
from .transfer_gift import TransferGift
from .upgrade_gift import UpgradeGift


class Payments(
    AddCollectionGifts,
    ApplyGiftCode,
    BuyGiftUpgrade,
    CheckGiftCode,
    ConvertGiftToStars,
    CreateGiftCollection,
    DeleteGiftCollection,
    GetAvailableGifts,
    GetChatGifts,
    GetChatGiftsCount,
    GetGiftCollections,
    GetGiftUpgradePreview,
    GetPaymentForm,
    GetStarsBalance,
    GetTonBalance,
    GetUpgradedGift,
    GetUpgradedGiftValueInfo,
    GiftPremiumWithStars,
    HideGift,
    RemoveCollectionGifts,
    ReorderCollectionGifts,
    ReorderGiftCollections,
    SearchGiftsForResale,
    SendGift,
    SendPaymentForm,
    SendResoldGift,
    SetGiftCollectionName,
    SetGiftResalePrice,
    SetPinnedGifts,
    ShowGift,
    TransferGift,
    UpgradeGift
):
    pass
