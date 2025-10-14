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


class PeerNotifySettings(TLObject):  # type: ignore
    """Telegram API type.

    Constructor of :obj:`~geezlibs.raw.base.PeerNotifySettings`.

    Details:
        - Layer: ``148``
        - ID: ``A83B0426``

    Parameters:
        show_previews (``bool``, *optional*):
            N/A

        silent (``bool``, *optional*):
            N/A

        mute_until (``int`` ``32-bit``, *optional*):
            N/A

        ios_sound (:obj:`NotificationSound <geezlibs.raw.base.NotificationSound>`, *optional*):
            N/A

        android_sound (:obj:`NotificationSound <geezlibs.raw.base.NotificationSound>`, *optional*):
            N/A

        other_sound (:obj:`NotificationSound <geezlibs.raw.base.NotificationSound>`, *optional*):
            N/A

    Functions:
        This object can be returned by 1 function.

        .. currentmodule:: geezlibs.raw.functions

        .. autosummary::
            :nosignatures:

            account.GetNotifySettings
    """

    __slots__: List[str] = ["show_previews", "silent", "mute_until", "ios_sound", "android_sound", "other_sound"]

    ID = 0xa83b0426
    QUALNAME = "types.PeerNotifySettings"

    def __init__(self, *, show_previews: Optional[bool] = None, silent: Optional[bool] = None, mute_until: Optional[int] = None, ios_sound: "raw.base.NotificationSound" = None, android_sound: "raw.base.NotificationSound" = None, other_sound: "raw.base.NotificationSound" = None) -> None:
        self.show_previews = show_previews  # flags.0?Bool
        self.silent = silent  # flags.1?Bool
        self.mute_until = mute_until  # flags.2?int
        self.ios_sound = ios_sound  # flags.3?NotificationSound
        self.android_sound = android_sound  # flags.4?NotificationSound
        self.other_sound = other_sound  # flags.5?NotificationSound

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "PeerNotifySettings":
        
        flags = Int.read(b)
        
        show_previews = Bool.read(b) if flags & (1 << 0) else None
        silent = Bool.read(b) if flags & (1 << 1) else None
        mute_until = Int.read(b) if flags & (1 << 2) else None
        ios_sound = TLObject.read(b) if flags & (1 << 3) else None
        
        android_sound = TLObject.read(b) if flags & (1 << 4) else None
        
        other_sound = TLObject.read(b) if flags & (1 << 5) else None
        
        return PeerNotifySettings(show_previews=show_previews, silent=silent, mute_until=mute_until, ios_sound=ios_sound, android_sound=android_sound, other_sound=other_sound)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        flags = 0
        flags |= (1 << 0) if self.show_previews is not None else 0
        flags |= (1 << 1) if self.silent is not None else 0
        flags |= (1 << 2) if self.mute_until is not None else 0
        flags |= (1 << 3) if self.ios_sound is not None else 0
        flags |= (1 << 4) if self.android_sound is not None else 0
        flags |= (1 << 5) if self.other_sound is not None else 0
        b.write(Int(flags))
        
        if self.show_previews is not None:
            b.write(Bool(self.show_previews))
        
        if self.silent is not None:
            b.write(Bool(self.silent))
        
        if self.mute_until is not None:
            b.write(Int(self.mute_until))
        
        if self.ios_sound is not None:
            b.write(self.ios_sound.write())
        
        if self.android_sound is not None:
            b.write(self.android_sound.write())
        
        if self.other_sound is not None:
            b.write(self.other_sound.write())
        
        return b.getvalue()
