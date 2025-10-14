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

InputMedia = Union[raw.types.InputMediaContact, raw.types.InputMediaDice, raw.types.InputMediaDocument, raw.types.InputMediaDocumentExternal, raw.types.InputMediaEmpty, raw.types.InputMediaGame, raw.types.InputMediaGeoLive, raw.types.InputMediaGeoPoint, raw.types.InputMediaInvoice, raw.types.InputMediaPhoto, raw.types.InputMediaPhotoExternal, raw.types.InputMediaPoll, raw.types.InputMediaUploadedDocument, raw.types.InputMediaUploadedPhoto, raw.types.InputMediaVenue]


# noinspection PyRedeclaration
class InputMedia:  # type: ignore
    """Telegram API base type.

    Constructors:
        This base type has 15 constructors available.

        .. currentmodule:: geezlibs.raw.types

        .. autosummary::
            :nosignatures:

            InputMediaContact
            InputMediaDice
            InputMediaDocument
            InputMediaDocumentExternal
            InputMediaEmpty
            InputMediaGame
            InputMediaGeoLive
            InputMediaGeoPoint
            InputMediaInvoice
            InputMediaPhoto
            InputMediaPhotoExternal
            InputMediaPoll
            InputMediaUploadedDocument
            InputMediaUploadedPhoto
            InputMediaVenue
    """

    QUALNAME = "geezlibs.raw.base.InputMedia"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. "
                        "More info: https://docs.pyrogram.org/telegram/base/input-media")
