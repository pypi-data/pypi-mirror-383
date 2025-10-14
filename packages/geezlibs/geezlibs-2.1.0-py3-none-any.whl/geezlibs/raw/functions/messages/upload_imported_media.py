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


class UploadImportedMedia(TLObject):  # type: ignore
    """Telegram API function.

    Details:
        - Layer: ``148``
        - ID: ``2A862092``

    Parameters:
        peer (:obj:`InputPeer <geezlibs.raw.base.InputPeer>`):
            N/A

        import_id (``int`` ``64-bit``):
            N/A

        file_name (``str``):
            N/A

        media (:obj:`InputMedia <geezlibs.raw.base.InputMedia>`):
            N/A

    Returns:
        :obj:`MessageMedia <geezlibs.raw.base.MessageMedia>`
    """

    __slots__: List[str] = ["peer", "import_id", "file_name", "media"]

    ID = 0x2a862092
    QUALNAME = "functions.messages.UploadImportedMedia"

    def __init__(self, *, peer: "raw.base.InputPeer", import_id: int, file_name: str, media: "raw.base.InputMedia") -> None:
        self.peer = peer  # InputPeer
        self.import_id = import_id  # long
        self.file_name = file_name  # string
        self.media = media  # InputMedia

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "UploadImportedMedia":
        # No flags
        
        peer = TLObject.read(b)
        
        import_id = Long.read(b)
        
        file_name = String.read(b)
        
        media = TLObject.read(b)
        
        return UploadImportedMedia(peer=peer, import_id=import_id, file_name=file_name, media=media)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        # No flags
        
        b.write(self.peer.write())
        
        b.write(Long(self.import_id))
        
        b.write(String(self.file_name))
        
        b.write(self.media.write())
        
        return b.getvalue()
