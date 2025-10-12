from typing import Dict, List, Any


class Meta(Dict):
    """Дополнительные свойства к этапам, размерности не проверяются, глупость возможна"""
    def _to_list(self, ) -> List[Any]:
        """Вернет list из значений полей словаря, порядок важен"""
        return [value for value in self.values()]
