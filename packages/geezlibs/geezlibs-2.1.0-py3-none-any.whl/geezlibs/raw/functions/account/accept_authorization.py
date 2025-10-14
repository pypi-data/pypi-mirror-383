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


class AcceptAuthorization(TLObject):  # type: ignore
    """Telegram API function.

    Details:
        - Layer: ``148``
        - ID: ``F3ED4C73``

    Parameters:
        bot_id (``int`` ``64-bit``):
            N/A

        scope (``str``):
            N/A

        public_key (``str``):
            N/A

        value_hashes (List of :obj:`SecureValueHash <geezlibs.raw.base.SecureValueHash>`):
            N/A

        credentials (:obj:`SecureCredentialsEncrypted <geezlibs.raw.base.SecureCredentialsEncrypted>`):
            N/A

    Returns:
        ``bool``
    """

    __slots__: List[str] = ["bot_id", "scope", "public_key", "value_hashes", "credentials"]

    ID = 0xf3ed4c73
    QUALNAME = "functions.account.AcceptAuthorization"

    def __init__(self, *, bot_id: int, scope: str, public_key: str, value_hashes: List["raw.base.SecureValueHash"], credentials: "raw.base.SecureCredentialsEncrypted") -> None:
        self.bot_id = bot_id  # long
        self.scope = scope  # string
        self.public_key = public_key  # string
        self.value_hashes = value_hashes  # Vector<SecureValueHash>
        self.credentials = credentials  # SecureCredentialsEncrypted

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "AcceptAuthorization":
        # No flags
        
        bot_id = Long.read(b)
        
        scope = String.read(b)
        
        public_key = String.read(b)
        
        value_hashes = TLObject.read(b)
        
        credentials = TLObject.read(b)
        
        return AcceptAuthorization(bot_id=bot_id, scope=scope, public_key=public_key, value_hashes=value_hashes, credentials=credentials)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        # No flags
        
        b.write(Long(self.bot_id))
        
        b.write(String(self.scope))
        
        b.write(String(self.public_key))
        
        b.write(Vector(self.value_hashes))
        
        b.write(self.credentials.write())
        
        return b.getvalue()
