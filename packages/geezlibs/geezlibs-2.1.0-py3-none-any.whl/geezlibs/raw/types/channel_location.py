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


class ChannelLocation(TLObject):  # type: ignore
    """Telegram API type.

    Constructor of :obj:`~geezlibs.raw.base.ChannelLocation`.

    Details:
        - Layer: ``148``
        - ID: ``209B82DB``

    Parameters:
        geo_point (:obj:`GeoPoint <geezlibs.raw.base.GeoPoint>`):
            N/A

        address (``str``):
            N/A

    """

    __slots__: List[str] = ["geo_point", "address"]

    ID = 0x209b82db
    QUALNAME = "types.ChannelLocation"

    def __init__(self, *, geo_point: "raw.base.GeoPoint", address: str) -> None:
        self.geo_point = geo_point  # GeoPoint
        self.address = address  # string

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "ChannelLocation":
        # No flags
        
        geo_point = TLObject.read(b)
        
        address = String.read(b)
        
        return ChannelLocation(geo_point=geo_point, address=address)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        # No flags
        
        b.write(self.geo_point.write())
        
        b.write(String(self.address))
        
        return b.getvalue()
