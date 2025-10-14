import uuid
import typing

from .attachment import Attachment
if typing.TYPE_CHECKING:
    from .couchdb import CouchDB


class Document:
    data = {}

    def __init__(self, db: 'CouchDB', data: dict = None):
        if data is not None:
            self.data = data

        if '_id' not in data:
            self.data['_id'] = uuid.uuid4().hex

        self.db = db

    def update(self) -> list | dict:
        if '_rev' not in self.data:
            document = self.db.get_document(self.id)
            self.data['_rev'] = document['_rev']
        result = self.db.req_json(self.id, 'PUT', self.data)
        self.data['_rev'] = result['rev']
        return result

    def create(self) -> list | dict:
        result = self.db.req_json(self.id, 'PUT', self.data)
        self.data['_rev'] = result['rev']
        return result

    def delete(self) -> list | dict:
        return self.db.req_json(self.id, 'DELETE', query_params={
            'rev': self.data['_rev']
        })

    def add_attachment(self, name: str, content: bytes):
        self.db._req(f'{self.id}/{name}', 'PUT', content, {'rev': self.data['_rev']})

    @property
    def attachments(self):
        attachments = []
        if '_attachments' in self.data:
            for name in self.data['_attachments']:
                _attachment = self.data['_attachments'][name]
                attachments.append(Attachment(self, name, _attachment['content_type'], _attachment['length']))
        return attachments

    @property
    def id(self):
        return self.data['_id']

    def __contains__(self, item: str) -> bool:
        return item in self.data

    def __getitem__(self, key: str) -> any:
        return self.data[key]

    def __setitem__(self, key: str, value: any):
        self.data[key] = value

    def __repr__(self) -> str:
        return f'<{self.__class__.__name__} {self.data}>'

    def __eq__(self, other) -> bool:
        if not isinstance(other, Document):
            return NotImplemented

        return other.data == self.data
