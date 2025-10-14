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


class LoginTokenMigrateTo(TLObject):  # type: ignore
    """Telegram API type.

    Constructor of :obj:`~geezlibs.raw.base.auth.LoginToken`.

    Details:
        - Layer: ``148``
        - ID: ``68E9916``

    Parameters:
        dc_id (``int`` ``32-bit``):
            N/A

        token (``bytes``):
            N/A

    Functions:
        This object can be returned by 2 functions.

        .. currentmodule:: geezlibs.raw.functions

        .. autosummary::
            :nosignatures:

            auth.ExportLoginToken
            auth.ImportLoginToken
    """

    __slots__: List[str] = ["dc_id", "token"]

    ID = 0x68e9916
    QUALNAME = "types.auth.LoginTokenMigrateTo"

    def __init__(self, *, dc_id: int, token: bytes) -> None:
        self.dc_id = dc_id  # int
        self.token = token  # bytes

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "LoginTokenMigrateTo":
        # No flags
        
        dc_id = Int.read(b)
        
        token = Bytes.read(b)
        
        return LoginTokenMigrateTo(dc_id=dc_id, token=token)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        # No flags
        
        b.write(Int(self.dc_id))
        
        b.write(Bytes(self.token))
        
        return b.getvalue()
