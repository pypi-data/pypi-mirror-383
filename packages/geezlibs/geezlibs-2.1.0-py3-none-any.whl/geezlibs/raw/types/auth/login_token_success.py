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


class LoginTokenSuccess(TLObject):  # type: ignore
    """Telegram API type.

    Constructor of :obj:`~geezlibs.raw.base.auth.LoginToken`.

    Details:
        - Layer: ``148``
        - ID: ``390D5C5E``

    Parameters:
        authorization (:obj:`auth.Authorization <geezlibs.raw.base.auth.Authorization>`):
            N/A

    Functions:
        This object can be returned by 2 functions.

        .. currentmodule:: geezlibs.raw.functions

        .. autosummary::
            :nosignatures:

            auth.ExportLoginToken
            auth.ImportLoginToken
    """

    __slots__: List[str] = ["authorization"]

    ID = 0x390d5c5e
    QUALNAME = "types.auth.LoginTokenSuccess"

    def __init__(self, *, authorization: "raw.base.auth.Authorization") -> None:
        self.authorization = authorization  # auth.Authorization

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "LoginTokenSuccess":
        # No flags
        
        authorization = TLObject.read(b)
        
        return LoginTokenSuccess(authorization=authorization)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        # No flags
        
        b.write(self.authorization.write())
        
        return b.getvalue()
