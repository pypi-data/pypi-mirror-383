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


class Flood(RPCError):
    """Flood"""
    CODE = 420
    """``int``: RPC Error Code"""
    NAME = __doc__


class TwoFaConfirmWait(Flood):
    """Since this account is active and protected by a 2FA password, we will delete it in 1 week for security purposes. You can cancel this process at any time, you'll be able to reset your account in {value} seconds."""
    ID = "2FA_CONFIRM_WAIT_X"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class AddressInvalid(Flood):
    """The specified geopoint address is invalid."""
    ID = "ADDRESS_INVALID"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class FloodPremiumWait(Flood):
    """Please wait {value} seconds before repeating the action, or purchase a [Telegram Premium subscription](https://core.telegram.org/api/premium) to remove this rate limit."""
    ID = "FLOOD_PREMIUM_WAIT_X"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class FloodTestPhoneWait(Flood):
    """A wait of {value} seconds is required in the test servers"""
    ID = "FLOOD_TEST_PHONE_WAIT_X"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class FloodWait(Flood):
    """Please wait {value} seconds before repeating the action."""
    ID = "FLOOD_WAIT_X"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class FrozenMethodInvalid(Flood):
    """The current account is [frozen](https://core.telegram.org/api/auth#frozen-accounts), and thus cannot execute the specified action."""
    ID = "FROZEN_METHOD_INVALID"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class PremiumSubActiveUntil(Flood):
    """You already have a premium subscription active until unixtime {value} ."""
    ID = "PREMIUM_SUB_ACTIVE_UNTIL_X"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class SlowmodeWait(Flood):
    """Slowmode is enabled in this chat: wait {value} seconds before sending another message to this chat."""
    ID = "SLOWMODE_WAIT_X"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class TakeoutInitDelay(Flood):
    """Sorry, for security reasons, you will be able to begin downloading your data in {value} seconds. We have notified all your devices about the export request to make sure it's authorized and to give you time to react if it's not."""
    ID = "TAKEOUT_INIT_DELAY_X"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


