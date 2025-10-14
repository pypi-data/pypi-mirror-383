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


class MessageMediaGame(TLObject):  # type: ignore
    """Telegram API type.

    Constructor of :obj:`~geezlibs.raw.base.MessageMedia`.

    Details:
        - Layer: ``148``
        - ID: ``FDB19008``

    Parameters:
        game (:obj:`Game <geezlibs.raw.base.Game>`):
            N/A

    Functions:
        This object can be returned by 3 functions.

        .. currentmodule:: geezlibs.raw.functions

        .. autosummary::
            :nosignatures:

            messages.GetWebPagePreview
            messages.UploadMedia
            messages.UploadImportedMedia
    """

    __slots__: List[str] = ["game"]

    ID = 0xfdb19008
    QUALNAME = "types.MessageMediaGame"

    def __init__(self, *, game: "raw.base.Game") -> None:
        self.game = game  # Game

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "MessageMediaGame":
        # No flags
        
        game = TLObject.read(b)
        
        return MessageMediaGame(game=game)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        # No flags
        
        b.write(self.game.write())
        
        return b.getvalue()
