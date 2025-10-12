import base64
import requests
import json
from typing import Union

from .environment import Environment
from .query import Query
from .response import Response


def _headers(request: str = '') -> dict[str, str]:
    token = _encoded_token()
    return {
        'ixcsoft': request,
        'Authorization': 'Basic {}'.format(base64.b64encode(token).decode('utf-8')),
        'Content-Type': 'application/json'
    }

def _encoded_token():
    env = Environment()
    token = env.token()
    return token if isinstance(token, bytes) else token.encode('utf-8')

def _uri(table: str) -> str:
    env = Environment()
    domain = env.domain()
    return 'https://{}/webservice/v1/{}'.format(domain, table)


class Connection:

    def __init__(self, table: str):
        self._table: str = table
        self._grid: list = []

    def where(self, args: str) -> None:
        query = Query(arg=args)
        args: dict = query.args()
        self._grid.append({
            'TB': '{}.{}'.format(self._table, args['column']),
            'OP': args['operator'],
            'P': args['value']
        })

    def many(self,
             page: int = 1,
             rows: int = 20,
             sort_name: str = 'id',
             sort_order: str = 'asc') -> Response:
        payload: object = {
            'qtype': self._table,
            'query': '',
            'oper': '',
            'page': page,
            'rp': rows,
            'sortname': '{}.{}'.format(self._table, sort_name),
            'sortorder': sort_order,
            'grid_param': json.dumps(self._grid)
        }

        response = requests.post(
            url=_uri(self._table),
            data=json.dumps(payload),
            headers=_headers(request='listar')
        )

        return Response(response.text)

    def one(self, record_id: int) -> dict[str, Union[str, int, bool]] | None:
        connection = Connection(table=self._table)
        connection.where(args=f'id = "{record_id}"')
        response = connection.many()

        if response.total() > 0:
            return response.records()[0]

        return None
