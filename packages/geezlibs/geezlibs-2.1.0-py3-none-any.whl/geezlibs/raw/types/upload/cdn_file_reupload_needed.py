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


class CdnFileReuploadNeeded(TLObject):  # type: ignore
    """Telegram API type.

    Constructor of :obj:`~geezlibs.raw.base.upload.CdnFile`.

    Details:
        - Layer: ``148``
        - ID: ``EEA8E46E``

    Parameters:
        request_token (``bytes``):
            N/A

    Functions:
        This object can be returned by 1 function.

        .. currentmodule:: geezlibs.raw.functions

        .. autosummary::
            :nosignatures:

            upload.GetCdnFile
    """

    __slots__: List[str] = ["request_token"]

    ID = 0xeea8e46e
    QUALNAME = "types.upload.CdnFileReuploadNeeded"

    def __init__(self, *, request_token: bytes) -> None:
        self.request_token = request_token  # bytes

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "CdnFileReuploadNeeded":
        # No flags
        
        request_token = Bytes.read(b)
        
        return CdnFileReuploadNeeded(request_token=request_token)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        # No flags
        
        b.write(Bytes(self.request_token))
        
        return b.getvalue()
