# GeezLibs - Telegram MTProto API Client Library for Python.
# Copyright (C) 2022-2023 izzy<https://github.com/hitokizzy>
#
# This file is part of GeezLibs.
#
# GeezLibs is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# GeezLibs is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with GeezLibs.  If not, see <http://www.gnu.org/licenses/>.

from ..rpc_error import RPCError


class ServiceUnavailable(RPCError):
    """Service Unavailable"""
    CODE = 503
    """``int``: RPC Error Code"""
    NAME = __doc__


class ApiCallError(ServiceUnavailable):
    """Telegram is having internal problems. Please try again later."""
    ID = "ApiCallError"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


class Timeout(ServiceUnavailable):
    """Telegram is having internal problems. Please try again later."""
    ID = "Timeout"
    """``str``: RPC Error ID"""
    MESSAGE = __doc__


