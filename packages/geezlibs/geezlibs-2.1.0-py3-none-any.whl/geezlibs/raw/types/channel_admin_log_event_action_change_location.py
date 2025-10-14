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


class ChannelAdminLogEventActionChangeLocation(TLObject):  # type: ignore
    """Telegram API type.

    Constructor of :obj:`~geezlibs.raw.base.ChannelAdminLogEventAction`.

    Details:
        - Layer: ``148``
        - ID: ``E6B76AE``

    Parameters:
        prev_value (:obj:`ChannelLocation <geezlibs.raw.base.ChannelLocation>`):
            N/A

        new_value (:obj:`ChannelLocation <geezlibs.raw.base.ChannelLocation>`):
            N/A

    """

    __slots__: List[str] = ["prev_value", "new_value"]

    ID = 0xe6b76ae
    QUALNAME = "types.ChannelAdminLogEventActionChangeLocation"

    def __init__(self, *, prev_value: "raw.base.ChannelLocation", new_value: "raw.base.ChannelLocation") -> None:
        self.prev_value = prev_value  # ChannelLocation
        self.new_value = new_value  # ChannelLocation

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "ChannelAdminLogEventActionChangeLocation":
        # No flags
        
        prev_value = TLObject.read(b)
        
        new_value = TLObject.read(b)
        
        return ChannelAdminLogEventActionChangeLocation(prev_value=prev_value, new_value=new_value)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        # No flags
        
        b.write(self.prev_value.write())
        
        b.write(self.new_value.write())
        
        return b.getvalue()
