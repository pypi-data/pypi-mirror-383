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


class UpdateBotCommands(TLObject):  # type: ignore
    """Telegram API type.

    Constructor of :obj:`~geezlibs.raw.base.Update`.

    Details:
        - Layer: ``148``
        - ID: ``4D712F2E``

    Parameters:
        peer (:obj:`Peer <geezlibs.raw.base.Peer>`):
            N/A

        bot_id (``int`` ``64-bit``):
            N/A

        commands (List of :obj:`BotCommand <geezlibs.raw.base.BotCommand>`):
            N/A

    """

    __slots__: List[str] = ["peer", "bot_id", "commands"]

    ID = 0x4d712f2e
    QUALNAME = "types.UpdateBotCommands"

    def __init__(self, *, peer: "raw.base.Peer", bot_id: int, commands: List["raw.base.BotCommand"]) -> None:
        self.peer = peer  # Peer
        self.bot_id = bot_id  # long
        self.commands = commands  # Vector<BotCommand>

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "UpdateBotCommands":
        # No flags
        
        peer = TLObject.read(b)
        
        bot_id = Long.read(b)
        
        commands = TLObject.read(b)
        
        return UpdateBotCommands(peer=peer, bot_id=bot_id, commands=commands)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        # No flags
        
        b.write(self.peer.write())
        
        b.write(Long(self.bot_id))
        
        b.write(Vector(self.commands))
        
        return b.getvalue()
