from requests import Response, get, post, patch, put, delete
from cocobase_client.config import BASEURL
from cocobase_client.exceptions import CocobaseError
from cocobase_client.query import QueryBuilder
from cocobase_client.record import Collection, Record
from cocobase_client.types import HttpMethod


class CocoBaseClient:
    """
    A client for interacting with the CocoBase API.
    Provides methods for collection, document, and user authentication management.
    """

    api_key = None
    app_client_token = None

    def __init__(self, api_key: str, token: str | None = None):
        """
        Initialize the CocoBaseClient with an API key and optional token.
        """
        self.api_key = api_key
        self.app_client_token = token

    def __request__(
        self,
        url,
        method: HttpMethod = HttpMethod.get,
        data: dict | None = None,
        custom_headers: dict | None = None,
        files=None,
    ) -> Response:
        """
        Internal method to send HTTP requests to the CocoBase API.
        Handles GET and POST methods, and allows custom headers.
        """
        headers = {"x-api-key": self.api_key}
        if not url.startswith("/"):
            url = "/" + url
        if custom_headers is not None:
            headers.update(custom_headers)
        if method not in (
            HttpMethod.get,
            HttpMethod.post,
            HttpMethod.delete,
            HttpMethod.patch,
        ):
            raise ValueError(
                "Invalid HTTP method. Use HttpMethod.get, HttpMethod.post, HttpMethod.delete, or HttpMethod.patch."
            )
        url = BASEURL + url
        if method == HttpMethod.get:
            return get(url, headers=headers, files=files)
        elif method == HttpMethod.delete:
            return delete(
                url, headers=headers, json=data, files=files
            )  # Simulate delete if needed
        elif method == HttpMethod.patch:
            return patch(
                url, headers=headers, json=data, files=files
            )  # Simulate patch if needed
        else:
            return post(url, headers=headers, json=data, files=files)

    # ------------------- COLLECTION METHODS -------------------
    def create_collection(
        self, collection_name, webhookurl: str | None = None
    ) -> Collection | None:
        """
        Create a new collection with an optional webhook URL.
        """
        data = {"name": collection_name}
        if webhookurl is not None:
            data["webhook_url"] = webhookurl
        req = self.__request__("/collections/", method=HttpMethod.post, data=data)
        if req.status_code == 400:
            raise CocobaseError("Invalid Request: " + req.text)
        elif req.status_code == 422:
            raise CocobaseError("A field is missing: " + req.text)
        elif req.status_code == 500:
            raise CocobaseError("Internal Server Error")
        elif req.status_code == 201:
            return Collection(req.json())

    def update_collection(
        self,
        collection_id,
        collection_name: str | None = None,
        webhookurl: str | None = None,
    ):
        """
        Update an existing collection's name and/or webhook URL.
        """
        data = dict()
        if collection_id is None:
            raise CocobaseError("Collection ID must be provided.")
        if webhookurl is None and collection_name is None:
            raise CocobaseError(
                "At least one of webhook_url or collection_name must be provided."
            )
        if webhookurl is not None:
            data["webhook_url"] = webhookurl
        if collection_name is not None:
            data["name"] = collection_name
        req = self.__request__(
            f"/collections/{collection_id}", method=HttpMethod.post, data=data
        )
        if req.status_code == 400:
            raise CocobaseError("Invalid Request: " + req.text)
        elif req.status_code == 422:
            raise CocobaseError("A field is missing: " + req.text)
        elif req.status_code == 500:
            raise CocobaseError("Internal Server Error")
        elif req.status_code == 200:
            return req.json()

    def delete_collection(self, collection_id):
        """
        Delete a collection by its ID.
        """
        if collection_id is None:
            raise CocobaseError("Collection ID must be provided.")
        req = self.__request__(
            f"/collections/{collection_id}", method=HttpMethod.delete
        )
        if req.status_code == 400:
            raise CocobaseError("Invalid Request: " + req.text)
        elif req.status_code == 422:
            raise CocobaseError("A field is missing: " + req.text)
        elif req.status_code == 500:
            raise CocobaseError("Internal Server Error")
        elif req.status_code == 204:
            return True
        else:
            print("Unexpected status code:", req.status_code)
            print("Response text:", req.text)

    # ------------------- DOCUMENT METHODS -------------------
    def create_document(self, collection_id, data: dict) -> Record | None:
        """
        Create a new document in a collection.
        """
        if collection_id is None:
            raise CocobaseError("Collection ID must be provided.")
        if not isinstance(data, dict):
            raise CocobaseError("Data must be a dictionary.")
        req = self.__request__(
            f"/collections/documents?collection=" + collection_id,
            method=HttpMethod.post,
            data={"data": data},
        )
        if req.status_code == 400:
            raise CocobaseError("Invalid Request: " + req.text)
        elif req.status_code == 422:
            raise CocobaseError("A field is missing: " + req.text)
        elif req.status_code == 500:
            raise CocobaseError("Internal Server Error")
        elif req.status_code == 201:
            return Record(req.json())

    def list_documents(
        self, collection_id, query: QueryBuilder | None = None
    ) -> list[Record] | None:
        """
        List all documents in a collection, optionally filtered by a query.
        """
        if collection_id is None:
            raise CocobaseError("Collection ID must be provided.")
        if query is not None and not isinstance(query, QueryBuilder):
            raise CocobaseError("Query must be an instance of QueryBuilder.")
        url = (
            f"/collections/{collection_id}/documents?{query.build()}"
            if query is not None
            else f"/collections/{collection_id}/documents"
        )
        req = self.__request__(url)
        if req.status_code == 400:
            raise CocobaseError("Invalid Request: " + req.text)
        elif req.status_code == 422:
            raise CocobaseError("A field is missing: " + req.text)
        elif req.status_code == 500:
            raise CocobaseError("Internal Server Error")
        elif req.status_code == 200:
            return [Record(doc) for doc in req.json()]

    def get_document(self, collection_id, document_id) -> Record | None:
        """
        Retrieve a single document by its ID from a collection.
        """
        if collection_id is None:
            raise CocobaseError("Collection ID must be provided.")
        if document_id is None:
            raise CocobaseError("Document ID must be provided.")
        req = self.__request__(f"/collections/{collection_id}/documents/{document_id}")
        if req.status_code == 400:
            raise CocobaseError("Invalid Request: " + req.text)
        elif req.status_code == 422:
            raise CocobaseError("A field is missing: " + req.text)
        elif req.status_code == 500:
            raise CocobaseError("Internal Server Error")
        elif req.status_code == 200:
            return Record(req.json())

    def delete_document(self, collection_id, document_id) -> bool:
        """
        Delete a document from a collection by its ID.
        """
        if collection_id is None:
            raise CocobaseError("Collection ID must be provided.")
        if document_id is None:
            raise CocobaseError("Document ID must be provided.")
        req = self.__request__(
            f"/collections/{collection_id}/documents/{document_id}",
            method=HttpMethod.delete,
        )
        if req.status_code == 400:
            raise CocobaseError("Invalid Request: " + req.text)
        elif req.status_code == 422:
            raise CocobaseError("A field is missing: " + req.text)
        elif req.status_code == 500:
            raise CocobaseError("Internal Server Error")
        elif req.status_code == 200 or req.status_code == 204:
            return True
        return False

    def update_document(self, collection_id, document_id, data: dict) -> Record | None:
        """
        Update a document in a collection by its ID.
        """
        if collection_id is None:
            raise CocobaseError("Collection ID must be provided.")
        if document_id is None:
            raise CocobaseError("Document ID must be provided.")
        if not isinstance(data, dict):
            raise CocobaseError("Data must be a dictionary.")
        req = self.__request__(
            f"/collections/{collection_id}/documents/{document_id}",
            method=HttpMethod.patch,
            data={"data": data},
        )
        if req.status_code == 400:
            raise CocobaseError("Invalid Request: " + req.text)
        elif req.status_code == 422:
            raise CocobaseError("A field is missing: " + req.text)
        elif req.status_code == 500:
            raise CocobaseError("Internal Server Error")
        elif req.status_code == 200:
            return Record(req.json())

    # ------------------- AUTHENTICATION METHODS -------------------
    def set_app_client_token(self, app_client_token: str):
        """
        Set the app client token for the client.
        """
        self.app_client_token = app_client_token

    def is_authenticated(self) -> bool:
        """
        Check if the client is authenticated.
        """
        return self.app_client_token is not None

    def register(self, email: str, password: str, data: dict | None = None) -> bool:
        """
        Register a new user with email, password, and optional extra data.
        """
        post_data = {
            "email": email,
            "password": password,
        }
        if data is not None and isinstance(data, dict):
            post_data["data"] = data  # type: ignore
        req = self.__request__(
            "/auth-collections/signup",
            method=HttpMethod.post,
            data=post_data,
        )
        if req.status_code == 200:
            self.set_app_client_token(req.json().get("access_token"))
            return req.json().get("access_token") is not None
        else:
            raise CocobaseError("Registration failed: " + req.text)

    def login(self, email: str, password: str) -> bool:
        """
        Log in a user with email and password.
        """
        req = self.__request__(
            "/auth-collections/login",
            method=HttpMethod.post,
            data={"email": email, "password": password},
        )
        if req.status_code == 200:
            self.set_app_client_token(req.json().get("access_token"))
            return req.json().get("access_token") is not None
        else:
            raise CocobaseError("Login failed: " + req.text)

    def logout(self):
        """
        Log out the current user by clearing the app client token.
        """
        self.app_client_token = None

    def get_user_info(self) -> dict | None:
        """
        Get the current user's information. Requires authentication.
        """
        if not self.is_authenticated():
            raise CocobaseError("Client is not authenticated.")
        req = self.__request__(
            "/auth-collections/user",
            method=HttpMethod.get,
            custom_headers={"Authorization": f"Bearer {self.app_client_token}"},
        )
        if req.status_code == 200:
            return req.json()
        else:
            raise CocobaseError("Failed to get user info: " + req.text)

    def update_user_info(self, email, password, data: dict) -> dict | None:
        """
        Update the current user's information. Requires authentication.
        """
        form_data = dict()
        if email is not None:
            form_data["email"] = email
        if password is not None:
            form_data["password"] = password
        if data is not None and isinstance(data, dict):
            form_data["data"] = data
        if not self.is_authenticated():
            raise CocobaseError("Client is not authenticated.")
        if not isinstance(data, dict):
            raise CocobaseError("Data must be a dictionary.")
        req = self.__request__(
            "/auth-collections/user",
            method=HttpMethod.patch,
            data=form_data,
            custom_headers={"Authorization": f"Bearer {self.app_client_token}"},
        )
        if req.status_code == 200:
            return req.json()
        else:
            raise CocobaseError("Failed to update user info: " + req.text)
