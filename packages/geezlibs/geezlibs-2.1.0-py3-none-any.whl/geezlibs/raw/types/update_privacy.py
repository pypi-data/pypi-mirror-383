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


class UpdatePrivacy(TLObject):  # type: ignore
    """Telegram API type.

    Constructor of :obj:`~geezlibs.raw.base.Update`.

    Details:
        - Layer: ``148``
        - ID: ``EE3B272A``

    Parameters:
        key (:obj:`PrivacyKey <geezlibs.raw.base.PrivacyKey>`):
            N/A

        rules (List of :obj:`PrivacyRule <geezlibs.raw.base.PrivacyRule>`):
            N/A

    """

    __slots__: List[str] = ["key", "rules"]

    ID = 0xee3b272a
    QUALNAME = "types.UpdatePrivacy"

    def __init__(self, *, key: "raw.base.PrivacyKey", rules: List["raw.base.PrivacyRule"]) -> None:
        self.key = key  # PrivacyKey
        self.rules = rules  # Vector<PrivacyRule>

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "UpdatePrivacy":
        # No flags
        
        key = TLObject.read(b)
        
        rules = TLObject.read(b)
        
        return UpdatePrivacy(key=key, rules=rules)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        # No flags
        
        b.write(self.key.write())
        
        b.write(Vector(self.rules))
        
        return b.getvalue()
