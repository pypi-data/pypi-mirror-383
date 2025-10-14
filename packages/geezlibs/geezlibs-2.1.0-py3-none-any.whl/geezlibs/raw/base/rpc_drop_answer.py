#  GeezLibs - Telegram MTProto API Client Library for Python.
#  Copyright (C) 2022-2023 izzy<https://github.com/hitokizzy>
#
#  This file is part of GeezLibs.
#
#  GeezLibs is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Affero General Public License as published
#  by the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  GeezLibs is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Affero General Public License for more details.
#
#  You should have received a copy of the GNU Affero General Public License
#  along with GeezLibs.  If not, see <http://www.gnu.org/licenses/>.

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #

from typing import Union
from geezlibs import raw
from geezlibs.raw.core import TLObject

RpcDropAnswer = Union[raw.types.RpcAnswerDropped, raw.types.RpcAnswerDroppedRunning, raw.types.RpcAnswerUnknown]


# noinspection PyRedeclaration
class RpcDropAnswer:  # type: ignore
    """Telegram API base type.

    Constructors:
        This base type has 3 constructors available.

        .. currentmodule:: geezlibs.raw.types

        .. autosummary::
            :nosignatures:

            RpcAnswerDropped
            RpcAnswerDroppedRunning
            RpcAnswerUnknown

    Functions:
        This object can be returned by 1 function.

        .. currentmodule:: geezlibs.raw.functions

        .. autosummary::
            :nosignatures:

            RpcDropAnswer
    """

    QUALNAME = "geezlibs.raw.base.RpcDropAnswer"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. "
                        "More info: https://docs.pyrogram.org/telegram/base/rpc-drop-answer")
