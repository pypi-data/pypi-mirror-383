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

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #

from typing import Union
from geezlibs import raw
from geezlibs.raw.core import TLObject

ChannelParticipantsFilter = Union[raw.types.ChannelParticipantsAdmins, raw.types.ChannelParticipantsBanned, raw.types.ChannelParticipantsBots, raw.types.ChannelParticipantsContacts, raw.types.ChannelParticipantsKicked, raw.types.ChannelParticipantsMentions, raw.types.ChannelParticipantsRecent, raw.types.ChannelParticipantsSearch]


# noinspection PyRedeclaration
class ChannelParticipantsFilter:  # type: ignore
    """Telegram API base type.

    Constructors:
        This base type has 8 constructors available.

        .. currentmodule:: geezlibs.raw.types

        .. autosummary::
            :nosignatures:

            ChannelParticipantsAdmins
            ChannelParticipantsBanned
            ChannelParticipantsBots
            ChannelParticipantsContacts
            ChannelParticipantsKicked
            ChannelParticipantsMentions
            ChannelParticipantsRecent
            ChannelParticipantsSearch
    """

    QUALNAME = "geezlibs.raw.base.ChannelParticipantsFilter"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. "
                        "More info: https://docs.pyrogram.org/telegram/base/channel-participants-filter")
