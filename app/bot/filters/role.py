import typing

from aiogram.dispatcher.filters import BoundFilter
from aiogram.dispatcher.handler import ctx_data
from aiogram.types.base import TelegramObject

from applications.users.models import UserRole


class RoleFilter(BoundFilter):
    key = 'role'

    def __init__(self, role: typing.Union[None, UserRole, typing.Collection[UserRole]] = None):
        # тут присоединяется фильтр к каждому хэндлеру
        if role is None:
            self.roles = None
        elif isinstance(role, UserRole):
            self.roles = {role}
        else:
            self.roles = set(role)

    async def check(self, obj: TelegramObject):
        # тут проверка совпадает ли роль юзера с доступными ролями этого метода. у каждого метода есть роли с которыми он доступен
        if self.roles is None:
            return True
        # эта штука берет из хэндлера аргумент role
        data = ctx_data.get()

        # проверяет этот аргумент роли есть ли в ролях метода
        return data.get("role") in self.roles


#
class AdminFilter(BoundFilter):
    key = 'is_admin'

    def __init__(self, is_admin: typing.Optional[bool] = None):
        # тут присоединяется фильтр к каждому хэндлеру
        self.is_admin = is_admin

    async def check(self, obj: TelegramObject):
        if self.is_admin is None:
            return True
        # эта штука берет из хэндлера аргумент role
        data = ctx_data.get()
        # и проверяет если роль админа и она соответсвует is_admin метода - то мы идем в метод
        return (data.get("role") is UserRole.ADMIN) == self.is_admin
