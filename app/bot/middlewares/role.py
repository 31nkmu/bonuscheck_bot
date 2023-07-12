from aiogram.dispatcher.middlewares import LifetimeControllerMiddleware

from applications.users.models import UserRole
from interface.backend import BackendInterface


class RoleMiddleware(LifetimeControllerMiddleware, BackendInterface):
    skip_patterns = ["error", "update"]

    def __init__(self):
        super().__init__()

    async def pre_process(self, obj, data, *args):
        if not getattr(obj, "from_user", None):
            data["role"] = None
        else:
            id = obj.from_user.id
            user_obj = await self.get_user(id)
            if user_obj is False:
                data["role"] = UserRole.NOT_ACTIVE
                return
            if user_obj.is_banned is True:
                data["role"] = UserRole.BAN
            elif user_obj.is_admin is True:
                data["role"] = UserRole.ADMIN
            elif await self.check_code_user(user_obj) is False:
                data["role"] = UserRole.NOT_ACTIVE
            else:
                data["role"] = UserRole.USER

    async def post_process(self, obj, data, *args):
        del data["role"]
