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


class InputMediaUploadedDocument(TLObject):  # type: ignore
    """Telegram API type.

    Constructor of :obj:`~geezlibs.raw.base.InputMedia`.

    Details:
        - Layer: ``148``
        - ID: ``5B38C6C1``

    Parameters:
        file (:obj:`InputFile <geezlibs.raw.base.InputFile>`):
            N/A

        mime_type (``str``):
            N/A

        attributes (List of :obj:`DocumentAttribute <geezlibs.raw.base.DocumentAttribute>`):
            N/A

        nosound_video (``bool``, *optional*):
            N/A

        force_file (``bool``, *optional*):
            N/A

        thumb (:obj:`InputFile <geezlibs.raw.base.InputFile>`, *optional*):
            N/A

        stickers (List of :obj:`InputDocument <geezlibs.raw.base.InputDocument>`, *optional*):
            N/A

        ttl_seconds (``int`` ``32-bit``, *optional*):
            N/A

    """

    __slots__: List[str] = ["file", "mime_type", "attributes", "nosound_video", "force_file", "thumb", "stickers", "ttl_seconds"]

    ID = 0x5b38c6c1
    QUALNAME = "types.InputMediaUploadedDocument"

    def __init__(self, *, file: "raw.base.InputFile", mime_type: str, attributes: List["raw.base.DocumentAttribute"], nosound_video: Optional[bool] = None, force_file: Optional[bool] = None, thumb: "raw.base.InputFile" = None, stickers: Optional[List["raw.base.InputDocument"]] = None, ttl_seconds: Optional[int] = None) -> None:
        self.file = file  # InputFile
        self.mime_type = mime_type  # string
        self.attributes = attributes  # Vector<DocumentAttribute>
        self.nosound_video = nosound_video  # flags.3?true
        self.force_file = force_file  # flags.4?true
        self.thumb = thumb  # flags.2?InputFile
        self.stickers = stickers  # flags.0?Vector<InputDocument>
        self.ttl_seconds = ttl_seconds  # flags.1?int

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "InputMediaUploadedDocument":
        
        flags = Int.read(b)
        
        nosound_video = True if flags & (1 << 3) else False
        force_file = True if flags & (1 << 4) else False
        file = TLObject.read(b)
        
        thumb = TLObject.read(b) if flags & (1 << 2) else None
        
        mime_type = String.read(b)
        
        attributes = TLObject.read(b)
        
        stickers = TLObject.read(b) if flags & (1 << 0) else []
        
        ttl_seconds = Int.read(b) if flags & (1 << 1) else None
        return InputMediaUploadedDocument(file=file, mime_type=mime_type, attributes=attributes, nosound_video=nosound_video, force_file=force_file, thumb=thumb, stickers=stickers, ttl_seconds=ttl_seconds)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        flags = 0
        flags |= (1 << 3) if self.nosound_video else 0
        flags |= (1 << 4) if self.force_file else 0
        flags |= (1 << 2) if self.thumb is not None else 0
        flags |= (1 << 0) if self.stickers else 0
        flags |= (1 << 1) if self.ttl_seconds is not None else 0
        b.write(Int(flags))
        
        b.write(self.file.write())
        
        if self.thumb is not None:
            b.write(self.thumb.write())
        
        b.write(String(self.mime_type))
        
        b.write(Vector(self.attributes))
        
        if self.stickers is not None:
            b.write(Vector(self.stickers))
        
        if self.ttl_seconds is not None:
            b.write(Int(self.ttl_seconds))
        
        return b.getvalue()
