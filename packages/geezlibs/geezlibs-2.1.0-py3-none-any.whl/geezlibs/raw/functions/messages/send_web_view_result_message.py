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

from io import BytesIO

from geezlibs.raw.core.primitives import Int, Long, Int128, Int256, Bool, Bytes, String, Double, Vector
from geezlibs.raw.core import TLObject
from geezlibs import raw
from typing import List, Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


class SendWebViewResultMessage(TLObject):  # type: ignore
    """Telegram API function.

    Details:
        - Layer: ``148``
        - ID: ``A4314F5``

    Parameters:
        bot_query_id (``str``):
            N/A

        result (:obj:`InputBotInlineResult <geezlibs.raw.base.InputBotInlineResult>`):
            N/A

    Returns:
        :obj:`WebViewMessageSent <geezlibs.raw.base.WebViewMessageSent>`
    """

    __slots__: List[str] = ["bot_query_id", "result"]

    ID = 0xa4314f5
    QUALNAME = "functions.messages.SendWebViewResultMessage"

    def __init__(self, *, bot_query_id: str, result: "raw.base.InputBotInlineResult") -> None:
        self.bot_query_id = bot_query_id  # string
        self.result = result  # InputBotInlineResult

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "SendWebViewResultMessage":
        # No flags
        
        bot_query_id = String.read(b)
        
        result = TLObject.read(b)
        
        return SendWebViewResultMessage(bot_query_id=bot_query_id, result=result)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        # No flags
        
        b.write(String(self.bot_query_id))
        
        b.write(self.result.write())
        
        return b.getvalue()
