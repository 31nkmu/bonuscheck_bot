from applications.checks.mixins import CheckInterfaceMixin, ProductInterfaceMixin, CodeWordMixin
from applications.outputs.mixins import OutputInterfaceMixin, BalanceMixin
from applications.users.mixins import UserInterfaceMixin, CodeInterfaceMixin


class BackendInterface(UserInterfaceMixin, CodeInterfaceMixin, CheckInterfaceMixin, OutputInterfaceMixin,
                       CodeWordMixin, ProductInterfaceMixin, BalanceMixin):
    pass
