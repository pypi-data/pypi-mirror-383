import typing
if typing.TYPE_CHECKING:
    from .document import Document

class Attachment:
    document: 'Document'
    name: str
    content_type: str
    length: int
    _data: bytes

    def __init__(self, document: 'Document', name: str, content_type: str, length: int, data: bytes = None):
        self.document = document
        self.name = name
        self.content_type = content_type
        self.length = length
        self._data = data

    @property
    def data(self) -> bytes:
        if self._data is None:  # we don't have the data, fetch it from the db
            self._data = self.document.db._req(f'{self.document.id}/{self.name}').content
        return self._data
    @data.setter
    def data(self, value: bytes):
        self._data = value

    def __repr__(self):
        return f'<Attachment "{self.name}" {self.content_type}>'