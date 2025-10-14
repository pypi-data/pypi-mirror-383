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


class PasswordSettings(TLObject):  # type: ignore
    """Telegram API type.

    Constructor of :obj:`~geezlibs.raw.base.account.PasswordSettings`.

    Details:
        - Layer: ``148``
        - ID: ``9A5C33E5``

    Parameters:
        email (``str``, *optional*):
            N/A

        secure_settings (:obj:`SecureSecretSettings <geezlibs.raw.base.SecureSecretSettings>`, *optional*):
            N/A

    Functions:
        This object can be returned by 1 function.

        .. currentmodule:: geezlibs.raw.functions

        .. autosummary::
            :nosignatures:

            account.GetPasswordSettings
    """

    __slots__: List[str] = ["email", "secure_settings"]

    ID = 0x9a5c33e5
    QUALNAME = "types.account.PasswordSettings"

    def __init__(self, *, email: Optional[str] = None, secure_settings: "raw.base.SecureSecretSettings" = None) -> None:
        self.email = email  # flags.0?string
        self.secure_settings = secure_settings  # flags.1?SecureSecretSettings

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "PasswordSettings":
        
        flags = Int.read(b)
        
        email = String.read(b) if flags & (1 << 0) else None
        secure_settings = TLObject.read(b) if flags & (1 << 1) else None
        
        return PasswordSettings(email=email, secure_settings=secure_settings)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        flags = 0
        flags |= (1 << 0) if self.email is not None else 0
        flags |= (1 << 1) if self.secure_settings is not None else 0
        b.write(Int(flags))
        
        if self.email is not None:
            b.write(String(self.email))
        
        if self.secure_settings is not None:
            b.write(self.secure_settings.write())
        
        return b.getvalue()
