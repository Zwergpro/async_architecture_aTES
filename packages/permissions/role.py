import enum


class Role(enum.StrEnum):
    ADMIN = 'ADMIN'
    MANAGER = 'MANAGER'
    EMPLOYEE = 'EMPLOYEE'
    ACCOUNTANT = 'ACCOUNTANT'

    @classmethod
    def list(cls) -> list[str]:
        return list(map(lambda c: c.value, cls))
