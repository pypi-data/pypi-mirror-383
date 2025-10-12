

class Query:


    def __init__(self, arg: str):
        self._arg = arg


    def operator(self) -> str:
        if self._arg.__contains__('>'):
            return '>=' if self._arg.__contains__('=') else '>'
        if self._arg.__contains__('<'):
            return '<=' if self._arg.__contains__('=') else '<'
        if self._arg.__contains__('!='):
            return '!='
        if self._arg.__contains__('?') or self._arg.__contains__('%'):
            return 'L'
        return '='
    

    def column(self) -> str:
        params: list[str] = self._arg.split(self.operator())
        if len(params) == 2:
            return params[0]
        return 'id'
    

    def value(self) -> str:
        params: list[str] = self._arg.split(self.operator())
        if len(params) == 2:
            return params[1]
        return '0'
    

    def args(self) -> dict[str, str]:
        return {
            'column': self.column(),
            'operator': self.operator(),
            'value': self.value().replace('"', '')
        }
