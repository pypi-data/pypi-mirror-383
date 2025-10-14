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


class MessageMediaVenue(TLObject):  # type: ignore
    """Telegram API type.

    Constructor of :obj:`~geezlibs.raw.base.MessageMedia`.

    Details:
        - Layer: ``148``
        - ID: ``2EC0533F``

    Parameters:
        geo (:obj:`GeoPoint <geezlibs.raw.base.GeoPoint>`):
            N/A

        title (``str``):
            N/A

        address (``str``):
            N/A

        provider (``str``):
            N/A

        venue_id (``str``):
            N/A

        venue_type (``str``):
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

    __slots__: List[str] = ["geo", "title", "address", "provider", "venue_id", "venue_type"]

    ID = 0x2ec0533f
    QUALNAME = "types.MessageMediaVenue"

    def __init__(self, *, geo: "raw.base.GeoPoint", title: str, address: str, provider: str, venue_id: str, venue_type: str) -> None:
        self.geo = geo  # GeoPoint
        self.title = title  # string
        self.address = address  # string
        self.provider = provider  # string
        self.venue_id = venue_id  # string
        self.venue_type = venue_type  # string

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "MessageMediaVenue":
        # No flags
        
        geo = TLObject.read(b)
        
        title = String.read(b)
        
        address = String.read(b)
        
        provider = String.read(b)
        
        venue_id = String.read(b)
        
        venue_type = String.read(b)
        
        return MessageMediaVenue(geo=geo, title=title, address=address, provider=provider, venue_id=venue_id, venue_type=venue_type)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        # No flags
        
        b.write(self.geo.write())
        
        b.write(String(self.title))
        
        b.write(String(self.address))
        
        b.write(String(self.provider))
        
        b.write(String(self.venue_id))
        
        b.write(String(self.venue_type))
        
        return b.getvalue()
