import requests
import json
from typing import Literal
import urllib.parse

from .document import Document

class CouchDBException(Exception):
    """
    Class for any error returned by CouchDB
    """
    response: requests.Response

    def __init__(self, message):
        try:  # try to parse the error message
            error_data = json.loads(message)
            message = f'{error_data["error"]}: {error_data["reason"]}'
        except:
            message = f'CouchDB returned {message}'

        super().__init__(message)


class CouchDB:
    """
    Base class representing a CouchDB connection

    Attributes:
        username (str): Username of the CouchDB user used to access the database
        password (str): Password of the CouchDB user used to access the database
        db (str): CouchDB database name. Empty string to execute database-agnostic endpoints
        host (str): Hostname of the CouchDB server
        port (int): Port of the CouchDB server
        scheme (str): Scheme of the CouchDB server (http or https)
        base_path (str): URL path of the CouchDB server, with a trailing slash at the end
    """

    def __init__(self,
                 username: str,
                 password: str,
                 db: str = '',
                 host: str = 'localhost',
                 port: int = 5984,
                 scheme: Literal['http', 'https'] = 'http',
                 base_path: str = ''):
        self.base_url = f'{scheme}://{username}:{password}@{host}:{port}/{base_path}'  # build full url
        self.db_name = db

    def _req(self,
             endpoint: str,
             method: str = 'GET',
             data: bytes = None,
             query_params: dict = None) -> requests.Response:
        """
        Makes a request to the CouchDB API, with username, password, database & URL given in the constructor

        Args:
            endpoint (str): API endpoint, URL path
            method (str): HTTP method
            data (bytes): Request body
            query_params (dict): URL query parameters

        Returns:
            requests.Response: The requests's Response object
        """
        if query_params is not None:
            query_params = {k: v for k, v in query_params.items() if v}  # remove None values
            params = '?' + urllib.parse.urlencode(query_params)  # encode query parameters
        else:
            params = ''

        # make the request
        response = requests.request(
            method,
            self.base_url + self.db_name + '/' + endpoint + params,
            headers={
                'Content-Type': 'application/json'
            },
            data=data, verify=False)

        if not response.ok:  # raise exception if response status isn't 200~
            ex = CouchDBException(response.content)
            ex.response = response
            raise ex

        return response

    def req_json(self,
                 endpoint: str,
                 method: str = 'GET',
                 data: dict = None,
                 query_params: dict = None) -> dict | list:
        """
        Makes a request to the CouchDB API, with username, password, database & URL given in the constructor

        Args:
            endpoint (str): API endpoint, URL path
            method (str): HTTP method
            data (dict): Request body, to be serialized in json
            query_params (dict): URL query parameters

        Returns:
            dict | list: The received data
        """
        if data is not None:
            data = {k: v for k, v in data.items() if v}  # remove None values
        response = self._req(endpoint, method, json.dumps(data).encode(), query_params)
        return json.loads(response.text)

    def get_all_documents(self, skip: int = None, limit: int = None) -> list[Document]:
        """
        Return all the documents in the database

        Args:
            skip (int): Skip this number of records before starting to return the results
            limit (int): Limit the number of the returned design documents to the specified number

        Returns:
            list[Documents]: List of the documents matching the query
        """
        params = {
            'include_docs': True,
            'skip': skip,
            'limit': limit
        }

        result = []
        for doc in self.req_json('_all_docs', 'GET', query_params=params)['rows']:
            if not doc['id'].startswith('_design'):  # ignore design documents
                result.append(Document(self, doc['doc']))
        return result

    def get_document(self, document_id: str) -> Document | None:
        """
        Returns document by the specified document_id from the db

        Args:
            document_id (str): The ID of the document to return

        Returns:
            Document | None: The Document matching the query, or `None` of no document was found
        """
        try:
            return Document(self, self.req_json(document_id, 'GET'))
        except CouchDBException as e:
            if e.response.status_code == 404:
                return None
            else:
                raise e

    def find_documents(
        self,
        selector: dict,
        fields: list = None,
        sort: list = None,
        limit: int = None,
        skip: int = None
    ) -> list[Document]:
        """
        Returns documents matching the selector from the db

        Args:
            selector (dict): Object describing criteria used to select documents. More information provided in the section on `selector syntax <https://docs.couchdb.org/en/stable/api/database/find.html#find-selectors>`_
            fields (dict): Array specifying which fields of each object should be returned
            sort (list): Sort array following the `sort syntax <https://docs.couchdb.org/en/stable/api/database/find.html#find-sort>`_
            limit (int): Maximum number of results returned
            skip (int): Skip the first 'n' results, where 'n' is the value specified

        Returns:
            list[Document]: Array of documents matching the search. In each matching document, the fields specified in the fields argument are listed, along with their values.
        """
        data = {
            'selector': selector,
            'fields': fields,
            'sort': sort,
            'limit': limit,
            'skip': skip
        }

        result = []
        for doc in self.req_json('_find', 'POST', data)['docs']:
            result.append(Document(self, doc))
        return result

    def find_one_document(self, selector: dict, fields: dict = None, sort: list = None, skip: int = None) -> Document | None:
        """
        Returns a document matching the selector from the db

        Args:
            selector (dict): Object describing criteria used to select documents. More information provided in the section on `selector syntax <https://docs.couchdb.org/en/stable/api/database/find.html#find-selectors>`_
            fields (dict): Array specifying which fields of each object should be returned
            sort (list): Sort array following the `sort syntax <https://docs.couchdb.org/en/stable/api/database/find.html#find-sort>`_
            skip (int): Skip the first 'n' results, where 'n' is the value specified

        Returns:
            Document | None: The document matching the search, `None` if no documents matches. The field specified in the fields argument are listed, along with their values.
        """
        result = self.find_documents(selector, fields, sort, 1, skip)
        if not result:
            return None
        return result[0]

    def create_documents(self, documents: list[Document]):
        """
        Bulk inserts the specified documents into the database

        Args:
            documents (list[Document]): A list of document objects to be inserted
        """
        docs_data = list(map(lambda d: d.data, documents))
        result = self.req_json('_bulk_docs', 'POST', {'docs': docs_data})
        for doc in documents:
            inserted = [d for d in result if d['id'] == doc.id][0]  # retrieve the inserted object
            if inserted['ok']:
                doc['_rev'] = inserted['rev']  # update the revision id

    def get_bulk_documents(self, ids: list[any]) -> list[Document | CouchDBException]:
        """
        Get all the documents specified in the ids list from the database

        Args:
            ids (list[any]): List of the documents ids to get
        Returns:
            list[Document | CouchDBException]: List of either Documents of CouchDBException for when an error has occured when getting a document
        """
        ids = [{'id': id} for id in ids]
        results = self.req_json('_bulk_get', 'POST', {'docs': ids})['results']
        returns = []
        for result in results:
            if 'ok' in result['docs'][0]:
                returns.append(self.document(result['docs'][0]['ok']))
            else:
                exception = CouchDBException(result['docs'][0]['error']['error'])
                exception.id = result['id']
                returns.append(exception)
        return returns

    def get_view(self,
        design_doc: str,
        view: str,
        limit: int = None,
        skip: int = None,
        startkey: dict | list = None,
        endkey: dict | list = None,
        key: dict | list = None,
        keys: list = None,
        group: bool = None,
        group_level: int = None,
        reduce: bool = None,
        sorted: bool = None,
        descending: bool = None,
        include_docs: bool = False
    ) -> list[dict]:
        params = {
            'limit': limit,
            'skip': skip,
            'startkey': json.dumps(startkey) if startkey else None,
            'endkey': json.dumps(endkey) if endkey else None,
            'key': json.dumps(key) if key else None,
            'keys': json.dumps(keys) if keys else None,
            'group': group,
            'group_level': group_level,
            'reduce': reduce,
            'sorted': sorted,
            'descending': descending,
            'include_docs': include_docs
        }
        rows = self.req_json(f'_design/{design_doc}/_view/{view}', query_params=params)['rows']
        if include_docs:
            for i in range(len(rows)):
                rows[i]['doc'] = self.document(rows[i]['doc'])
        return rows

    def document(self, data: dict = None) -> Document:
        return Document(self, data)
