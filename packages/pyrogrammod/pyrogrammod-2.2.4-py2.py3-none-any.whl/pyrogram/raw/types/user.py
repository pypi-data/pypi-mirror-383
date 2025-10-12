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


class User(TLObject):  # type: ignore
    """Indicates info about a certain user.

    Constructor of :obj:`~pyrogram.raw.base.User`.

    Details:
        - Layer: ``216``
        - ID: ``20B1422``

    Parameters:
        id (``int`` ``64-bit``):
            ID of the user, see here » for more info and the available ID range.

        is_self (``bool``, *optional*):
            N/A

        contact (``bool``, *optional*):
            Whether this user is a contact When updating the local peer database, do not apply changes to this field if the min flag is set.

        mutual_contact (``bool``, *optional*):
            Whether this user is a mutual contact. When updating the local peer database, do not apply changes to this field if the min flag is set.

        deleted (``bool``, *optional*):
            Whether the account of this user was deleted. Changes to this flag should invalidate the local userFull cache for this user ID, see here » for more info.

        bot (``bool``, *optional*):
            Is this user a bot? Changes to this flag should invalidate the local userFull cache for this user ID, see here » for more info.

        bot_chat_history (``bool``, *optional*):
            Can the bot see all messages in groups?

        bot_nochats (``bool``, *optional*):
            Can the bot be added to groups?

        verified (``bool``, *optional*):
            Whether this user is verified

        restricted (``bool``, *optional*):
            Access to this user must be restricted for the reason specified in restriction_reason

        min (``bool``, *optional*):
            See min

        bot_inline_geo (``bool``, *optional*):
            Whether the bot can request our geolocation in inline mode

        support (``bool``, *optional*):
            Whether this is an official support user

        scam (``bool``, *optional*):
            This may be a scam user

        apply_min_photo (``bool``, *optional*):
            If set and min is set, the value of photo can be used to update the local database, see the documentation of that flag for more info.

        fake (``bool``, *optional*):
            If set, this user was reported by many users as a fake or scam user: be careful when interacting with them.

        bot_attach_menu (``bool``, *optional*):
            Whether this bot offers an attachment menu web app

        premium (``bool``, *optional*):
            Whether this user is a Telegram Premium user Changes to this flag should invalidate the local userFull cache for this user ID, see here » for more info. Changes to this flag if the self flag is set should also trigger the following calls, to refresh the respective caches: - The help.getConfig cache - The messages.getTopReactions cache if the bot flag is not set

        attach_menu_enabled (``bool``, *optional*):
            Whether we installed the attachment menu web app offered by this bot. When updating the local peer database, do not apply changes to this field if the min flag is set.

        bot_can_edit (``bool``, *optional*):
            Whether we can edit the profile picture, name, about text and description of this bot because we own it. When updating the local peer database, do not apply changes to this field if the min flag is set. Changes to this flag (if min is not set) should invalidate the local userFull cache for this user ID.

        close_friend (``bool``, *optional*):
            Whether we marked this user as a close friend, see here » for more info. When updating the local peer database, do not apply changes to this field if the min flag is set.

        stories_hidden (``bool``, *optional*):
            Whether we have hidden » all active stories of this user. When updating the local peer database, do not apply changes to this field if the min flag is set.

        stories_unavailable (``bool``, *optional*):
            No stories from this user are visible.

        contact_require_premium (``bool``, *optional*):
            See here for more info on this flag ».

        bot_business (``bool``, *optional*):
            Whether this bot can be connected to a user as specified here ».

        bot_has_main_app (``bool``, *optional*):
            If set, this bot has configured a Main Mini App ».

        bot_forum_view (``bool``, *optional*):
            N/A

        access_hash (``int`` ``64-bit``, *optional*):
            Access hash of the user, see here » for more info. If this flag is set, when updating the local peer database, generate a virtual flag called min_access_hash, which is: - Set to true if min is set AND -- The phone flag is not set OR -- The phone flag is set and the associated phone number string is non-empty - Set to false otherwise. Then, apply both access_hash and min_access_hash to the local database if: - min_access_hash is false OR - min_access_hash is true AND -- There is no locally cached object for this user OR -- There is no access_hash in the local cache OR -- The cached object's min_access_hash is also true If the final merged object stored to the database has the min_access_hash field set to true, the related access_hash is only suitable to use in inputPeerPhotoFileLocation », to directly download the profile pictures of users, everywhere else a inputPeer*FromMessage constructor will have to be generated as specified here ». Bots can also use min access hashes in some conditions, by passing 0 instead of the min access hash.

        first_name (``str``, *optional*):
            First name. When updating the local peer database, apply changes to this field only if: - The min flag is not set OR - The min flag is set AND -- The min flag of the locally cached user entry is set.

        last_name (``str``, *optional*):
            Last name. When updating the local peer database, apply changes to this field only if: - The min flag is not set OR - The min flag is set AND -- The min flag of the locally cached user entry is set.

        username (``str``, *optional*):
            Main active username. When updating the local peer database, apply changes to this field only if: - The min flag is not set OR - The min flag is set AND -- The min flag of the locally cached user entry is set. Changes to this flag should invalidate the local userFull cache for this user ID if the above conditions are respected and the bot_can_edit flag is also set.

        phone (``str``, *optional*):
            Phone number. When updating the local peer database, apply changes to this field only if: - The min flag is not set OR - The min flag is set AND -- The min flag of the locally cached user entry is set.

        photo (:obj:`UserProfilePhoto <pyrogram.raw.base.UserProfilePhoto>`, *optional*):
            Profile picture of user. When updating the local peer database, apply changes to this field only if: - The min flag is not set OR - The min flag is set AND -- The apply_min_photo flag is set OR -- The min flag of the locally cached user entry is set.

        status (:obj:`UserStatus <pyrogram.raw.base.UserStatus>`, *optional*):
            Online status of user. When updating the local peer database, apply changes to this field only if: - The min flag is not set OR - The min flag is set AND -- The min flag of the locally cached user entry is set OR -- The locally cached user entry is equal to userStatusEmpty.

        bot_info_version (``int`` ``32-bit``, *optional*):
            Version of the bot_info field in userFull, incremented every time it changes. Changes to this flag should invalidate the local userFull cache for this user ID, see here » for more info.

        restriction_reason (List of :obj:`RestrictionReason <pyrogram.raw.base.RestrictionReason>`, *optional*):
            Contains the reason why access to this user must be restricted.

        bot_inline_placeholder (``str``, *optional*):
            Inline placeholder for this inline bot

        lang_code (``str``, *optional*):
            Language code of the user

        emoji_status (:obj:`EmojiStatus <pyrogram.raw.base.EmojiStatus>`, *optional*):
            Emoji status

        usernames (List of :obj:`Username <pyrogram.raw.base.Username>`, *optional*):
            Additional usernames. When updating the local peer database, apply changes to this field only if: - The min flag is not set OR - The min flag is set AND -- The min flag of the locally cached user entry is set. Changes to this flag (if the above conditions are respected) should invalidate the local userFull cache for this user ID.

        stories_max_id (``int`` ``32-bit``, *optional*):
            ID of the maximum read story.  When updating the local peer database, do not apply changes to this field if the min flag of the incoming constructor is set.

        color (:obj:`PeerColor <pyrogram.raw.base.PeerColor>`, *optional*):
            The user's accent color.

        profile_color (:obj:`PeerColor <pyrogram.raw.base.PeerColor>`, *optional*):
            The user's profile color.

        bot_active_users (``int`` ``32-bit``, *optional*):
            Monthly Active Users (MAU) of this bot (may be absent for small bots).

        bot_verification_icon (``int`` ``64-bit``, *optional*):
            Describes a bot verification icon ».

        send_paid_messages_stars (``int`` ``64-bit``, *optional*):
            If set, the user has enabled paid messages », we might need to pay the specified amount of Stars to send them messages, depending on the configured exceptions: check userFull.send_paid_messages_stars or users.getRequirementsToContact to see if the currently logged in user actually has to pay or not, see here » for the full flow.

    Functions:
        This object can be returned by 8 functions.

        .. currentmodule:: pyrogram.raw.functions

        .. autosummary::
            :nosignatures:

            account.UpdateProfile
            account.UpdateUsername
            account.ChangePhone
            users.GetUsers
            contacts.ImportContactToken
            contacts.ImportCard
            channels.GetMessageAuthor
            bots.GetAdminedBots
    """

    __slots__: List[str] = ["id", "is_self", "contact", "mutual_contact", "deleted", "bot", "bot_chat_history", "bot_nochats", "verified", "restricted", "min", "bot_inline_geo", "support", "scam", "apply_min_photo", "fake", "bot_attach_menu", "premium", "attach_menu_enabled", "bot_can_edit", "close_friend", "stories_hidden", "stories_unavailable", "contact_require_premium", "bot_business", "bot_has_main_app", "bot_forum_view", "access_hash", "first_name", "last_name", "username", "phone", "photo", "status", "bot_info_version", "restriction_reason", "bot_inline_placeholder", "lang_code", "emoji_status", "usernames", "stories_max_id", "color", "profile_color", "bot_active_users", "bot_verification_icon", "send_paid_messages_stars"]

    ID = 0x20b1422
    QUALNAME = "types.User"

    def __init__(self, *, id: int, is_self: Optional[bool] = None, contact: Optional[bool] = None, mutual_contact: Optional[bool] = None, deleted: Optional[bool] = None, bot: Optional[bool] = None, bot_chat_history: Optional[bool] = None, bot_nochats: Optional[bool] = None, verified: Optional[bool] = None, restricted: Optional[bool] = None, min: Optional[bool] = None, bot_inline_geo: Optional[bool] = None, support: Optional[bool] = None, scam: Optional[bool] = None, apply_min_photo: Optional[bool] = None, fake: Optional[bool] = None, bot_attach_menu: Optional[bool] = None, premium: Optional[bool] = None, attach_menu_enabled: Optional[bool] = None, bot_can_edit: Optional[bool] = None, close_friend: Optional[bool] = None, stories_hidden: Optional[bool] = None, stories_unavailable: Optional[bool] = None, contact_require_premium: Optional[bool] = None, bot_business: Optional[bool] = None, bot_has_main_app: Optional[bool] = None, bot_forum_view: Optional[bool] = None, access_hash: Optional[int] = None, first_name: Optional[str] = None, last_name: Optional[str] = None, username: Optional[str] = None, phone: Optional[str] = None, photo: "raw.base.UserProfilePhoto" = None, status: "raw.base.UserStatus" = None, bot_info_version: Optional[int] = None, restriction_reason: Optional[List["raw.base.RestrictionReason"]] = None, bot_inline_placeholder: Optional[str] = None, lang_code: Optional[str] = None, emoji_status: "raw.base.EmojiStatus" = None, usernames: Optional[List["raw.base.Username"]] = None, stories_max_id: Optional[int] = None, color: "raw.base.PeerColor" = None, profile_color: "raw.base.PeerColor" = None, bot_active_users: Optional[int] = None, bot_verification_icon: Optional[int] = None, send_paid_messages_stars: Optional[int] = None) -> None:
        self.id = id  # long
        self.is_self = is_self  # flags.10?true
        self.contact = contact  # flags.11?true
        self.mutual_contact = mutual_contact  # flags.12?true
        self.deleted = deleted  # flags.13?true
        self.bot = bot  # flags.14?true
        self.bot_chat_history = bot_chat_history  # flags.15?true
        self.bot_nochats = bot_nochats  # flags.16?true
        self.verified = verified  # flags.17?true
        self.restricted = restricted  # flags.18?true
        self.min = min  # flags.20?true
        self.bot_inline_geo = bot_inline_geo  # flags.21?true
        self.support = support  # flags.23?true
        self.scam = scam  # flags.24?true
        self.apply_min_photo = apply_min_photo  # flags.25?true
        self.fake = fake  # flags.26?true
        self.bot_attach_menu = bot_attach_menu  # flags.27?true
        self.premium = premium  # flags.28?true
        self.attach_menu_enabled = attach_menu_enabled  # flags.29?true
        self.bot_can_edit = bot_can_edit  # flags2.1?true
        self.close_friend = close_friend  # flags2.2?true
        self.stories_hidden = stories_hidden  # flags2.3?true
        self.stories_unavailable = stories_unavailable  # flags2.4?true
        self.contact_require_premium = contact_require_premium  # flags2.10?true
        self.bot_business = bot_business  # flags2.11?true
        self.bot_has_main_app = bot_has_main_app  # flags2.13?true
        self.bot_forum_view = bot_forum_view  # flags2.16?true
        self.access_hash = access_hash  # flags.0?long
        self.first_name = first_name  # flags.1?string
        self.last_name = last_name  # flags.2?string
        self.username = username  # flags.3?string
        self.phone = phone  # flags.4?string
        self.photo = photo  # flags.5?UserProfilePhoto
        self.status = status  # flags.6?UserStatus
        self.bot_info_version = bot_info_version  # flags.14?int
        self.restriction_reason = restriction_reason  # flags.18?Vector<RestrictionReason>
        self.bot_inline_placeholder = bot_inline_placeholder  # flags.19?string
        self.lang_code = lang_code  # flags.22?string
        self.emoji_status = emoji_status  # flags.30?EmojiStatus
        self.usernames = usernames  # flags2.0?Vector<Username>
        self.stories_max_id = stories_max_id  # flags2.5?int
        self.color = color  # flags2.8?PeerColor
        self.profile_color = profile_color  # flags2.9?PeerColor
        self.bot_active_users = bot_active_users  # flags2.12?int
        self.bot_verification_icon = bot_verification_icon  # flags2.14?long
        self.send_paid_messages_stars = send_paid_messages_stars  # flags2.15?long

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "User":
        
        flags = Int.read(b)
        
        is_self = True if flags & (1 << 10) else False
        contact = True if flags & (1 << 11) else False
        mutual_contact = True if flags & (1 << 12) else False
        deleted = True if flags & (1 << 13) else False
        bot = True if flags & (1 << 14) else False
        bot_chat_history = True if flags & (1 << 15) else False
        bot_nochats = True if flags & (1 << 16) else False
        verified = True if flags & (1 << 17) else False
        restricted = True if flags & (1 << 18) else False
        min = True if flags & (1 << 20) else False
        bot_inline_geo = True if flags & (1 << 21) else False
        support = True if flags & (1 << 23) else False
        scam = True if flags & (1 << 24) else False
        apply_min_photo = True if flags & (1 << 25) else False
        fake = True if flags & (1 << 26) else False
        bot_attach_menu = True if flags & (1 << 27) else False
        premium = True if flags & (1 << 28) else False
        attach_menu_enabled = True if flags & (1 << 29) else False
        flags2 = Int.read(b)
        
        bot_can_edit = True if flags2 & (1 << 1) else False
        close_friend = True if flags2 & (1 << 2) else False
        stories_hidden = True if flags2 & (1 << 3) else False
        stories_unavailable = True if flags2 & (1 << 4) else False
        contact_require_premium = True if flags2 & (1 << 10) else False
        bot_business = True if flags2 & (1 << 11) else False
        bot_has_main_app = True if flags2 & (1 << 13) else False
        bot_forum_view = True if flags2 & (1 << 16) else False
        id = Long.read(b)
        
        access_hash = Long.read(b) if flags & (1 << 0) else None
        first_name = String.read(b) if flags & (1 << 1) else None
        last_name = String.read(b) if flags & (1 << 2) else None
        username = String.read(b) if flags & (1 << 3) else None
        phone = String.read(b) if flags & (1 << 4) else None
        photo = TLObject.read(b) if flags & (1 << 5) else None
        
        status = TLObject.read(b) if flags & (1 << 6) else None
        
        bot_info_version = Int.read(b) if flags & (1 << 14) else None
        restriction_reason = TLObject.read(b) if flags & (1 << 18) else []
        
        bot_inline_placeholder = String.read(b) if flags & (1 << 19) else None
        lang_code = String.read(b) if flags & (1 << 22) else None
        emoji_status = TLObject.read(b) if flags & (1 << 30) else None
        
        usernames = TLObject.read(b) if flags2 & (1 << 0) else []
        
        stories_max_id = Int.read(b) if flags2 & (1 << 5) else None
        color = TLObject.read(b) if flags2 & (1 << 8) else None
        
        profile_color = TLObject.read(b) if flags2 & (1 << 9) else None
        
        bot_active_users = Int.read(b) if flags2 & (1 << 12) else None
        bot_verification_icon = Long.read(b) if flags2 & (1 << 14) else None
        send_paid_messages_stars = Long.read(b) if flags2 & (1 << 15) else None
        return User(id=id, is_self=is_self, contact=contact, mutual_contact=mutual_contact, deleted=deleted, bot=bot, bot_chat_history=bot_chat_history, bot_nochats=bot_nochats, verified=verified, restricted=restricted, min=min, bot_inline_geo=bot_inline_geo, support=support, scam=scam, apply_min_photo=apply_min_photo, fake=fake, bot_attach_menu=bot_attach_menu, premium=premium, attach_menu_enabled=attach_menu_enabled, bot_can_edit=bot_can_edit, close_friend=close_friend, stories_hidden=stories_hidden, stories_unavailable=stories_unavailable, contact_require_premium=contact_require_premium, bot_business=bot_business, bot_has_main_app=bot_has_main_app, bot_forum_view=bot_forum_view, access_hash=access_hash, first_name=first_name, last_name=last_name, username=username, phone=phone, photo=photo, status=status, bot_info_version=bot_info_version, restriction_reason=restriction_reason, bot_inline_placeholder=bot_inline_placeholder, lang_code=lang_code, emoji_status=emoji_status, usernames=usernames, stories_max_id=stories_max_id, color=color, profile_color=profile_color, bot_active_users=bot_active_users, bot_verification_icon=bot_verification_icon, send_paid_messages_stars=send_paid_messages_stars)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        flags = 0
        flags |= (1 << 10) if self.is_self else 0
        flags |= (1 << 11) if self.contact else 0
        flags |= (1 << 12) if self.mutual_contact else 0
        flags |= (1 << 13) if self.deleted else 0
        flags |= (1 << 14) if self.bot else 0
        flags |= (1 << 15) if self.bot_chat_history else 0
        flags |= (1 << 16) if self.bot_nochats else 0
        flags |= (1 << 17) if self.verified else 0
        flags |= (1 << 18) if self.restricted else 0
        flags |= (1 << 20) if self.min else 0
        flags |= (1 << 21) if self.bot_inline_geo else 0
        flags |= (1 << 23) if self.support else 0
        flags |= (1 << 24) if self.scam else 0
        flags |= (1 << 25) if self.apply_min_photo else 0
        flags |= (1 << 26) if self.fake else 0
        flags |= (1 << 27) if self.bot_attach_menu else 0
        flags |= (1 << 28) if self.premium else 0
        flags |= (1 << 29) if self.attach_menu_enabled else 0
        flags |= (1 << 0) if self.access_hash is not None else 0
        flags |= (1 << 1) if self.first_name is not None else 0
        flags |= (1 << 2) if self.last_name is not None else 0
        flags |= (1 << 3) if self.username is not None else 0
        flags |= (1 << 4) if self.phone is not None else 0
        flags |= (1 << 5) if self.photo is not None else 0
        flags |= (1 << 6) if self.status is not None else 0
        flags |= (1 << 14) if self.bot_info_version is not None else 0
        flags |= (1 << 18) if self.restriction_reason else 0
        flags |= (1 << 19) if self.bot_inline_placeholder is not None else 0
        flags |= (1 << 22) if self.lang_code is not None else 0
        flags |= (1 << 30) if self.emoji_status is not None else 0
        b.write(Int(flags))
        flags2 = 0
        flags2 |= (1 << 1) if self.bot_can_edit else 0
        flags2 |= (1 << 2) if self.close_friend else 0
        flags2 |= (1 << 3) if self.stories_hidden else 0
        flags2 |= (1 << 4) if self.stories_unavailable else 0
        flags2 |= (1 << 10) if self.contact_require_premium else 0
        flags2 |= (1 << 11) if self.bot_business else 0
        flags2 |= (1 << 13) if self.bot_has_main_app else 0
        flags2 |= (1 << 16) if self.bot_forum_view else 0
        flags2 |= (1 << 0) if self.usernames else 0
        flags2 |= (1 << 5) if self.stories_max_id is not None else 0
        flags2 |= (1 << 8) if self.color is not None else 0
        flags2 |= (1 << 9) if self.profile_color is not None else 0
        flags2 |= (1 << 12) if self.bot_active_users is not None else 0
        flags2 |= (1 << 14) if self.bot_verification_icon is not None else 0
        flags2 |= (1 << 15) if self.send_paid_messages_stars is not None else 0
        b.write(Int(flags2))
        
        b.write(Long(self.id))
        
        if self.access_hash is not None:
            b.write(Long(self.access_hash))
        
        if self.first_name is not None:
            b.write(String(self.first_name))
        
        if self.last_name is not None:
            b.write(String(self.last_name))
        
        if self.username is not None:
            b.write(String(self.username))
        
        if self.phone is not None:
            b.write(String(self.phone))
        
        if self.photo is not None:
            b.write(self.photo.write())
        
        if self.status is not None:
            b.write(self.status.write())
        
        if self.bot_info_version is not None:
            b.write(Int(self.bot_info_version))
        
        if self.restriction_reason is not None:
            b.write(Vector(self.restriction_reason))
        
        if self.bot_inline_placeholder is not None:
            b.write(String(self.bot_inline_placeholder))
        
        if self.lang_code is not None:
            b.write(String(self.lang_code))
        
        if self.emoji_status is not None:
            b.write(self.emoji_status.write())
        
        if self.usernames is not None:
            b.write(Vector(self.usernames))
        
        if self.stories_max_id is not None:
            b.write(Int(self.stories_max_id))
        
        if self.color is not None:
            b.write(self.color.write())
        
        if self.profile_color is not None:
            b.write(self.profile_color.write())
        
        if self.bot_active_users is not None:
            b.write(Int(self.bot_active_users))
        
        if self.bot_verification_icon is not None:
            b.write(Long(self.bot_verification_icon))
        
        if self.send_paid_messages_stars is not None:
            b.write(Long(self.send_paid_messages_stars))
        
        return b.getvalue()
