import json


class Status:


    def __init__(self, payload: str):
        if payload is None or payload.__contains__('</div>') or len(payload) == 0:
            self._type: str = 'error'
            self._message: str = 'Ocorreu um erro na requisição'
        else:
            dataset = json.loads(payload)
            if 'type' in dataset:
                self._type: str = dataset['type']
            if 'message' in dataset:
                self._message: str = dataset['message']


    def type(self) -> str:
        return self._type


    def message(self) -> str:
        return self._message


    def success(self) -> bool:
        return self._type == 'success'
