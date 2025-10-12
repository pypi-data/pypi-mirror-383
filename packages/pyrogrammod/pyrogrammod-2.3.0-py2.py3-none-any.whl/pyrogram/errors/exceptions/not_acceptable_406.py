# Pyrogram - Telegram MTProto API Client Library for Python
# Copyright (C) 2017-present Dan <https://github.com/delivrance>
#
# This file is part of Pyrogram.
#
# Pyrogram is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Pyrogram is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with Pyrogram.  If not, see <http://www.gnu.org/licenses/>.

from ..rpc_error import RPCError


class NotAcceptable(RPCError):
    """Not Acceptable"""
    CODE = 406
    """``int``: RPC Error Code"""
    NAME = __doc__


class TwoFaConfirmWait(NotAcceptable):
    """Since this account is active and protected by a 2FA password, we will delete it in 1 week for security purposes. You can cancel this process at any time, you'll be able to reset your account in {value} seconds."""
    ID = "2FA_CONFIRM_WAIT_X"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class AboutTooLong(NotAcceptable):
    """About string too long."""
    ID = "ABOUT_TOO_LONG"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class AccessTokenExpired(NotAcceptable):
    """Access token expired."""
    ID = "ACCESS_TOKEN_EXPIRED"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class AccessTokenInvalid(NotAcceptable):
    """Access token invalid."""
    ID = "ACCESS_TOKEN_INVALID"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class AddressInvalid(NotAcceptable):
    """The specified geopoint address is invalid."""
    ID = "ADDRESS_INVALID"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class AdminsTooMuch(NotAcceptable):
    """There are too many admins."""
    ID = "ADMINS_TOO_MUCH"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class AdminIdInvalid(NotAcceptable):
    """The specified admin ID is invalid."""
    ID = "ADMIN_ID_INVALID"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class AdminRankEmojiNotAllowed(NotAcceptable):
    """An admin rank cannot contain emojis."""
    ID = "ADMIN_RANK_EMOJI_NOT_ALLOWED"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class AdminRankInvalid(NotAcceptable):
    """The specified admin rank is invalid."""
    ID = "ADMIN_RANK_INVALID"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class AdminRightsEmpty(NotAcceptable):
    """The chatAdminRights constructor passed in keyboardButtonRequestPeer.peer_type.user_admin_rights has no rights set (i.e. flags is 0)."""
    ID = "ADMIN_RIGHTS_EMPTY"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class AlbumPhotosTooMany(NotAcceptable):
    """You have uploaded too many profile photos, delete some before retrying."""
    ID = "ALBUM_PHOTOS_TOO_MANY"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class AllowPaymentRequired(NotAcceptable):
    """This peer only accepts [paid messages &raquo;](https://core.telegram.org/api/paid-messages): this error is only emitted for older layers without paid messages support, so the client must be updated in order to use paid messages.  ."""
    ID = "ALLOW_PAYMENT_REQUIRED"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class AnonymousReactionsDisabled(NotAcceptable):
    """Sorry, anonymous administrators cannot leave reactions or participate in polls."""
    ID = "ANONYMOUS_REACTIONS_DISABLED"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class ApiGiftRestrictedUpdateApp(NotAcceptable):
    """Please update the app to access the gift API."""
    ID = "API_GIFT_RESTRICTED_UPDATE_APP"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class ApiIdInvalid(NotAcceptable):
    """API ID invalid."""
    ID = "API_ID_INVALID"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class ApiIdPublishedFlood(NotAcceptable):
    """This API id was published somewhere, you can't use it now."""
    ID = "API_ID_PUBLISHED_FLOOD"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class ArticleTitleEmpty(NotAcceptable):
    """The title of the article is empty."""
    ID = "ARTICLE_TITLE_EMPTY"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class AudioContentUrlEmpty(NotAcceptable):
    """The remote URL specified in the content field is empty."""
    ID = "AUDIO_CONTENT_URL_EMPTY"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class AudioTitleEmpty(NotAcceptable):
    """An empty audio title was provided."""
    ID = "AUDIO_TITLE_EMPTY"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class AuthBytesInvalid(NotAcceptable):
    """The provided authorization is invalid."""
    ID = "AUTH_BYTES_INVALID"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class AuthKeyDuplicated(NotAcceptable):
    """Concurrent usage of the current session from multiple connections was detected, the current session was invalidated by the server for security reasons!"""
    ID = "AUTH_KEY_DUPLICATED"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class AuthRestart(NotAcceptable):
    """Restart the authorization process."""
    ID = "AUTH_RESTART"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class AuthTokenAlreadyAccepted(NotAcceptable):
    """The specified auth token was already accepted."""
    ID = "AUTH_TOKEN_ALREADY_ACCEPTED"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class AuthTokenException(NotAcceptable):
    """An error occurred while importing the auth token."""
    ID = "AUTH_TOKEN_EXCEPTION"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class AuthTokenExpired(NotAcceptable):
    """The authorization token has expired."""
    ID = "AUTH_TOKEN_EXPIRED"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class AuthTokenInvalid(NotAcceptable):
    """The specified auth token is invalid."""
    ID = "AUTH_TOKEN_INVALID"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class AuthTokenInvalidx(NotAcceptable):
    """The specified auth token is invalid."""
    ID = "AUTH_TOKEN_INVALIDX"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class AutoarchiveNotAvailable(NotAcceptable):
    """The autoarchive setting is not available at this time: please check the value of the [autoarchive_setting_available field in client config &raquo;](https://core.telegram.org/api/config#client-configuration) before calling this method."""
    ID = "AUTOARCHIVE_NOT_AVAILABLE"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class BankCardNumberInvalid(NotAcceptable):
    """The specified card number is invalid."""
    ID = "BANK_CARD_NUMBER_INVALID"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class BannedRightsInvalid(NotAcceptable):
    """You provided some invalid flags in the banned rights."""
    ID = "BANNED_RIGHTS_INVALID"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class BoostsEmpty(NotAcceptable):
    """No boost slots were specified."""
    ID = "BOOSTS_EMPTY"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class BoostsRequired(NotAcceptable):
    """The specified channel must first be [boosted by its users](https://core.telegram.org/api/boost) in order to perform this action."""
    ID = "BOOSTS_REQUIRED"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class BoostNotModified(NotAcceptable):
    """You're already [boosting](https://core.telegram.org/api/boost) the specified channel."""
    ID = "BOOST_NOT_MODIFIED"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class BoostPeerInvalid(NotAcceptable):
    """The specified `boost_peer` is invalid."""
    ID = "BOOST_PEER_INVALID"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class BotsTooMuch(NotAcceptable):
    """There are too many bots in this chat/channel."""
    ID = "BOTS_TOO_MUCH"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class BotAppInvalid(NotAcceptable):
    """The specified bot app is invalid."""
    ID = "BOT_APP_INVALID"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class BotAppShortnameInvalid(NotAcceptable):
    """The specified bot app short name is invalid."""
    ID = "BOT_APP_SHORTNAME_INVALID"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class BotChannelsNa(NotAcceptable):
    """Bots can't edit admin privileges."""
    ID = "BOT_CHANNELS_NA"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class BotCommandDescriptionInvalid(NotAcceptable):
    """The specified command description is invalid."""
    ID = "BOT_COMMAND_DESCRIPTION_INVALID"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class BotCommandInvalid(NotAcceptable):
    """The specified command is invalid."""
    ID = "BOT_COMMAND_INVALID"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class BotDomainInvalid(NotAcceptable):
    """Bot domain invalid."""
    ID = "BOT_DOMAIN_INVALID"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class BotGroupsBlocked(NotAcceptable):
    """This bot can't be added to groups."""
    ID = "BOT_GROUPS_BLOCKED"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class BotInlineDisabled(NotAcceptable):
    """This bot can't be used in inline mode."""
    ID = "BOT_INLINE_DISABLED"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class BotInvalid(NotAcceptable):
    """This is not a valid bot."""
    ID = "BOT_INVALID"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class BotMissing(NotAcceptable):
    """Only bots can call this method, please use [@stickers](https://t.me/stickers) if you're a user."""
    ID = "BOT_MISSING"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class BotOnesideNotAvail(NotAcceptable):
    """Bots can't pin messages in PM just for themselves."""
    ID = "BOT_ONESIDE_NOT_AVAIL"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class BotPaymentsDisabled(NotAcceptable):
    """Please enable bot payments in botfather before calling this method."""
    ID = "BOT_PAYMENTS_DISABLED"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class BotResponseTimeout(NotAcceptable):
    """A timeout occurred while fetching data from the bot."""
    ID = "BOT_RESPONSE_TIMEOUT"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class BotScoreNotModified(NotAcceptable):
    """The score wasn't modified."""
    ID = "BOT_SCORE_NOT_MODIFIED"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class BotWebviewDisabled(NotAcceptable):
    """A webview cannot be opened in the specified conditions: emitted for example if `from_bot_menu` or `url` are set and `peer` is not the chat with the bot."""
    ID = "BOT_WEBVIEW_DISABLED"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class BroadcastForbidden(NotAcceptable):
    """Channel poll voters and reactions cannot be fetched to prevent deanonymization."""
    ID = "BROADCAST_FORBIDDEN"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class BroadcastIdInvalid(NotAcceptable):
    """Broadcast ID invalid."""
    ID = "BROADCAST_ID_INVALID"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class BroadcastPublicVotersForbidden(NotAcceptable):
    """You can't forward polls with public voters."""
    ID = "BROADCAST_PUBLIC_VOTERS_FORBIDDEN"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class BroadcastRequired(NotAcceptable):
    """This method can only be called on a channel, please use stats.getMegagroupStats for supergroups."""
    ID = "BROADCAST_REQUIRED"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class BusinessAddressActive(NotAcceptable):
    """The user is currently advertising a [Business Location](https://core.telegram.org/api/business#location), the location may only be changed (or removed) using [account.updateBusinessLocation &raquo;](https://core.telegram.org/method/account.updateBusinessLocation).  ."""
    ID = "BUSINESS_ADDRESS_ACTIVE"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class ButtonDataInvalid(NotAcceptable):
    """The data of one or more of the buttons you provided is invalid."""
    ID = "BUTTON_DATA_INVALID"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class ButtonTextInvalid(NotAcceptable):
    """The specified button text is invalid."""
    ID = "BUTTON_TEXT_INVALID"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class ButtonTypeInvalid(NotAcceptable):
    """The type of one or more of the buttons you provided is invalid."""
    ID = "BUTTON_TYPE_INVALID"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class ButtonUrlInvalid(NotAcceptable):
    """Button URL invalid."""
    ID = "BUTTON_URL_INVALID"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class ButtonUserPrivacyRestricted(NotAcceptable):
    """The privacy setting of the user specified in a [inputKeyboardButtonUserProfile](/constructor/inputKeyboardButtonUserProfile) button do not allow creating such a button."""
    ID = "BUTTON_USER_PRIVACY_RESTRICTED"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class CallAlreadyAccepted(NotAcceptable):
    """The call was already accepted."""
    ID = "CALL_ALREADY_ACCEPTED"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class CallAlreadyDeclined(NotAcceptable):
    """The call was already declined."""
    ID = "CALL_ALREADY_DECLINED"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class CallOccupyFailed(NotAcceptable):
    """The call failed because the user is already making another call."""
    ID = "CALL_OCCUPY_FAILED"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class CallPeerInvalid(NotAcceptable):
    """The provided call peer object is invalid."""
    ID = "CALL_PEER_INVALID"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class CallProtocolCompatLayerInvalid(NotAcceptable):
    """The other side of the call does not support any of the VoIP protocols supported by the local client, as specified by the `protocol.layer` and `protocol.library_versions` fields."""
    ID = "CALL_PROTOCOL_COMPAT_LAYER_INVALID"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class CallProtocolFlagsInvalid(NotAcceptable):
    """Call protocol flags invalid."""
    ID = "CALL_PROTOCOL_FLAGS_INVALID"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class CdnMethodInvalid(NotAcceptable):
    """You can't call this method in a CDN DC."""
    ID = "CDN_METHOD_INVALID"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class CdnUploadTimeout(NotAcceptable):
    """A server-side timeout occurred while reuploading the file to the CDN DC."""
    ID = "CDN_UPLOAD_TIMEOUT"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class ChannelsAdminLocatedTooMuch(NotAcceptable):
    """The user has reached the limit of public geogroups."""
    ID = "CHANNELS_ADMIN_LOCATED_TOO_MUCH"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class ChannelsAdminPublicTooMuch(NotAcceptable):
    """You're admin of too many public channels, make some channels private to change the username of this channel."""
    ID = "CHANNELS_ADMIN_PUBLIC_TOO_MUCH"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class ChannelsTooMuch(NotAcceptable):
    """You have joined too many channels/supergroups."""
    ID = "CHANNELS_TOO_MUCH"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class ChannelForumMissing(NotAcceptable):
    """This supergroup is not a forum."""
    ID = "CHANNEL_FORUM_MISSING"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class ChannelIdInvalid(NotAcceptable):
    """The specified supergroup ID is invalid."""
    ID = "CHANNEL_ID_INVALID"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class ChannelInvalid(NotAcceptable):
    """The provided channel is invalid."""
    ID = "CHANNEL_INVALID"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class ChannelParicipantMissing(NotAcceptable):
    """The current user is not in the channel."""
    ID = "CHANNEL_PARICIPANT_MISSING"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class ChannelPrivate(NotAcceptable):
    """You haven't joined this channel/supergroup."""
    ID = "CHANNEL_PRIVATE"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class ChannelPublicGroupNa(NotAcceptable):
    """channel/supergroup not available."""
    ID = "CHANNEL_PUBLIC_GROUP_NA"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class ChannelTooBig(NotAcceptable):
    """This channel has too many participants (>1000) to be deleted."""
    ID = "CHANNEL_TOO_BIG"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class ChannelTooLarge(NotAcceptable):
    """Channel is too large to be deleted; this error is issued when trying to delete channels with more than 1000 members (subject to change)."""
    ID = "CHANNEL_TOO_LARGE"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class ChatlistExcludeInvalid(NotAcceptable):
    """The specified `exclude_peers` are invalid."""
    ID = "CHATLIST_EXCLUDE_INVALID"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class ChatAboutNotModified(NotAcceptable):
    """About text has not changed."""
    ID = "CHAT_ABOUT_NOT_MODIFIED"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class ChatAboutTooLong(NotAcceptable):
    """Chat about too long."""
    ID = "CHAT_ABOUT_TOO_LONG"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class ChatAdminInviteRequired(NotAcceptable):
    """You do not have the rights to do this."""
    ID = "CHAT_ADMIN_INVITE_REQUIRED"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class ChatAdminRequired(NotAcceptable):
    """You must be an admin in this chat to do this."""
    ID = "CHAT_ADMIN_REQUIRED"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class ChatDiscussionUnallowed(NotAcceptable):
    """You can't enable forum topics in a discussion group linked to a channel."""
    ID = "CHAT_DISCUSSION_UNALLOWED"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class ChatForwardsRestricted(NotAcceptable):
    """You can't forward messages from a protected chat."""
    ID = "CHAT_FORWARDS_RESTRICTED"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class ChatGuestSendForbidden(NotAcceptable):
    """You join the discussion group before commenting, see [here &raquo;](/api/discussion#requiring-users-to-join-the-group) for more info."""
    ID = "CHAT_GUEST_SEND_FORBIDDEN"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class ChatIdEmpty(NotAcceptable):
    """The provided chat ID is empty."""
    ID = "CHAT_ID_EMPTY"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class ChatIdGenerateFailed(NotAcceptable):
    """Failure while generating the chat ID."""
    ID = "CHAT_ID_GENERATE_FAILED"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class ChatIdInvalid(NotAcceptable):
    """The provided chat id is invalid."""
    ID = "CHAT_ID_INVALID"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class ChatInvalid(NotAcceptable):
    """Invalid chat."""
    ID = "CHAT_INVALID"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class ChatInvitePermanent(NotAcceptable):
    """You can't set an expiration date on permanent invite links."""
    ID = "CHAT_INVITE_PERMANENT"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class ChatLinkExists(NotAcceptable):
    """The chat is public, you can't hide the history to new users."""
    ID = "CHAT_LINK_EXISTS"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class ChatNotModified(NotAcceptable):
    """No changes were made to chat information because the new information you passed is identical to the current information."""
    ID = "CHAT_NOT_MODIFIED"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class ChatPublicRequired(NotAcceptable):
    """You can only enable join requests in public groups."""
    ID = "CHAT_PUBLIC_REQUIRED"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class ChatRestricted(NotAcceptable):
    """You can't send messages in this chat, you were restricted."""
    ID = "CHAT_RESTRICTED"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class ChatRevokeDateUnsupported(NotAcceptable):
    """`min_date` and `max_date` are not available for using with non-user peers."""
    ID = "CHAT_REVOKE_DATE_UNSUPPORTED"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class ChatSendAudiosForbidden(NotAcceptable):
    """You can't send audio messages in this chat."""
    ID = "CHAT_SEND_AUDIOS_FORBIDDEN"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class ChatSendDocsForbidden(NotAcceptable):
    """You can't send documents in this chat."""
    ID = "CHAT_SEND_DOCS_FORBIDDEN"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class ChatSendGameForbidden(NotAcceptable):
    """You can't send a game to this chat."""
    ID = "CHAT_SEND_GAME_FORBIDDEN"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class ChatSendGifsForbidden(NotAcceptable):
    """You can't send gifs in this chat."""
    ID = "CHAT_SEND_GIFS_FORBIDDEN"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class ChatSendInlineForbidden(NotAcceptable):
    """You can't send inline messages in this group."""
    ID = "CHAT_SEND_INLINE_FORBIDDEN"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class ChatSendMediaForbidden(NotAcceptable):
    """You can't send media in this chat."""
    ID = "CHAT_SEND_MEDIA_FORBIDDEN"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class ChatSendPhotosForbidden(NotAcceptable):
    """You can't send photos in this chat."""
    ID = "CHAT_SEND_PHOTOS_FORBIDDEN"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class ChatSendPlainForbidden(NotAcceptable):
    """You can't send non-media (text) messages in this chat."""
    ID = "CHAT_SEND_PLAIN_FORBIDDEN"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class ChatSendPollForbidden(NotAcceptable):
    """You can't send polls in this chat."""
    ID = "CHAT_SEND_POLL_FORBIDDEN"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class ChatSendStickersForbidden(NotAcceptable):
    """You can't send stickers in this chat."""
    ID = "CHAT_SEND_STICKERS_FORBIDDEN"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class ChatSendVideosForbidden(NotAcceptable):
    """You can't send videos in this chat."""
    ID = "CHAT_SEND_VIDEOS_FORBIDDEN"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class ChatSendVoicesForbidden(NotAcceptable):
    """You can't send voice recordings in this chat."""
    ID = "CHAT_SEND_VOICES_FORBIDDEN"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class ChatTitleEmpty(NotAcceptable):
    """No chat title provided."""
    ID = "CHAT_TITLE_EMPTY"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class ChatTooBig(NotAcceptable):
    """This method is not available for groups with more than `chat_read_mark_size_threshold` members, [see client configuration &raquo;](https://core.telegram.org/api/config#client-configuration)."""
    ID = "CHAT_TOO_BIG"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class ChatWriteForbidden(NotAcceptable):
    """You can't write in this chat."""
    ID = "CHAT_WRITE_FORBIDDEN"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class CodeEmpty(NotAcceptable):
    """The provided code is empty."""
    ID = "CODE_EMPTY"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class CodeHashInvalid(NotAcceptable):
    """Code hash invalid."""
    ID = "CODE_HASH_INVALID"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class CodeInvalid(NotAcceptable):
    """Code invalid."""
    ID = "CODE_INVALID"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class ColorInvalid(NotAcceptable):
    """The specified color palette ID was invalid."""
    ID = "COLOR_INVALID"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class ConnectionApiIdInvalid(NotAcceptable):
    """The provided API id is invalid."""
    ID = "CONNECTION_API_ID_INVALID"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class ConnectionAppVersionEmpty(NotAcceptable):
    """App version is empty."""
    ID = "CONNECTION_APP_VERSION_EMPTY"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class ConnectionLayerInvalid(NotAcceptable):
    """Layer invalid."""
    ID = "CONNECTION_LAYER_INVALID"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class ContactAddMissing(NotAcceptable):
    """Contact to add is missing."""
    ID = "CONTACT_ADD_MISSING"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class ContactIdInvalid(NotAcceptable):
    """The provided contact ID is invalid."""
    ID = "CONTACT_ID_INVALID"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class ContactMissing(NotAcceptable):
    """The specified user is not a contact."""
    ID = "CONTACT_MISSING"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class ContactNameEmpty(NotAcceptable):
    """Contact name empty."""
    ID = "CONTACT_NAME_EMPTY"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class ContactReqMissing(NotAcceptable):
    """Missing contact request."""
    ID = "CONTACT_REQ_MISSING"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class CreateCallFailed(NotAcceptable):
    """An error occurred while creating the call."""
    ID = "CREATE_CALL_FAILED"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class CurrencyTotalAmountInvalid(NotAcceptable):
    """The total amount of all prices is invalid."""
    ID = "CURRENCY_TOTAL_AMOUNT_INVALID"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class CustomReactionsTooMany(NotAcceptable):
    """Too many custom reactions were specified."""
    ID = "CUSTOM_REACTIONS_TOO_MANY"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class DataInvalid(NotAcceptable):
    """Encrypted data invalid."""
    ID = "DATA_INVALID"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class DataJsonInvalid(NotAcceptable):
    """The provided JSON data is invalid."""
    ID = "DATA_JSON_INVALID"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class DataTooLong(NotAcceptable):
    """Data too long."""
    ID = "DATA_TOO_LONG"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class DateEmpty(NotAcceptable):
    """Date empty."""
    ID = "DATE_EMPTY"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class DcIdInvalid(NotAcceptable):
    """The provided DC ID is invalid."""
    ID = "DC_ID_INVALID"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class DhGAInvalid(NotAcceptable):
    """g_a invalid."""
    ID = "DH_G_A_INVALID"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class DocumentInvalid(NotAcceptable):
    """The specified document is invalid."""
    ID = "DOCUMENT_INVALID"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class EditBotInviteForbidden(NotAcceptable):
    """Normal users can't edit invites that were created by bots."""
    ID = "EDIT_BOT_INVITE_FORBIDDEN"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class EmailHashExpired(NotAcceptable):
    """Email hash expired."""
    ID = "EMAIL_HASH_EXPIRED"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class EmailInvalid(NotAcceptable):
    """The specified email is invalid."""
    ID = "EMAIL_INVALID"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class EmailNotSetup(NotAcceptable):
    """In order to change the login email with emailVerifyPurposeLoginChange, an existing login email must already be set using emailVerifyPurposeLoginSetup."""
    ID = "EMAIL_NOT_SETUP"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class EmailUnconfirmed(NotAcceptable):
    """Email unconfirmed."""
    ID = "EMAIL_UNCONFIRMED"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class EmailUnconfirmed(NotAcceptable):
    """The provided email isn't confirmed, {value} is the length of the verification code that was just sent to the email: use [account.verifyEmail](https://core.telegram.org/method/account.verifyEmail) to enter the received verification code and enable the recovery email."""
    ID = "EMAIL_UNCONFIRMED_X"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class EmailVerifyExpired(NotAcceptable):
    """The verification email has expired."""
    ID = "EMAIL_VERIFY_EXPIRED"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class EmojiInvalid(NotAcceptable):
    """The specified theme emoji is valid."""
    ID = "EMOJI_INVALID"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class EmojiMarkupInvalid(NotAcceptable):
    """The specified `video_emoji_markup` was invalid."""
    ID = "EMOJI_MARKUP_INVALID"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class EmojiNotModified(NotAcceptable):
    """The theme wasn't changed."""
    ID = "EMOJI_NOT_MODIFIED"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class EmoticonEmpty(NotAcceptable):
    """The emoji is empty."""
    ID = "EMOTICON_EMPTY"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class EmoticonInvalid(NotAcceptable):
    """The specified emoji is invalid."""
    ID = "EMOTICON_INVALID"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class EmoticonStickerpackMissing(NotAcceptable):
    """inputStickerSetDice.emoji cannot be empty."""
    ID = "EMOTICON_STICKERPACK_MISSING"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class EncryptedMessageInvalid(NotAcceptable):
    """Encrypted message invalid."""
    ID = "ENCRYPTED_MESSAGE_INVALID"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class EncryptionAlreadyAccepted(NotAcceptable):
    """Secret chat already accepted."""
    ID = "ENCRYPTION_ALREADY_ACCEPTED"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class EncryptionAlreadyDeclined(NotAcceptable):
    """The secret chat was already declined."""
    ID = "ENCRYPTION_ALREADY_DECLINED"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class EncryptionDeclined(NotAcceptable):
    """The secret chat was declined."""
    ID = "ENCRYPTION_DECLINED"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class EncryptionIdInvalid(NotAcceptable):
    """The provided secret chat ID is invalid."""
    ID = "ENCRYPTION_ID_INVALID"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class EntitiesTooLong(NotAcceptable):
    """You provided too many styled message entities."""
    ID = "ENTITIES_TOO_LONG"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class EntityBoundsInvalid(NotAcceptable):
    """A specified [entity offset or length](/api/entities#entity-length) is invalid, see [here &raquo;](/api/entities#entity-length) for info on how to properly compute the entity offset/length."""
    ID = "ENTITY_BOUNDS_INVALID"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class EntityMentionUserInvalid(NotAcceptable):
    """You mentioned an invalid user."""
    ID = "ENTITY_MENTION_USER_INVALID"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class ErrorTextEmpty(NotAcceptable):
    """The provided error message is empty."""
    ID = "ERROR_TEXT_EMPTY"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class ExpireDateInvalid(NotAcceptable):
    """The specified expiration date is invalid."""
    ID = "EXPIRE_DATE_INVALID"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class ExportCardInvalid(NotAcceptable):
    """Provided card is invalid."""
    ID = "EXPORT_CARD_INVALID"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class ExternalUrlInvalid(NotAcceptable):
    """External URL invalid."""
    ID = "EXTERNAL_URL_INVALID"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class FilerefUpgradeNeeded(NotAcceptable):
    """The client has to be updated in order to support [file references](https://core.telegram.org/api/file-references)."""
    ID = "FILEREF_UPGRADE_NEEDED"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class FileContentTypeInvalid(NotAcceptable):
    """File content-type is invalid."""
    ID = "FILE_CONTENT_TYPE_INVALID"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class FileEmtpy(NotAcceptable):
    """An empty file was provided."""
    ID = "FILE_EMTPY"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class FileIdInvalid(NotAcceptable):
    """The provided file id is invalid."""
    ID = "FILE_ID_INVALID"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class FilePartsInvalid(NotAcceptable):
    """The number of file parts is invalid."""
    ID = "FILE_PARTS_INVALID"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class FilePartEmpty(NotAcceptable):
    """The provided file part is empty."""
    ID = "FILE_PART_EMPTY"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class FilePartInvalid(NotAcceptable):
    """The file part number is invalid."""
    ID = "FILE_PART_INVALID"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class FilePartLengthInvalid(NotAcceptable):
    """The length of a file part is invalid."""
    ID = "FILE_PART_LENGTH_INVALID"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class FilePartSizeChanged(NotAcceptable):
    """Provided file part size has changed."""
    ID = "FILE_PART_SIZE_CHANGED"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class FilePartSizeInvalid(NotAcceptable):
    """The provided file part size is invalid."""
    ID = "FILE_PART_SIZE_INVALID"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class FilePartTooBig(NotAcceptable):
    """The uploaded file part is too big."""
    ID = "FILE_PART_TOO_BIG"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class FileReferenceEmpty(NotAcceptable):
    """An empty [file reference](https://core.telegram.org/api/file_reference) was specified."""
    ID = "FILE_REFERENCE_EMPTY"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class FileReferenceExpired(NotAcceptable):
    """File reference expired, it must be refetched as described in [the documentation](https://core.telegram.org/api/file_reference)."""
    ID = "FILE_REFERENCE_EXPIRED"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class FileReferenceInvalid(NotAcceptable):
    """The specified [file reference](https://core.telegram.org/api/file_reference) is invalid."""
    ID = "FILE_REFERENCE_INVALID"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class FileTitleEmpty(NotAcceptable):
    """An empty file title was specified."""
    ID = "FILE_TITLE_EMPTY"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class FileTokenInvalid(NotAcceptable):
    """The specified file token is invalid."""
    ID = "FILE_TOKEN_INVALID"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class FilterIdInvalid(NotAcceptable):
    """The specified filter ID is invalid."""
    ID = "FILTER_ID_INVALID"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class FilterIncludeEmpty(NotAcceptable):
    """The include_peers vector of the filter is empty."""
    ID = "FILTER_INCLUDE_EMPTY"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class FilterNotSupported(NotAcceptable):
    """The specified filter cannot be used in this context."""
    ID = "FILTER_NOT_SUPPORTED"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class FilterTitleEmpty(NotAcceptable):
    """The title field of the filter is empty."""
    ID = "FILTER_TITLE_EMPTY"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class FirstnameInvalid(NotAcceptable):
    """The first name is invalid."""
    ID = "FIRSTNAME_INVALID"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class FolderIdEmpty(NotAcceptable):
    """An empty folder ID was specified."""
    ID = "FOLDER_ID_EMPTY"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class FolderIdInvalid(NotAcceptable):
    """Invalid folder ID."""
    ID = "FOLDER_ID_INVALID"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class ForumEnabled(NotAcceptable):
    """You can't execute the specified action because the group is a [forum](https://core.telegram.org/api/forum), disable forum functionality to continue."""
    ID = "FORUM_ENABLED"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class FreshChangeAdminsForbidden(NotAcceptable):
    """You were just elected admin, you can't add or modify other admins yet."""
    ID = "FRESH_CHANGE_ADMINS_FORBIDDEN"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class FreshChangePhoneForbidden(NotAcceptable):
    """You can't change phone number right after logging in, please wait at least 24 hours."""
    ID = "FRESH_CHANGE_PHONE_FORBIDDEN"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class FreshResetAuthorisationForbidden(NotAcceptable):
    """You can't logout other sessions if less than 24 hours have passed since you logged on the current session."""
    ID = "FRESH_RESET_AUTHORISATION_FORBIDDEN"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class FromMessageBotDisabled(NotAcceptable):
    """Bots can't use fromMessage min constructors."""
    ID = "FROM_MESSAGE_BOT_DISABLED"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class FromPeerInvalid(NotAcceptable):
    """The specified from_id is invalid."""
    ID = "FROM_PEER_INVALID"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class GameBotInvalid(NotAcceptable):
    """Bots can't send another bot's game."""
    ID = "GAME_BOT_INVALID"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class GeneralModifyIconForbidden(NotAcceptable):
    """You can't modify the icon of the "General" topic."""
    ID = "GENERAL_MODIFY_ICON_FORBIDDEN"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class GeoPointInvalid(NotAcceptable):
    """Invalid geoposition provided."""
    ID = "GEO_POINT_INVALID"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class GiftSlugExpired(NotAcceptable):
    """The specified gift slug has expired."""
    ID = "GIFT_SLUG_EXPIRED"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class GiftSlugInvalid(NotAcceptable):
    """The specified slug is invalid."""
    ID = "GIFT_SLUG_INVALID"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class GifContentTypeInvalid(NotAcceptable):
    """GIF content-type invalid."""
    ID = "GIF_CONTENT_TYPE_INVALID"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class GifIdInvalid(NotAcceptable):
    """The provided GIF ID is invalid."""
    ID = "GIF_ID_INVALID"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class GraphExpiredReload(NotAcceptable):
    """This graph has expired, please obtain a new graph token."""
    ID = "GRAPH_EXPIRED_RELOAD"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class GraphInvalidReload(NotAcceptable):
    """Invalid graph token provided, please reload the stats and provide the updated token."""
    ID = "GRAPH_INVALID_RELOAD"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class GraphOutdatedReload(NotAcceptable):
    """The graph is outdated, please get a new async token using stats.getBroadcastStats."""
    ID = "GRAPH_OUTDATED_RELOAD"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class GroupcallAlreadyDiscarded(NotAcceptable):
    """The group call was already discarded."""
    ID = "GROUPCALL_ALREADY_DISCARDED"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class GroupcallAlreadyStarted(NotAcceptable):
    """The groupcall has already started, you can join directly using [phone.joinGroupCall](https://core.telegram.org/method/phone.joinGroupCall)."""
    ID = "GROUPCALL_ALREADY_STARTED"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class GroupcallForbidden(NotAcceptable):
    """The group call has already ended."""
    ID = "GROUPCALL_FORBIDDEN"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class GroupcallInvalid(NotAcceptable):
    """The specified group call is invalid."""
    ID = "GROUPCALL_INVALID"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class GroupcallJoinMissing(NotAcceptable):
    """You haven't joined this group call."""
    ID = "GROUPCALL_JOIN_MISSING"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class GroupcallNotModified(NotAcceptable):
    """Group call settings weren't modified."""
    ID = "GROUPCALL_NOT_MODIFIED"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class GroupcallSsrcDuplicateMuch(NotAcceptable):
    """The app needs to retry joining the group call with a new SSRC value."""
    ID = "GROUPCALL_SSRC_DUPLICATE_MUCH"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class GroupedMediaInvalid(NotAcceptable):
    """Invalid grouped media."""
    ID = "GROUPED_MEDIA_INVALID"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class HashInvalid(NotAcceptable):
    """The provided hash is invalid."""
    ID = "HASH_INVALID"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class HideRequesterMissing(NotAcceptable):
    """The join request was missing or was already handled."""
    ID = "HIDE_REQUESTER_MISSING"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class ImageProcessFailed(NotAcceptable):
    """Failure while processing image."""
    ID = "IMAGE_PROCESS_FAILED"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class ImportFileInvalid(NotAcceptable):
    """The specified chat export file is invalid."""
    ID = "IMPORT_FILE_INVALID"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class ImportFormatUnrecognized(NotAcceptable):
    """The specified chat export file was exported from an unsupported chat app."""
    ID = "IMPORT_FORMAT_UNRECOGNIZED"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class ImportIdInvalid(NotAcceptable):
    """The specified import ID is invalid."""
    ID = "IMPORT_ID_INVALID"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class ImportTokenInvalid(NotAcceptable):
    """The specified token is invalid."""
    ID = "IMPORT_TOKEN_INVALID"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class InlineBotRequired(NotAcceptable):
    """Only the inline bot can edit message."""
    ID = "INLINE_BOT_REQUIRED"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class InlineResultExpired(NotAcceptable):
    """The inline query expired."""
    ID = "INLINE_RESULT_EXPIRED"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class InputChatlistInvalid(NotAcceptable):
    """The specified folder is invalid."""
    ID = "INPUT_CHATLIST_INVALID"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class InputFilterInvalid(NotAcceptable):
    """The specified filter is invalid."""
    ID = "INPUT_FILTER_INVALID"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class InputTextEmpty(NotAcceptable):
    """The specified text is empty."""
    ID = "INPUT_TEXT_EMPTY"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class InputTextTooLong(NotAcceptable):
    """The specified text is too long."""
    ID = "INPUT_TEXT_TOO_LONG"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class InputUserDeactivated(NotAcceptable):
    """The specified user was deleted."""
    ID = "INPUT_USER_DEACTIVATED"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class InvitesTooMuch(NotAcceptable):
    """The maximum number of per-folder invites specified by the `chatlist_invites_limit_default`/`chatlist_invites_limit_premium` [client configuration parameters &raquo;](/api/config#chatlist-invites-limit-default) was reached."""
    ID = "INVITES_TOO_MUCH"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class InviteForbiddenWithJoinas(NotAcceptable):
    """If the user has anonymously joined a group call as a channel, they can't invite other users to the group call because that would cause deanonymization, because the invite would be sent using the original user ID, not the anonymized channel ID."""
    ID = "INVITE_FORBIDDEN_WITH_JOINAS"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class InviteHashEmpty(NotAcceptable):
    """The invite hash is empty."""
    ID = "INVITE_HASH_EMPTY"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class InviteHashExpired(NotAcceptable):
    """The invite link has expired."""
    ID = "INVITE_HASH_EXPIRED"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class InviteHashInvalid(NotAcceptable):
    """The invite hash is invalid."""
    ID = "INVITE_HASH_INVALID"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class InviteRequestSent(NotAcceptable):
    """You have successfully requested to join this chat or channel."""
    ID = "INVITE_REQUEST_SENT"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class InviteRevokedMissing(NotAcceptable):
    """The specified invite link was already revoked or is invalid."""
    ID = "INVITE_REVOKED_MISSING"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class InviteSlugEmpty(NotAcceptable):
    """The specified invite slug is empty."""
    ID = "INVITE_SLUG_EMPTY"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class InviteSlugExpired(NotAcceptable):
    """The specified chat folder link has expired."""
    ID = "INVITE_SLUG_EXPIRED"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class InvoicePayloadInvalid(NotAcceptable):
    """The specified invoice payload is invalid."""
    ID = "INVOICE_PAYLOAD_INVALID"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class JoinAsPeerInvalid(NotAcceptable):
    """The specified peer cannot be used to join a group call."""
    ID = "JOIN_AS_PEER_INVALID"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class LangCodeInvalid(NotAcceptable):
    """The specified language code is invalid."""
    ID = "LANG_CODE_INVALID"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class LangCodeNotSupported(NotAcceptable):
    """The specified language code is not supported."""
    ID = "LANG_CODE_NOT_SUPPORTED"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class LangPackInvalid(NotAcceptable):
    """The provided language pack is invalid."""
    ID = "LANG_PACK_INVALID"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class LastnameInvalid(NotAcceptable):
    """The last name is invalid."""
    ID = "LASTNAME_INVALID"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class LimitInvalid(NotAcceptable):
    """The provided limit is invalid."""
    ID = "LIMIT_INVALID"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class LinkNotModified(NotAcceptable):
    """Discussion link not modified."""
    ID = "LINK_NOT_MODIFIED"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class LocationInvalid(NotAcceptable):
    """The provided location is invalid."""
    ID = "LOCATION_INVALID"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class MaxDateInvalid(NotAcceptable):
    """The specified maximum date is invalid."""
    ID = "MAX_DATE_INVALID"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class MaxIdInvalid(NotAcceptable):
    """The provided max ID is invalid."""
    ID = "MAX_ID_INVALID"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class MaxQtsInvalid(NotAcceptable):
    """The specified max_qts is invalid."""
    ID = "MAX_QTS_INVALID"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class Md5ChecksumInvalid(NotAcceptable):
    """The MD5 checksums do not match."""
    ID = "MD5_CHECKSUM_INVALID"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class MediaCaptionTooLong(NotAcceptable):
    """The caption is too long."""
    ID = "MEDIA_CAPTION_TOO_LONG"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class MediaEmpty(NotAcceptable):
    """The provided media object is invalid."""
    ID = "MEDIA_EMPTY"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class MediaFileInvalid(NotAcceptable):
    """The specified media file is invalid."""
    ID = "MEDIA_FILE_INVALID"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class MediaGroupedInvalid(NotAcceptable):
    """You tried to send media of different types in an album."""
    ID = "MEDIA_GROUPED_INVALID"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class MediaInvalid(NotAcceptable):
    """Media invalid."""
    ID = "MEDIA_INVALID"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class MediaNewInvalid(NotAcceptable):
    """The new media is invalid."""
    ID = "MEDIA_NEW_INVALID"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class MediaPrevInvalid(NotAcceptable):
    """Previous media invalid."""
    ID = "MEDIA_PREV_INVALID"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class MediaTtlInvalid(NotAcceptable):
    """The specified media TTL is invalid."""
    ID = "MEDIA_TTL_INVALID"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class MediaTypeInvalid(NotAcceptable):
    """The specified media type cannot be used in stories."""
    ID = "MEDIA_TYPE_INVALID"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class MediaVideoStoryMissing(NotAcceptable):
    """"""
    ID = "MEDIA_VIDEO_STORY_MISSING"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class MegagroupGeoRequired(NotAcceptable):
    """This method can only be invoked on a geogroup."""
    ID = "MEGAGROUP_GEO_REQUIRED"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class MegagroupIdInvalid(NotAcceptable):
    """Invalid supergroup ID."""
    ID = "MEGAGROUP_ID_INVALID"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class MegagroupPrehistoryHidden(NotAcceptable):
    """Group with hidden history for new members can't be set as discussion groups."""
    ID = "MEGAGROUP_PREHISTORY_HIDDEN"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class MegagroupRequired(NotAcceptable):
    """You can only use this method on a supergroup."""
    ID = "MEGAGROUP_REQUIRED"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class MessageAuthorRequired(NotAcceptable):
    """Message author required."""
    ID = "MESSAGE_AUTHOR_REQUIRED"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class MessageDeleteForbidden(NotAcceptable):
    """You can't delete one of the messages you tried to delete, most likely because it is a service message."""
    ID = "MESSAGE_DELETE_FORBIDDEN"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class MessageEditTimeExpired(NotAcceptable):
    """You can't edit this message anymore, too much time has passed since its creation."""
    ID = "MESSAGE_EDIT_TIME_EXPIRED"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class MessageEmpty(NotAcceptable):
    """The provided message is empty."""
    ID = "MESSAGE_EMPTY"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class MessageIdsEmpty(NotAcceptable):
    """No message ids were provided."""
    ID = "MESSAGE_IDS_EMPTY"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class MessageIdInvalid(NotAcceptable):
    """The provided message id is invalid."""
    ID = "MESSAGE_ID_INVALID"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class MessageNotModified(NotAcceptable):
    """The provided message data is identical to the previous message data, the message wasn't modified."""
    ID = "MESSAGE_NOT_MODIFIED"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class MessagePollClosed(NotAcceptable):
    """Poll closed."""
    ID = "MESSAGE_POLL_CLOSED"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class MessageTooLong(NotAcceptable):
    """The provided message is too long."""
    ID = "MESSAGE_TOO_LONG"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class MethodInvalid(NotAcceptable):
    """The specified method is invalid."""
    ID = "METHOD_INVALID"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class MinDateInvalid(NotAcceptable):
    """The specified minimum date is invalid."""
    ID = "MIN_DATE_INVALID"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class MsgIdInvalid(NotAcceptable):
    """Invalid message ID provided."""
    ID = "MSG_ID_INVALID"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class MsgTooOld(NotAcceptable):
    """[`chat_read_mark_expire_period` seconds](https://core.telegram.org/api/config#chat-read-mark-expire-period) have passed since the message was sent, read receipts were deleted."""
    ID = "MSG_TOO_OLD"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class MsgWaitFailed(NotAcceptable):
    """A waiting call returned an error."""
    ID = "MSG_WAIT_FAILED"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class MultiMediaTooLong(NotAcceptable):
    """Too many media files for album."""
    ID = "MULTI_MEDIA_TOO_LONG"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class NewSaltInvalid(NotAcceptable):
    """The new salt is invalid."""
    ID = "NEW_SALT_INVALID"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class NewSettingsEmpty(NotAcceptable):
    """No password is set on the current account, and no new password was specified in `new_settings`."""
    ID = "NEW_SETTINGS_EMPTY"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class NewSettingsInvalid(NotAcceptable):
    """The new password settings are invalid."""
    ID = "NEW_SETTINGS_INVALID"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class NextOffsetInvalid(NotAcceptable):
    """The specified offset is longer than 64 bytes."""
    ID = "NEXT_OFFSET_INVALID"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class OffsetInvalid(NotAcceptable):
    """The provided offset is invalid."""
    ID = "OFFSET_INVALID"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class OffsetPeerIdInvalid(NotAcceptable):
    """The provided offset peer is invalid."""
    ID = "OFFSET_PEER_ID_INVALID"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class OptionsTooMuch(NotAcceptable):
    """Too many options provided."""
    ID = "OPTIONS_TOO_MUCH"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class OptionInvalid(NotAcceptable):
    """Invalid option selected."""
    ID = "OPTION_INVALID"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class OrderInvalid(NotAcceptable):
    """The specified username order is invalid."""
    ID = "ORDER_INVALID"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class PackShortNameInvalid(NotAcceptable):
    """Short pack name invalid."""
    ID = "PACK_SHORT_NAME_INVALID"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class PackShortNameOccupied(NotAcceptable):
    """A stickerpack with this name already exists."""
    ID = "PACK_SHORT_NAME_OCCUPIED"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class PackTitleInvalid(NotAcceptable):
    """The stickerpack title is invalid."""
    ID = "PACK_TITLE_INVALID"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class ParticipantsTooFew(NotAcceptable):
    """Not enough participants."""
    ID = "PARTICIPANTS_TOO_FEW"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class ParticipantIdInvalid(NotAcceptable):
    """The specified participant ID is invalid."""
    ID = "PARTICIPANT_ID_INVALID"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class ParticipantJoinMissing(NotAcceptable):
    """Trying to enable a presentation, when the user hasn't joined the Video Chat with [phone.joinGroupCall](https://core.telegram.org/method/phone.joinGroupCall)."""
    ID = "PARTICIPANT_JOIN_MISSING"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class ParticipantVersionOutdated(NotAcceptable):
    """The other participant does not use an up to date telegram client with support for calls."""
    ID = "PARTICIPANT_VERSION_OUTDATED"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class PasswordEmpty(NotAcceptable):
    """The provided password is empty."""
    ID = "PASSWORD_EMPTY"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class PasswordHashInvalid(NotAcceptable):
    """The provided password hash is invalid."""
    ID = "PASSWORD_HASH_INVALID"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class PasswordMissing(NotAcceptable):
    """You must enable 2FA in order to transfer ownership of a channel."""
    ID = "PASSWORD_MISSING"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class PasswordRecoveryExpired(NotAcceptable):
    """The recovery code has expired."""
    ID = "PASSWORD_RECOVERY_EXPIRED"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class PasswordRecoveryNa(NotAcceptable):
    """No email was set, can't recover password via email."""
    ID = "PASSWORD_RECOVERY_NA"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class PasswordRequired(NotAcceptable):
    """A [2FA password](https://core.telegram.org/api/srp) must be configured to use Telegram Passport."""
    ID = "PASSWORD_REQUIRED"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class PasswordTooFresh(NotAcceptable):
    """The password was modified less than 24 hours ago, try again in {value} seconds."""
    ID = "PASSWORD_TOO_FRESH_X"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class PaymentProviderInvalid(NotAcceptable):
    """The specified payment provider is invalid."""
    ID = "PAYMENT_PROVIDER_INVALID"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class PaymentUnsupported(NotAcceptable):
    """A detailed description of the error will be received separately as described [here &raquo;](https://core.telegram.org/api/errors#406-not-acceptable)."""
    ID = "PAYMENT_UNSUPPORTED"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class PeersListEmpty(NotAcceptable):
    """The specified list of peers is empty."""
    ID = "PEERS_LIST_EMPTY"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class PeerHistoryEmpty(NotAcceptable):
    """You can't pin an empty chat with a user."""
    ID = "PEER_HISTORY_EMPTY"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class PeerIdInvalid(NotAcceptable):
    """The provided peer id is invalid."""
    ID = "PEER_ID_INVALID"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class PeerIdNotSupported(NotAcceptable):
    """The provided peer ID is not supported."""
    ID = "PEER_ID_NOT_SUPPORTED"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class PersistentTimestampEmpty(NotAcceptable):
    """Persistent timestamp empty."""
    ID = "PERSISTENT_TIMESTAMP_EMPTY"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class PersistentTimestampInvalid(NotAcceptable):
    """Persistent timestamp invalid."""
    ID = "PERSISTENT_TIMESTAMP_INVALID"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class PersistentTimestampOutdated(NotAcceptable):
    """Channel internal replication issues, try again later (treat this like an RPC_CALL_FAIL)."""
    ID = "PERSISTENT_TIMESTAMP_OUTDATED"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class PhoneCodeEmpty(NotAcceptable):
    """phone_code is missing."""
    ID = "PHONE_CODE_EMPTY"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class PhoneCodeExpired(NotAcceptable):
    """The phone code you provided has expired."""
    ID = "PHONE_CODE_EXPIRED"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class PhoneCodeHashEmpty(NotAcceptable):
    """phone_code_hash is missing."""
    ID = "PHONE_CODE_HASH_EMPTY"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class PhoneCodeInvalid(NotAcceptable):
    """The provided phone code is invalid."""
    ID = "PHONE_CODE_INVALID"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class PhoneHashExpired(NotAcceptable):
    """An invalid or expired `phone_code_hash` was provided."""
    ID = "PHONE_HASH_EXPIRED"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class PhoneNotOccupied(NotAcceptable):
    """No user is associated to the specified phone number."""
    ID = "PHONE_NOT_OCCUPIED"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class PhoneNumberAppSignupForbidden(NotAcceptable):
    """You can't sign up using this app."""
    ID = "PHONE_NUMBER_APP_SIGNUP_FORBIDDEN"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class PhoneNumberBanned(NotAcceptable):
    """The provided phone number is banned from telegram."""
    ID = "PHONE_NUMBER_BANNED"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class PhoneNumberFlood(NotAcceptable):
    """You asked for the code too many times."""
    ID = "PHONE_NUMBER_FLOOD"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class PhoneNumberInvalid(NotAcceptable):
    """The phone number is invalid."""
    ID = "PHONE_NUMBER_INVALID"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class PhoneNumberOccupied(NotAcceptable):
    """The phone number is already in use."""
    ID = "PHONE_NUMBER_OCCUPIED"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class PhoneNumberUnoccupied(NotAcceptable):
    """The phone number is not yet being used."""
    ID = "PHONE_NUMBER_UNOCCUPIED"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class PhonePasswordFlood(NotAcceptable):
    """You have tried logging in too many times."""
    ID = "PHONE_PASSWORD_FLOOD"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class PhonePasswordProtected(NotAcceptable):
    """This phone is password protected."""
    ID = "PHONE_PASSWORD_PROTECTED"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class PhotoContentTypeInvalid(NotAcceptable):
    """Photo mime-type invalid."""
    ID = "PHOTO_CONTENT_TYPE_INVALID"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class PhotoContentUrlEmpty(NotAcceptable):
    """Photo URL invalid."""
    ID = "PHOTO_CONTENT_URL_EMPTY"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class PhotoCropFileMissing(NotAcceptable):
    """Photo crop file missing."""
    ID = "PHOTO_CROP_FILE_MISSING"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class PhotoCropSizeSmall(NotAcceptable):
    """Photo is too small."""
    ID = "PHOTO_CROP_SIZE_SMALL"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class PhotoExtInvalid(NotAcceptable):
    """The extension of the photo is invalid."""
    ID = "PHOTO_EXT_INVALID"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class PhotoFileMissing(NotAcceptable):
    """Profile photo file missing."""
    ID = "PHOTO_FILE_MISSING"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class PhotoIdInvalid(NotAcceptable):
    """Photo ID invalid."""
    ID = "PHOTO_ID_INVALID"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class PhotoInvalid(NotAcceptable):
    """Photo invalid."""
    ID = "PHOTO_INVALID"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class PhotoInvalidDimensions(NotAcceptable):
    """The photo dimensions are invalid."""
    ID = "PHOTO_INVALID_DIMENSIONS"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class PhotoSaveFileInvalid(NotAcceptable):
    """Internal issues, try again later."""
    ID = "PHOTO_SAVE_FILE_INVALID"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class PhotoThumbUrlEmpty(NotAcceptable):
    """Photo thumbnail URL is empty."""
    ID = "PHOTO_THUMB_URL_EMPTY"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class PinnedDialogsTooMuch(NotAcceptable):
    """Too many pinned dialogs."""
    ID = "PINNED_DIALOGS_TOO_MUCH"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class PinRestricted(NotAcceptable):
    """You can't pin messages."""
    ID = "PIN_RESTRICTED"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class PlaymarketPurchaseUsed(NotAcceptable):
    """ The Google account logged in the Play Store has already an ongoing Telegram Premium cycle in progress"""
    ID = "PLAYMARKET_PURCHASE_USED"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class PollAnswersInvalid(NotAcceptable):
    """Invalid poll answers were provided."""
    ID = "POLL_ANSWERS_INVALID"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class PollAnswerInvalid(NotAcceptable):
    """One of the poll answers is not acceptable."""
    ID = "POLL_ANSWER_INVALID"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class PollOptionDuplicate(NotAcceptable):
    """Duplicate poll options provided."""
    ID = "POLL_OPTION_DUPLICATE"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class PollOptionInvalid(NotAcceptable):
    """Invalid poll option provided."""
    ID = "POLL_OPTION_INVALID"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class PollQuestionInvalid(NotAcceptable):
    """One of the poll questions is not acceptable."""
    ID = "POLL_QUESTION_INVALID"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class PollVoteRequired(NotAcceptable):
    """Cast a vote in the poll before calling this method."""
    ID = "POLL_VOTE_REQUIRED"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class PrecheckoutFailed(NotAcceptable):
    """Precheckout failed, a detailed and localized description for the error will be emitted via an [updateServiceNotification as specified here &raquo;](https://core.telegram.org/api/errors#406-not-acceptable)."""
    ID = "PRECHECKOUT_FAILED"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class PremiumAccountRequired(NotAcceptable):
    """A premium account is required to execute this action."""
    ID = "PREMIUM_ACCOUNT_REQUIRED"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class PremiumCurrentlyUnavailable(NotAcceptable):
    """You cannot currently purchase a Premium subscription."""
    ID = "PREMIUM_CURRENTLY_UNAVAILABLE"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class PremiumGiftcodeWasRefunded(NotAcceptable):
    """This gift code can't be redeemed because the giveaway organizer requested a refund"""
    ID = "PREMIUM_GIFTCODE_WAS_REFUNDED"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class PremiumSubActiveUntil(NotAcceptable):
    """You already have a premium subscription active until unixtime {value} ."""
    ID = "PREMIUM_SUB_ACTIVE_UNTIL_X"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class PreviousChatImportActiveWaitMin(NotAcceptable):
    """Import for this chat is already in progress, wait {value} minutes before starting a new one."""
    ID = "PREVIOUS_CHAT_IMPORT_ACTIVE_WAIT_XMIN"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class PrivacyKeyInvalid(NotAcceptable):
    """The privacy key is invalid."""
    ID = "PRIVACY_KEY_INVALID"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class PrivacyPremiumRequired(NotAcceptable):
    """You need a [Telegram Premium subscription](https://core.telegram.org/api/premium) to send a message to this user."""
    ID = "PRIVACY_PREMIUM_REQUIRED"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class PrivacyTooLong(NotAcceptable):
    """Too many privacy rules were specified, the current limit is 1000."""
    ID = "PRIVACY_TOO_LONG"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class PrivacyValueInvalid(NotAcceptable):
    """The specified privacy rule combination is invalid."""
    ID = "PRIVACY_VALUE_INVALID"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class PublicChannelMissing(NotAcceptable):
    """You can only export group call invite links for public chats or channels."""
    ID = "PUBLIC_CHANNEL_MISSING"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class PublicKeyRequired(NotAcceptable):
    """A public key is required."""
    ID = "PUBLIC_KEY_REQUIRED"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class QueryIdEmpty(NotAcceptable):
    """The query ID is empty."""
    ID = "QUERY_ID_EMPTY"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class QueryIdInvalid(NotAcceptable):
    """The query ID is invalid."""
    ID = "QUERY_ID_INVALID"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class QueryTooShort(NotAcceptable):
    """The query string is too short."""
    ID = "QUERY_TOO_SHORT"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class QuizAnswerMissing(NotAcceptable):
    """You can forward a quiz while hiding the original author only after choosing an option in the quiz."""
    ID = "QUIZ_ANSWER_MISSING"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class QuizCorrectAnswersEmpty(NotAcceptable):
    """No correct quiz answer was specified."""
    ID = "QUIZ_CORRECT_ANSWERS_EMPTY"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class QuizCorrectAnswersTooMuch(NotAcceptable):
    """You specified too many correct answers in a quiz, quizzes can only have one right answer!"""
    ID = "QUIZ_CORRECT_ANSWERS_TOO_MUCH"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class QuizCorrectAnswerInvalid(NotAcceptable):
    """An invalid value was provided to the correct_answers field."""
    ID = "QUIZ_CORRECT_ANSWER_INVALID"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class QuizMultipleInvalid(NotAcceptable):
    """Quizzes can't have the multiple_choice flag set!"""
    ID = "QUIZ_MULTIPLE_INVALID"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class RandomIdDuplicate(NotAcceptable):
    """You provided a random ID that was already used."""
    ID = "RANDOM_ID_DUPLICATE"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class RandomIdEmpty(NotAcceptable):
    """Random ID empty."""
    ID = "RANDOM_ID_EMPTY"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class RandomIdInvalid(NotAcceptable):
    """A provided random ID is invalid."""
    ID = "RANDOM_ID_INVALID"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class RandomLengthInvalid(NotAcceptable):
    """Random length invalid."""
    ID = "RANDOM_LENGTH_INVALID"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class RangesInvalid(NotAcceptable):
    """Invalid range provided."""
    ID = "RANGES_INVALID"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class ReactionsTooMany(NotAcceptable):
    """The message already has exactly `reactions_uniq_max` reaction emojis, you can't react with a new emoji, see [the docs for more info &raquo;](/api/config#client-configuration)."""
    ID = "REACTIONS_TOO_MANY"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class ReactionEmpty(NotAcceptable):
    """Empty reaction provided."""
    ID = "REACTION_EMPTY"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class ReactionInvalid(NotAcceptable):
    """The specified reaction is invalid."""
    ID = "REACTION_INVALID"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class ReplyMarkupBuyEmpty(NotAcceptable):
    """Reply markup for buy button empty."""
    ID = "REPLY_MARKUP_BUY_EMPTY"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class ReplyMarkupInvalid(NotAcceptable):
    """The provided reply markup is invalid."""
    ID = "REPLY_MARKUP_INVALID"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class ReplyMarkupTooLong(NotAcceptable):
    """The specified reply_markup is too long."""
    ID = "REPLY_MARKUP_TOO_LONG"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class ReplyMessageIdInvalid(NotAcceptable):
    """The specified reply-to message ID is invalid."""
    ID = "REPLY_MESSAGE_ID_INVALID"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class ReplyToInvalid(NotAcceptable):
    """The specified `reply_to` field is invalid."""
    ID = "REPLY_TO_INVALID"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class ReplyToUserInvalid(NotAcceptable):
    """The replied-to user is invalid."""
    ID = "REPLY_TO_USER_INVALID"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class ResetRequestMissing(NotAcceptable):
    """No password reset is in progress."""
    ID = "RESET_REQUEST_MISSING"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class ResultsTooMuch(NotAcceptable):
    """Too many results were provided."""
    ID = "RESULTS_TOO_MUCH"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class ResultIdDuplicate(NotAcceptable):
    """You provided a duplicate result ID."""
    ID = "RESULT_ID_DUPLICATE"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class ResultIdEmpty(NotAcceptable):
    """Result ID empty."""
    ID = "RESULT_ID_EMPTY"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class ResultIdInvalid(NotAcceptable):
    """One of the specified result IDs is invalid."""
    ID = "RESULT_ID_INVALID"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class ResultTypeInvalid(NotAcceptable):
    """Result type invalid."""
    ID = "RESULT_TYPE_INVALID"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class RevoteNotAllowed(NotAcceptable):
    """You cannot change your vote."""
    ID = "REVOTE_NOT_ALLOWED"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class RightsNotModified(NotAcceptable):
    """The new admin rights are equal to the old rights, no change was made."""
    ID = "RIGHTS_NOT_MODIFIED"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class RightForbidden(NotAcceptable):
    """Your admin rights do not allow you to do this."""
    ID = "RIGHT_FORBIDDEN"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class RsaDecryptFailed(NotAcceptable):
    """Internal RSA decryption failed."""
    ID = "RSA_DECRYPT_FAILED"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class ScheduleBotNotAllowed(NotAcceptable):
    """Bots cannot schedule messages."""
    ID = "SCHEDULE_BOT_NOT_ALLOWED"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class ScheduleDateInvalid(NotAcceptable):
    """Invalid schedule date provided."""
    ID = "SCHEDULE_DATE_INVALID"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class ScheduleDateTooLate(NotAcceptable):
    """You can't schedule a message this far in the future."""
    ID = "SCHEDULE_DATE_TOO_LATE"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class ScheduleStatusPrivate(NotAcceptable):
    """Can't schedule until user is online, if the user's last seen timestamp is hidden by their privacy settings."""
    ID = "SCHEDULE_STATUS_PRIVATE"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class ScheduleTooMuch(NotAcceptable):
    """There are too many scheduled messages."""
    ID = "SCHEDULE_TOO_MUCH"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class ScoreInvalid(NotAcceptable):
    """The specified game score is invalid."""
    ID = "SCORE_INVALID"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class SearchQueryEmpty(NotAcceptable):
    """The search query is empty."""
    ID = "SEARCH_QUERY_EMPTY"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class SearchWithLinkNotSupported(NotAcceptable):
    """You cannot provide a search query and an invite link at the same time."""
    ID = "SEARCH_WITH_LINK_NOT_SUPPORTED"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class SecondsInvalid(NotAcceptable):
    """Invalid duration provided."""
    ID = "SECONDS_INVALID"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class SendAsPeerInvalid(NotAcceptable):
    """You can't send messages as the specified peer."""
    ID = "SEND_AS_PEER_INVALID"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class SendCodeUnavailable(NotAcceptable):
    """Returned when all available options for this type of number were already used (e.g. flash-call, then SMS, then this error might be returned to trigger a second resend)."""
    ID = "SEND_CODE_UNAVAILABLE"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class SendMediaInvalid(NotAcceptable):
    """The specified media is invalid."""
    ID = "SEND_MEDIA_INVALID"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class SendMessageMediaInvalid(NotAcceptable):
    """Invalid media provided."""
    ID = "SEND_MESSAGE_MEDIA_INVALID"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class SendMessageTypeInvalid(NotAcceptable):
    """The message type is invalid."""
    ID = "SEND_MESSAGE_TYPE_INVALID"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class SensitiveChangeForbidden(NotAcceptable):
    """You can't change your sensitive content settings."""
    ID = "SENSITIVE_CHANGE_FORBIDDEN"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class SessionTooFresh(NotAcceptable):
    """This session was created less than 24 hours ago, try again in {value} seconds."""
    ID = "SESSION_TOO_FRESH_X"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class SettingsInvalid(NotAcceptable):
    """Invalid settings were provided."""
    ID = "SETTINGS_INVALID"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class Sha256HashInvalid(NotAcceptable):
    """The provided SHA256 hash is invalid."""
    ID = "SHA256_HASH_INVALID"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class ShortNameInvalid(NotAcceptable):
    """The specified short name is invalid."""
    ID = "SHORT_NAME_INVALID"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class ShortNameOccupied(NotAcceptable):
    """The specified short name is already in use."""
    ID = "SHORT_NAME_OCCUPIED"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class SignInFailed(NotAcceptable):
    """Failure while signing in."""
    ID = "SIGN_IN_FAILED"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class SlotsEmpty(NotAcceptable):
    """The specified slot list is empty."""
    ID = "SLOTS_EMPTY"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class SlowmodeMultiMsgsDisabled(NotAcceptable):
    """Slowmode is enabled, you cannot forward multiple messages to this group."""
    ID = "SLOWMODE_MULTI_MSGS_DISABLED"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class SlowmodeWait(NotAcceptable):
    """Slowmode is enabled in this chat: wait {value} seconds before sending another message to this chat."""
    ID = "SLOWMODE_WAIT_X"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class SlugInvalid(NotAcceptable):
    """The specified invoice slug is invalid."""
    ID = "SLUG_INVALID"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class SmsCodeCreateFailed(NotAcceptable):
    """An error occurred while creating the SMS code."""
    ID = "SMS_CODE_CREATE_FAILED"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class SrpIdInvalid(NotAcceptable):
    """Invalid SRP ID provided."""
    ID = "SRP_ID_INVALID"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class SrpPasswordChanged(NotAcceptable):
    """Password has changed."""
    ID = "SRP_PASSWORD_CHANGED"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class StargiftExportInProgress(NotAcceptable):
    """A gift export is in progress, a detailed and localized description for the error will be emitted via an [updateServiceNotification as specified here &raquo;](https://core.telegram.org/api/errors#406-not-acceptable)."""
    ID = "STARGIFT_EXPORT_IN_PROGRESS"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class StarsFormAmountMismatch(NotAcceptable):
    """The form amount has changed, please fetch the new form using [payments.getPaymentForm](https://core.telegram.org/method/payments.getPaymentForm) and restart the process."""
    ID = "STARS_FORM_AMOUNT_MISMATCH"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class StartParamEmpty(NotAcceptable):
    """The start parameter is empty."""
    ID = "START_PARAM_EMPTY"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class StartParamInvalid(NotAcceptable):
    """Start parameter invalid."""
    ID = "START_PARAM_INVALID"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class StartParamTooLong(NotAcceptable):
    """Start parameter is too long."""
    ID = "START_PARAM_TOO_LONG"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class StickerpackStickersTooMuch(NotAcceptable):
    """There are too many stickers in this stickerpack, you can't add any more."""
    ID = "STICKERPACK_STICKERS_TOO_MUCH"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class StickersetInvalid(NotAcceptable):
    """The provided sticker set is invalid."""
    ID = "STICKERSET_INVALID"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class StickersetOwnerAnonymous(NotAcceptable):
    """Provided stickerset can't be installed as group stickerset to prevent admin deanonymization."""
    ID = "STICKERSET_OWNER_ANONYMOUS"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class StickersEmpty(NotAcceptable):
    """No sticker provided."""
    ID = "STICKERS_EMPTY"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class StickersTooMuch(NotAcceptable):
    """There are too many stickers in this stickerpack, you can't add any more."""
    ID = "STICKERS_TOO_MUCH"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class StickerDocumentInvalid(NotAcceptable):
    """The specified sticker document is invalid."""
    ID = "STICKER_DOCUMENT_INVALID"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class StickerEmojiInvalid(NotAcceptable):
    """Sticker emoji invalid."""
    ID = "STICKER_EMOJI_INVALID"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class StickerFileInvalid(NotAcceptable):
    """Sticker file invalid."""
    ID = "STICKER_FILE_INVALID"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class StickerGifDimensions(NotAcceptable):
    """The specified video sticker has invalid dimensions."""
    ID = "STICKER_GIF_DIMENSIONS"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class StickerIdInvalid(NotAcceptable):
    """The provided sticker ID is invalid."""
    ID = "STICKER_ID_INVALID"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class StickerInvalid(NotAcceptable):
    """The provided sticker is invalid."""
    ID = "STICKER_INVALID"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class StickerMimeInvalid(NotAcceptable):
    """The specified sticker MIME type is invalid."""
    ID = "STICKER_MIME_INVALID"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class StickerPngDimensions(NotAcceptable):
    """Sticker png dimensions invalid."""
    ID = "STICKER_PNG_DIMENSIONS"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class StickerPngNopng(NotAcceptable):
    """One of the specified stickers is not a valid PNG file."""
    ID = "STICKER_PNG_NOPNG"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class StickerTgsNodoc(NotAcceptable):
    """You must send the animated sticker as a document."""
    ID = "STICKER_TGS_NODOC"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class StickerTgsNotgs(NotAcceptable):
    """Invalid TGS sticker provided."""
    ID = "STICKER_TGS_NOTGS"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class StickerThumbPngNopng(NotAcceptable):
    """Incorrect stickerset thumb file provided, PNG / WEBP expected."""
    ID = "STICKER_THUMB_PNG_NOPNG"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class StickerThumbTgsNotgs(NotAcceptable):
    """Incorrect stickerset TGS thumb file provided."""
    ID = "STICKER_THUMB_TGS_NOTGS"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class StickerVideoBig(NotAcceptable):
    """The specified video sticker is too big."""
    ID = "STICKER_VIDEO_BIG"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class StickerVideoNodoc(NotAcceptable):
    """You must send the video sticker as a document."""
    ID = "STICKER_VIDEO_NODOC"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class StickerVideoNowebm(NotAcceptable):
    """The specified video sticker is not in webm format."""
    ID = "STICKER_VIDEO_NOWEBM"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class StoriesNeverCreated(NotAcceptable):
    """This peer hasn't ever posted any stories."""
    ID = "STORIES_NEVER_CREATED"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class StoriesTooMuch(NotAcceptable):
    """You have hit the maximum active stories limit as specified by the [`story_expiring_limit_*` client configuration parameters](https://core.telegram.org/api/config#story-expiring-limit-default): you should buy a [Premium](/api/premium) subscription, delete an active story, or wait for the oldest story to expire."""
    ID = "STORIES_TOO_MUCH"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class StoryIdEmpty(NotAcceptable):
    """You specified no story IDs."""
    ID = "STORY_ID_EMPTY"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class StoryIdInvalid(NotAcceptable):
    """The specified story ID is invalid."""
    ID = "STORY_ID_INVALID"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class StoryNotModified(NotAcceptable):
    """The new story information you passed is equal to the previous story information, thus it wasn't modified."""
    ID = "STORY_NOT_MODIFIED"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class StoryPeriodInvalid(NotAcceptable):
    """The specified story period is invalid for this account."""
    ID = "STORY_PERIOD_INVALID"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class StorySendFloodMonthly(NotAcceptable):
    """You've hit the monthly story limit as specified by the [`stories_sent_monthly_limit_*` client configuration parameters](https://core.telegram.org/api/config#stories-sent-monthly-limit-default): wait for the specified number of seconds before posting a new story."""
    ID = "STORY_SEND_FLOOD_MONTHLY_X"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class StorySendFloodWeekly(NotAcceptable):
    """You've hit the weekly story limit as specified by the [`stories_sent_weekly_limit_*` client configuration parameters](https://core.telegram.org/api/config#stories-sent-weekly-limit-default): wait for the specified number of seconds before posting a new story."""
    ID = "STORY_SEND_FLOOD_WEEKLY_X"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class SwitchPmTextEmpty(NotAcceptable):
    """The switch_pm.text field was empty."""
    ID = "SWITCH_PM_TEXT_EMPTY"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class TakeoutInitDelay(NotAcceptable):
    """Sorry, for security reasons, you will be able to begin downloading your data in {value} seconds. We have notified all your devices about the export request to make sure it's authorized and to give you time to react if it's not."""
    ID = "TAKEOUT_INIT_DELAY_X"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class TakeoutInvalid(NotAcceptable):
    """The specified takeout ID is invalid."""
    ID = "TAKEOUT_INVALID"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class TakeoutRequired(NotAcceptable):
    """A [takeout](https://core.telegram.org/api/takeout) session needs to be initialized first, [see here &raquo; for more info](/api/takeout)."""
    ID = "TAKEOUT_REQUIRED"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class TaskAlreadyExists(NotAcceptable):
    """An email reset was already requested."""
    ID = "TASK_ALREADY_EXISTS"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class TempAuthKeyAlreadyBound(NotAcceptable):
    """The passed temporary key is already bound to another **perm_auth_key_id**."""
    ID = "TEMP_AUTH_KEY_ALREADY_BOUND"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class TempAuthKeyEmpty(NotAcceptable):
    """No temporary auth key provided."""
    ID = "TEMP_AUTH_KEY_EMPTY"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class ThemeFileInvalid(NotAcceptable):
    """Invalid theme file provided."""
    ID = "THEME_FILE_INVALID"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class ThemeFormatInvalid(NotAcceptable):
    """Invalid theme format provided."""
    ID = "THEME_FORMAT_INVALID"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class ThemeInvalid(NotAcceptable):
    """Invalid theme provided."""
    ID = "THEME_INVALID"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class ThemeMimeInvalid(NotAcceptable):
    """The theme's MIME type is invalid."""
    ID = "THEME_MIME_INVALID"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class ThemeTitleInvalid(NotAcceptable):
    """The specified theme title is invalid."""
    ID = "THEME_TITLE_INVALID"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class TitleInvalid(NotAcceptable):
    """The specified stickerpack title is invalid."""
    ID = "TITLE_INVALID"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class TmpPasswordDisabled(NotAcceptable):
    """The temporary password is disabled."""
    ID = "TMP_PASSWORD_DISABLED"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class TokenEmpty(NotAcceptable):
    """The specified token is empty."""
    ID = "TOKEN_EMPTY"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class TokenInvalid(NotAcceptable):
    """The provided token is invalid."""
    ID = "TOKEN_INVALID"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class TokenTypeInvalid(NotAcceptable):
    """The specified token type is invalid."""
    ID = "TOKEN_TYPE_INVALID"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class TopicsEmpty(NotAcceptable):
    """You specified no topic IDs."""
    ID = "TOPICS_EMPTY"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class TopicClosed(NotAcceptable):
    """This topic was closed, you can't send messages to it anymore."""
    ID = "TOPIC_CLOSED"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class TopicCloseSeparately(NotAcceptable):
    """The `close` flag cannot be provided together with any of the other flags."""
    ID = "TOPIC_CLOSE_SEPARATELY"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class TopicDeleted(NotAcceptable):
    """The specified topic was deleted."""
    ID = "TOPIC_DELETED"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class TopicHideSeparately(NotAcceptable):
    """The `hide` flag cannot be provided together with any of the other flags."""
    ID = "TOPIC_HIDE_SEPARATELY"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class TopicIdInvalid(NotAcceptable):
    """The specified topic ID is invalid."""
    ID = "TOPIC_ID_INVALID"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class TopicNotModified(NotAcceptable):
    """The updated topic info is equal to the current topic info, nothing was changed."""
    ID = "TOPIC_NOT_MODIFIED"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class TopicTitleEmpty(NotAcceptable):
    """The specified topic title is empty."""
    ID = "TOPIC_TITLE_EMPTY"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class ToLangInvalid(NotAcceptable):
    """The specified destination language is invalid."""
    ID = "TO_LANG_INVALID"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class TranscriptionFailed(NotAcceptable):
    """Audio transcription failed."""
    ID = "TRANSCRIPTION_FAILED"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class TranslationsDisabled(NotAcceptable):
    """Translations are unavailable, a detailed and localized description for the error will be emitted via an [updateServiceNotification as specified here &raquo;](https://core.telegram.org/api/errors#406-not-acceptable)."""
    ID = "TRANSLATIONS_DISABLED"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class TtlDaysInvalid(NotAcceptable):
    """The provided TTL is invalid."""
    ID = "TTL_DAYS_INVALID"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class TtlMediaInvalid(NotAcceptable):
    """Invalid media Time To Live was provided."""
    ID = "TTL_MEDIA_INVALID"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class TtlPeriodInvalid(NotAcceptable):
    """The specified TTL period is invalid."""
    ID = "TTL_PERIOD_INVALID"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class TypesEmpty(NotAcceptable):
    """No top peer type was provided."""
    ID = "TYPES_EMPTY"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class UntilDateInvalid(NotAcceptable):
    """Invalid until date provided."""
    ID = "UNTIL_DATE_INVALID"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class UpdateAppToLogin(NotAcceptable):
    """Please update your client to login."""
    ID = "UPDATE_APP_TO_LOGIN"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class UrlInvalid(NotAcceptable):
    """Invalid URL provided."""
    ID = "URL_INVALID"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class UsageLimitInvalid(NotAcceptable):
    """The specified usage limit is invalid."""
    ID = "USAGE_LIMIT_INVALID"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class UsernamesActiveTooMuch(NotAcceptable):
    """The maximum number of active usernames was reached."""
    ID = "USERNAMES_ACTIVE_TOO_MUCH"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class UsernameInvalid(NotAcceptable):
    """The provided username is not valid."""
    ID = "USERNAME_INVALID"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class UsernameNotModified(NotAcceptable):
    """The username was not modified."""
    ID = "USERNAME_NOT_MODIFIED"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class UsernameNotOccupied(NotAcceptable):
    """The provided username is not occupied."""
    ID = "USERNAME_NOT_OCCUPIED"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class UsernameOccupied(NotAcceptable):
    """The provided username is already occupied."""
    ID = "USERNAME_OCCUPIED"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class UsernamePurchaseAvailable(NotAcceptable):
    """The specified username can be purchased on https://fragment.com."""
    ID = "USERNAME_PURCHASE_AVAILABLE"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class UserpicPrivacyRequired(NotAcceptable):
    """You need to disable privacy settings for your profile picture in order to make your geolocation public."""
    ID = "USERPIC_PRIVACY_REQUIRED"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class UserpicUploadRequired(NotAcceptable):
    """You must have a profile picture to publish your geolocation."""
    ID = "USERPIC_UPLOAD_REQUIRED"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class UsersTooFew(NotAcceptable):
    """Not enough users (to create a chat, for example)."""
    ID = "USERS_TOO_FEW"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class UsersTooMuch(NotAcceptable):
    """The maximum number of users has been exceeded (to create a chat, for example)."""
    ID = "USERS_TOO_MUCH"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class UserAdminInvalid(NotAcceptable):
    """You're not an admin."""
    ID = "USER_ADMIN_INVALID"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class UserAlreadyInvited(NotAcceptable):
    """You have already invited this user."""
    ID = "USER_ALREADY_INVITED"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class UserAlreadyParticipant(NotAcceptable):
    """The user is already in the group."""
    ID = "USER_ALREADY_PARTICIPANT"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class UserBannedInChannel(NotAcceptable):
    """You're banned from sending messages in supergroups/channels."""
    ID = "USER_BANNED_IN_CHANNEL"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class UserBlocked(NotAcceptable):
    """User blocked."""
    ID = "USER_BLOCKED"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class UserBot(NotAcceptable):
    """Bots can only be admins in channels."""
    ID = "USER_BOT"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class UserBotInvalid(NotAcceptable):
    """User accounts must provide the `bot` method parameter when calling this method. If there is no such method parameter, this method can only be invoked by bot accounts."""
    ID = "USER_BOT_INVALID"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class UserBotRequired(NotAcceptable):
    """This method can only be called by a bot."""
    ID = "USER_BOT_REQUIRED"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class UserChannelsTooMuch(NotAcceptable):
    """One of the users you tried to add is already in too many channels/supergroups."""
    ID = "USER_CHANNELS_TOO_MUCH"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class UserCreator(NotAcceptable):
    """You can't leave this channel, because you're its creator."""
    ID = "USER_CREATOR"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class UserDeleted(NotAcceptable):
    """You can't send this secret message because the other participant deleted their account."""
    ID = "USER_DELETED"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class UserIdInvalid(NotAcceptable):
    """The provided user ID is invalid."""
    ID = "USER_ID_INVALID"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class UserInvalid(NotAcceptable):
    """Invalid user provided."""
    ID = "USER_INVALID"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class UserIsBlocked(NotAcceptable):
    """You were blocked by this user."""
    ID = "USER_IS_BLOCKED"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class UserIsBot(NotAcceptable):
    """Bots can't send messages to other bots."""
    ID = "USER_IS_BOT"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class UserKicked(NotAcceptable):
    """This user was kicked from this supergroup/channel."""
    ID = "USER_KICKED"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class UserNotMutualContact(NotAcceptable):
    """The provided user is not a mutual contact."""
    ID = "USER_NOT_MUTUAL_CONTACT"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class UserNotParticipant(NotAcceptable):
    """You're not a member of this supergroup/channel."""
    ID = "USER_NOT_PARTICIPANT"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class UserPrivacyRestricted(NotAcceptable):
    """The user's privacy settings do not allow you to do this."""
    ID = "USER_PRIVACY_RESTRICTED"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class UserPublicMissing(NotAcceptable):
    """Cannot generate a link to stories posted by a peer without a username."""
    ID = "USER_PUBLIC_MISSING"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class UserRestricted(NotAcceptable):
    """You're spamreported, you can't create channels or chats."""
    ID = "USER_RESTRICTED"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class UserVolumeInvalid(NotAcceptable):
    """The specified user volume is invalid."""
    ID = "USER_VOLUME_INVALID"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class VenueIdInvalid(NotAcceptable):
    """The specified venue ID is invalid."""
    ID = "VENUE_ID_INVALID"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class VideoContentTypeInvalid(NotAcceptable):
    """The video's content type is invalid."""
    ID = "VIDEO_CONTENT_TYPE_INVALID"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class VideoFileInvalid(NotAcceptable):
    """The specified video file is invalid."""
    ID = "VIDEO_FILE_INVALID"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class VideoTitleEmpty(NotAcceptable):
    """The specified video title is empty."""
    ID = "VIDEO_TITLE_EMPTY"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class VoiceMessagesForbidden(NotAcceptable):
    """This user's privacy settings forbid you from sending voice messages."""
    ID = "VOICE_MESSAGES_FORBIDDEN"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class WallpaperFileInvalid(NotAcceptable):
    """The specified wallpaper file is invalid."""
    ID = "WALLPAPER_FILE_INVALID"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class WallpaperInvalid(NotAcceptable):
    """The specified wallpaper is invalid."""
    ID = "WALLPAPER_INVALID"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class WallpaperMimeInvalid(NotAcceptable):
    """The specified wallpaper MIME type is invalid."""
    ID = "WALLPAPER_MIME_INVALID"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class WallpaperNotFound(NotAcceptable):
    """The specified wallpaper could not be found."""
    ID = "WALLPAPER_NOT_FOUND"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class WcConvertUrlInvalid(NotAcceptable):
    """WC convert URL invalid."""
    ID = "WC_CONVERT_URL_INVALID"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class WebdocumentInvalid(NotAcceptable):
    """Invalid webdocument URL provided."""
    ID = "WEBDOCUMENT_INVALID"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class WebdocumentMimeInvalid(NotAcceptable):
    """Invalid webdocument mime type provided."""
    ID = "WEBDOCUMENT_MIME_INVALID"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class WebdocumentSizeTooBig(NotAcceptable):
    """Webdocument is too big!"""
    ID = "WEBDOCUMENT_SIZE_TOO_BIG"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class WebdocumentUrlInvalid(NotAcceptable):
    """The specified webdocument URL is invalid."""
    ID = "WEBDOCUMENT_URL_INVALID"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class WebpageCurlFailed(NotAcceptable):
    """Failure while fetching the webpage with cURL."""
    ID = "WEBPAGE_CURL_FAILED"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class WebpageMediaEmpty(NotAcceptable):
    """Webpage media empty."""
    ID = "WEBPAGE_MEDIA_EMPTY"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class WebpageNotFound(NotAcceptable):
    """A preview for the specified webpage `url` could not be generated."""
    ID = "WEBPAGE_NOT_FOUND"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class WebpageUrlInvalid(NotAcceptable):
    """The specified webpage `url` is invalid."""
    ID = "WEBPAGE_URL_INVALID"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class WebpushAuthInvalid(NotAcceptable):
    """The specified web push authentication secret is invalid."""
    ID = "WEBPUSH_AUTH_INVALID"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class WebpushKeyInvalid(NotAcceptable):
    """The specified web push elliptic curve Diffie-Hellman public key is invalid."""
    ID = "WEBPUSH_KEY_INVALID"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class WebpushTokenInvalid(NotAcceptable):
    """The specified web push token is invalid."""
    ID = "WEBPUSH_TOKEN_INVALID"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class YouBlockedUser(NotAcceptable):
    """You blocked this user."""
    ID = "YOU_BLOCKED_USER"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


