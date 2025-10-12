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


class StarsTransaction(TLObject):  # type: ignore
    """Represents a Telegram Stars or TON transaction ».

    Constructor of :obj:`~pyrogram.raw.base.StarsTransaction`.

    Details:
        - Layer: ``216``
        - ID: ``13659EB0``

    Parameters:
        id (``str``):
            Transaction ID.

        amount (:obj:`StarsAmount <pyrogram.raw.base.StarsAmount>`):
            Amount of Telegram Stars or TON.

        date (``int`` ``32-bit``):
            Date of the transaction (unixtime).

        peer (:obj:`StarsTransactionPeer <pyrogram.raw.base.StarsTransactionPeer>`):
            Source of the incoming transaction, or its recipient for outgoing transactions.

        refund (``bool``, *optional*):
            Whether this transaction is a refund.

        pending (``bool``, *optional*):
            The transaction is currently pending.

        failed (``bool``, *optional*):
            This transaction has failed.

        gift (``bool``, *optional*):
            This transaction was a gift from the user in peer.peer.

        reaction (``bool``, *optional*):
            This transaction is a paid reaction ».

        subscription (``bool``, *optional*):
            N/A

        stargift_upgrade (``bool``, *optional*):
            This transaction pays for the upgrade of a gift to a collectible gift ».

        floodskip (``bool``, *optional*):
            N/A

        business_transfer (``bool``, *optional*):
            This transaction transfers stars from the balance of a user account connected to a business bot, to the balance of the business bot, see here » for more info.

        stargift_resale (``bool``, *optional*):
            This transaction is related to the resale of a collectible gift ».

        paid_message (``bool``, *optional*):
            N/A

        posts_search (``bool``, *optional*):
            Represents payment for a paid global post search ».

        premium_gift (``bool``, *optional*):
            N/A

        stargift_prepaid_upgrade (``bool``, *optional*):
            Represents payment for a separate prepaid upgrade of a gift.

        stargift_drop_original_details (``bool``, *optional*):
            N/A

        title (``str``, *optional*):
            For transactions with bots, title of the bought product.

        description (``str``, *optional*):
            For transactions with bots, description of the bought product.

        photo (:obj:`WebDocument <pyrogram.raw.base.WebDocument>`, *optional*):
            For transactions with bots, photo of the bought product.

        transaction_date (``int`` ``32-bit``, *optional*):
            If neither pending nor failed are set, the transaction was completed successfully, and this field will contain the point in time (Unix timestamp) when the withdrawal was completed successfully.

        transaction_url (``str``, *optional*):
            If neither pending nor failed are set, the transaction was completed successfully, and this field will contain a URL where the withdrawal transaction can be viewed.

        bot_payload (``bytes``, *optional*):
            Bot specified invoice payload (i.e. the payload passed to inputMediaInvoice when creating the invoice).

        msg_id (``int`` ``32-bit``, *optional*):
            For paid media transactions », message ID of the paid media posted to peer.peer (can point to a deleted message; either way, extended_media will always contain the bought media).

        extended_media (List of :obj:`MessageMedia <pyrogram.raw.base.MessageMedia>`, *optional*):
            The purchased paid media ».

        subscription_period (``int`` ``32-bit``, *optional*):
            The number of seconds between consecutive Telegram Star debiting for Telegram Star subscriptions ».

        giveaway_post_id (``int`` ``32-bit``, *optional*):
            ID of the message containing the messageMediaGiveaway, for incoming star giveaway prizes.

        stargift (:obj:`StarGift <pyrogram.raw.base.StarGift>`, *optional*):
            This transaction indicates a purchase or a sale (conversion back to Stars) of a gift ».

        floodskip_number (``int`` ``32-bit``, *optional*):
            This transaction is payment for paid bot broadcasts.  Paid broadcasts are only allowed if the allow_paid_floodskip parameter of messages.sendMessage and other message sending methods is set while trying to broadcast more than 30 messages per second to bot users. The integer value returned by this flag indicates the number of billed API calls.

        starref_commission_permille (``int`` ``32-bit``, *optional*):
            This transaction is the receival (or refund) of an affiliate commission (i.e. this is the transaction received by the peer that created the referral link, flag 17 is for transactions made by users that imported the referral link).

        starref_peer (:obj:`Peer <pyrogram.raw.base.Peer>`, *optional*):
            For transactions made by referred users, the peer that received the affiliate commission.

        starref_amount (:obj:`StarsAmount <pyrogram.raw.base.StarsAmount>`, *optional*):
            For transactions made by referred users, the amount of Telegram Stars received by the affiliate, can be negative for refunds.

        paid_messages (``int`` ``32-bit``, *optional*):
            This transaction is related to the reception or transmission of a paid message ».

        premium_gift_months (``int`` ``32-bit``, *optional*):
            This transaction indicates the payment for a gifted Telegram Premium subscription ».

        ads_proceeds_from_date (``int`` ``32-bit``, *optional*):
            Indicates that this is payment for ad revenue from the specified unixtime (always set together with ads_proceeds_to_date).

        ads_proceeds_to_date (``int`` ``32-bit``, *optional*):
            Indicates that this is payment for ad revenue to the specified unixtime.

    """

    __slots__: List[str] = ["id", "amount", "date", "peer", "refund", "pending", "failed", "gift", "reaction", "subscription", "stargift_upgrade", "floodskip", "business_transfer", "stargift_resale", "paid_message", "posts_search", "premium_gift", "stargift_prepaid_upgrade", "stargift_drop_original_details", "title", "description", "photo", "transaction_date", "transaction_url", "bot_payload", "msg_id", "extended_media", "subscription_period", "giveaway_post_id", "stargift", "floodskip_number", "starref_commission_permille", "starref_peer", "starref_amount", "paid_messages", "premium_gift_months", "ads_proceeds_from_date", "ads_proceeds_to_date"]

    ID = 0x13659eb0
    QUALNAME = "types.StarsTransaction"

    def __init__(self, *, id: str, amount: "raw.base.StarsAmount", date: int, peer: "raw.base.StarsTransactionPeer", refund: Optional[bool] = None, pending: Optional[bool] = None, failed: Optional[bool] = None, gift: Optional[bool] = None, reaction: Optional[bool] = None, subscription: Optional[bool] = None, stargift_upgrade: Optional[bool] = None, floodskip: Optional[bool] = None, business_transfer: Optional[bool] = None, stargift_resale: Optional[bool] = None, paid_message: Optional[bool] = None, posts_search: Optional[bool] = None, premium_gift: Optional[bool] = None, stargift_prepaid_upgrade: Optional[bool] = None, stargift_drop_original_details: Optional[bool] = None, title: Optional[str] = None, description: Optional[str] = None, photo: "raw.base.WebDocument" = None, transaction_date: Optional[int] = None, transaction_url: Optional[str] = None, bot_payload: Optional[bytes] = None, msg_id: Optional[int] = None, extended_media: Optional[List["raw.base.MessageMedia"]] = None, subscription_period: Optional[int] = None, giveaway_post_id: Optional[int] = None, stargift: "raw.base.StarGift" = None, floodskip_number: Optional[int] = None, starref_commission_permille: Optional[int] = None, starref_peer: "raw.base.Peer" = None, starref_amount: "raw.base.StarsAmount" = None, paid_messages: Optional[int] = None, premium_gift_months: Optional[int] = None, ads_proceeds_from_date: Optional[int] = None, ads_proceeds_to_date: Optional[int] = None) -> None:
        self.id = id  # string
        self.amount = amount  # StarsAmount
        self.date = date  # int
        self.peer = peer  # StarsTransactionPeer
        self.refund = refund  # flags.3?true
        self.pending = pending  # flags.4?true
        self.failed = failed  # flags.6?true
        self.gift = gift  # flags.10?true
        self.reaction = reaction  # flags.11?true
        self.subscription = subscription  # flags.12?true
        self.stargift_upgrade = stargift_upgrade  # flags.18?true
        self.floodskip = floodskip  # flags.15?true
        self.business_transfer = business_transfer  # flags.21?true
        self.stargift_resale = stargift_resale  # flags.22?true
        self.paid_message = paid_message  # flags.19?true
        self.posts_search = posts_search  # flags.24?true
        self.premium_gift = premium_gift  # flags.20?true
        self.stargift_prepaid_upgrade = stargift_prepaid_upgrade  # flags.25?true
        self.stargift_drop_original_details = stargift_drop_original_details  # flags.26?true
        self.title = title  # flags.0?string
        self.description = description  # flags.1?string
        self.photo = photo  # flags.2?WebDocument
        self.transaction_date = transaction_date  # flags.5?int
        self.transaction_url = transaction_url  # flags.5?string
        self.bot_payload = bot_payload  # flags.7?bytes
        self.msg_id = msg_id  # flags.8?int
        self.extended_media = extended_media  # flags.9?Vector<MessageMedia>
        self.subscription_period = subscription_period  # flags.12?int
        self.giveaway_post_id = giveaway_post_id  # flags.13?int
        self.stargift = stargift  # flags.14?StarGift
        self.floodskip_number = floodskip_number  # flags.15?int
        self.starref_commission_permille = starref_commission_permille  # flags.16?int
        self.starref_peer = starref_peer  # flags.17?Peer
        self.starref_amount = starref_amount  # flags.17?StarsAmount
        self.paid_messages = paid_messages  # flags.19?int
        self.premium_gift_months = premium_gift_months  # flags.20?int
        self.ads_proceeds_from_date = ads_proceeds_from_date  # flags.23?int
        self.ads_proceeds_to_date = ads_proceeds_to_date  # flags.23?int

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "StarsTransaction":
        
        flags = Int.read(b)
        
        refund = True if flags & (1 << 3) else False
        pending = True if flags & (1 << 4) else False
        failed = True if flags & (1 << 6) else False
        gift = True if flags & (1 << 10) else False
        reaction = True if flags & (1 << 11) else False
        subscription = True if flags & (1 << 12) else False
        stargift_upgrade = True if flags & (1 << 18) else False
        floodskip = True if flags & (1 << 15) else False
        business_transfer = True if flags & (1 << 21) else False
        stargift_resale = True if flags & (1 << 22) else False
        paid_message = True if flags & (1 << 19) else False
        posts_search = True if flags & (1 << 24) else False
        premium_gift = True if flags & (1 << 20) else False
        stargift_prepaid_upgrade = True if flags & (1 << 25) else False
        stargift_drop_original_details = True if flags & (1 << 26) else False
        id = String.read(b)
        
        amount = TLObject.read(b)
        
        date = Int.read(b)
        
        peer = TLObject.read(b)
        
        title = String.read(b) if flags & (1 << 0) else None
        description = String.read(b) if flags & (1 << 1) else None
        photo = TLObject.read(b) if flags & (1 << 2) else None
        
        transaction_date = Int.read(b) if flags & (1 << 5) else None
        transaction_url = String.read(b) if flags & (1 << 5) else None
        bot_payload = Bytes.read(b) if flags & (1 << 7) else None
        msg_id = Int.read(b) if flags & (1 << 8) else None
        extended_media = TLObject.read(b) if flags & (1 << 9) else []
        
        subscription_period = Int.read(b) if flags & (1 << 12) else None
        giveaway_post_id = Int.read(b) if flags & (1 << 13) else None
        stargift = TLObject.read(b) if flags & (1 << 14) else None
        
        floodskip_number = Int.read(b) if flags & (1 << 15) else None
        starref_commission_permille = Int.read(b) if flags & (1 << 16) else None
        starref_peer = TLObject.read(b) if flags & (1 << 17) else None
        
        starref_amount = TLObject.read(b) if flags & (1 << 17) else None
        
        paid_messages = Int.read(b) if flags & (1 << 19) else None
        premium_gift_months = Int.read(b) if flags & (1 << 20) else None
        ads_proceeds_from_date = Int.read(b) if flags & (1 << 23) else None
        ads_proceeds_to_date = Int.read(b) if flags & (1 << 23) else None
        return StarsTransaction(id=id, amount=amount, date=date, peer=peer, refund=refund, pending=pending, failed=failed, gift=gift, reaction=reaction, subscription=subscription, stargift_upgrade=stargift_upgrade, floodskip=floodskip, business_transfer=business_transfer, stargift_resale=stargift_resale, paid_message=paid_message, posts_search=posts_search, premium_gift=premium_gift, stargift_prepaid_upgrade=stargift_prepaid_upgrade, stargift_drop_original_details=stargift_drop_original_details, title=title, description=description, photo=photo, transaction_date=transaction_date, transaction_url=transaction_url, bot_payload=bot_payload, msg_id=msg_id, extended_media=extended_media, subscription_period=subscription_period, giveaway_post_id=giveaway_post_id, stargift=stargift, floodskip_number=floodskip_number, starref_commission_permille=starref_commission_permille, starref_peer=starref_peer, starref_amount=starref_amount, paid_messages=paid_messages, premium_gift_months=premium_gift_months, ads_proceeds_from_date=ads_proceeds_from_date, ads_proceeds_to_date=ads_proceeds_to_date)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        flags = 0
        flags |= (1 << 3) if self.refund else 0
        flags |= (1 << 4) if self.pending else 0
        flags |= (1 << 6) if self.failed else 0
        flags |= (1 << 10) if self.gift else 0
        flags |= (1 << 11) if self.reaction else 0
        flags |= (1 << 12) if self.subscription else 0
        flags |= (1 << 18) if self.stargift_upgrade else 0
        flags |= (1 << 15) if self.floodskip else 0
        flags |= (1 << 21) if self.business_transfer else 0
        flags |= (1 << 22) if self.stargift_resale else 0
        flags |= (1 << 19) if self.paid_message else 0
        flags |= (1 << 24) if self.posts_search else 0
        flags |= (1 << 20) if self.premium_gift else 0
        flags |= (1 << 25) if self.stargift_prepaid_upgrade else 0
        flags |= (1 << 26) if self.stargift_drop_original_details else 0
        flags |= (1 << 0) if self.title is not None else 0
        flags |= (1 << 1) if self.description is not None else 0
        flags |= (1 << 2) if self.photo is not None else 0
        flags |= (1 << 5) if self.transaction_date is not None else 0
        flags |= (1 << 5) if self.transaction_url is not None else 0
        flags |= (1 << 7) if self.bot_payload is not None else 0
        flags |= (1 << 8) if self.msg_id is not None else 0
        flags |= (1 << 9) if self.extended_media else 0
        flags |= (1 << 12) if self.subscription_period is not None else 0
        flags |= (1 << 13) if self.giveaway_post_id is not None else 0
        flags |= (1 << 14) if self.stargift is not None else 0
        flags |= (1 << 15) if self.floodskip_number is not None else 0
        flags |= (1 << 16) if self.starref_commission_permille is not None else 0
        flags |= (1 << 17) if self.starref_peer is not None else 0
        flags |= (1 << 17) if self.starref_amount is not None else 0
        flags |= (1 << 19) if self.paid_messages is not None else 0
        flags |= (1 << 20) if self.premium_gift_months is not None else 0
        flags |= (1 << 23) if self.ads_proceeds_from_date is not None else 0
        flags |= (1 << 23) if self.ads_proceeds_to_date is not None else 0
        b.write(Int(flags))
        
        b.write(String(self.id))
        
        b.write(self.amount.write())
        
        b.write(Int(self.date))
        
        b.write(self.peer.write())
        
        if self.title is not None:
            b.write(String(self.title))
        
        if self.description is not None:
            b.write(String(self.description))
        
        if self.photo is not None:
            b.write(self.photo.write())
        
        if self.transaction_date is not None:
            b.write(Int(self.transaction_date))
        
        if self.transaction_url is not None:
            b.write(String(self.transaction_url))
        
        if self.bot_payload is not None:
            b.write(Bytes(self.bot_payload))
        
        if self.msg_id is not None:
            b.write(Int(self.msg_id))
        
        if self.extended_media is not None:
            b.write(Vector(self.extended_media))
        
        if self.subscription_period is not None:
            b.write(Int(self.subscription_period))
        
        if self.giveaway_post_id is not None:
            b.write(Int(self.giveaway_post_id))
        
        if self.stargift is not None:
            b.write(self.stargift.write())
        
        if self.floodskip_number is not None:
            b.write(Int(self.floodskip_number))
        
        if self.starref_commission_permille is not None:
            b.write(Int(self.starref_commission_permille))
        
        if self.starref_peer is not None:
            b.write(self.starref_peer.write())
        
        if self.starref_amount is not None:
            b.write(self.starref_amount.write())
        
        if self.paid_messages is not None:
            b.write(Int(self.paid_messages))
        
        if self.premium_gift_months is not None:
            b.write(Int(self.premium_gift_months))
        
        if self.ads_proceeds_from_date is not None:
            b.write(Int(self.ads_proceeds_from_date))
        
        if self.ads_proceeds_to_date is not None:
            b.write(Int(self.ads_proceeds_to_date))
        
        return b.getvalue()
