from copy import deepcopy


class prototype:

    def clone(self):
        return deepcopy(self)

    def is_match(self, other) -> bool:
        """
        Сравнивает только непустые поля прототипа.
        Если поле None — не участвует в фильтрации.
        """
        for key, proto_value in self.__dict__.items():
            other_value = getattr(other, key, None)

            if proto_value in [None, "", 0]:
                continue

            if proto_value != other_value:
                return False

        return True
