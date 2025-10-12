import json
from typing import Union


class Response:

    def __init__(self, payload: str):

        self._total: int = 0
        self._records: list[dict[str, Union[str, int, bool]]] = []

        if payload is not None and not payload.__contains__('</div>') and len(payload) > 0:
            dataset = json.loads(payload)
            if 'total' in dataset and 'registros' in dataset:
                self._total = int(dataset['total'])
                self._records = dataset['registros']

    def total(self) -> int:
        return self._total

    def records(self) -> list[dict[str, Union[str, int, bool]]]:
        return self._records
