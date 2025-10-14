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


class AuthorizationForm(TLObject):  # type: ignore
    """Telegram API type.

    Constructor of :obj:`~geezlibs.raw.base.account.AuthorizationForm`.

    Details:
        - Layer: ``148``
        - ID: ``AD2E1CD8``

    Parameters:
        required_types (List of :obj:`SecureRequiredType <geezlibs.raw.base.SecureRequiredType>`):
            N/A

        values (List of :obj:`SecureValue <geezlibs.raw.base.SecureValue>`):
            N/A

        errors (List of :obj:`SecureValueError <geezlibs.raw.base.SecureValueError>`):
            N/A

        users (List of :obj:`User <geezlibs.raw.base.User>`):
            N/A

        privacy_policy_url (``str``, *optional*):
            N/A

    Functions:
        This object can be returned by 1 function.

        .. currentmodule:: geezlibs.raw.functions

        .. autosummary::
            :nosignatures:

            account.GetAuthorizationForm
    """

    __slots__: List[str] = ["required_types", "values", "errors", "users", "privacy_policy_url"]

    ID = 0xad2e1cd8
    QUALNAME = "types.account.AuthorizationForm"

    def __init__(self, *, required_types: List["raw.base.SecureRequiredType"], values: List["raw.base.SecureValue"], errors: List["raw.base.SecureValueError"], users: List["raw.base.User"], privacy_policy_url: Optional[str] = None) -> None:
        self.required_types = required_types  # Vector<SecureRequiredType>
        self.values = values  # Vector<SecureValue>
        self.errors = errors  # Vector<SecureValueError>
        self.users = users  # Vector<User>
        self.privacy_policy_url = privacy_policy_url  # flags.0?string

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "AuthorizationForm":
        
        flags = Int.read(b)
        
        required_types = TLObject.read(b)
        
        values = TLObject.read(b)
        
        errors = TLObject.read(b)
        
        users = TLObject.read(b)
        
        privacy_policy_url = String.read(b) if flags & (1 << 0) else None
        return AuthorizationForm(required_types=required_types, values=values, errors=errors, users=users, privacy_policy_url=privacy_policy_url)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        flags = 0
        flags |= (1 << 0) if self.privacy_policy_url is not None else 0
        b.write(Int(flags))
        
        b.write(Vector(self.required_types))
        
        b.write(Vector(self.values))
        
        b.write(Vector(self.errors))
        
        b.write(Vector(self.users))
        
        if self.privacy_policy_url is not None:
            b.write(String(self.privacy_policy_url))
        
        return b.getvalue()
