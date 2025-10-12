import json
from io import BytesIO

import PIL
import pytest
from django.core.files.uploadedfile import InMemoryUploadedFile
from graphene_django.settings import graphene_settings

pytest_plugins = ("celery.contrib.pytest",)


def graphql_query(
    query,
    operation_name=None,
    input_data=None,
    variables=None,
    headers=None,
    client=None,
):
    """Do a GraphQL query for testing."""
    graphql_url = graphene_settings.TESTING_ENDPOINT
    body = {"query": query}
    if operation_name:
        body["operationName"] = operation_name
    if variables:
        body["variables"] = variables
    if input_data:
        if "variables" in body:
            body["variables"]["input"] = input_data
        else:
            body["variables"] = {"input": input_data}
    if headers:
        header_params = {"headers": headers}
        resp = client.post(
            graphql_url,
            json.dumps(body),
            content_type="application/json",
            **header_params,
        )
    else:
        resp = client.post(
            graphql_url, json.dumps(body), content_type="application/json"
        )
    content = json.loads(resp.content)
    return resp, content


def graphql_query_multipart(
    query,
    operation_name=None,
    input_data=None,
    variables=None,
    headers=None,
    files=None,
    client=None,
):
    """Do a GraphQL query for testing."""
    graphql_url = graphene_settings.TESTING_ENDPOINT
    operations = {"query": query}
    if operation_name:
        operations["operationName"] = operation_name
    if variables:
        operations["variables"] = variables
    if input_data:
        if "variables" in operations:
            operations["variables"]["input"] = input_data
        else:
            operations["variables"] = {"input": input_data}
    body = {
        "operations": json.dumps(operations),
    }
    map = {}
    if files:
        for idx, (key, value) in enumerate(files.items()):
            file_key = f"file_{idx}"
            body[file_key] = value
            map[file_key] = [key]
    body["map"] = json.dumps(map)
    if headers:
        header_params = {"headers": headers}
        resp = client.post(
            graphql_url,
            data = body,
            **header_params,
        )
    else:
        resp = client.post(
            graphql_url, data=body
        )
    content = json.loads(resp.content)
    return resp, content


@pytest.fixture
def logged_in_client(client, django_user_model):
    """Provide a logged-in client for testing."""
    from aleksis.core.models import Person
    username = "foo"
    password = "bar"

    user = django_user_model.objects.create_user(username=username, password=password)
    Person.objects.create(user=user, first_name="John", last_name="Doe")

    client.login(username=username, password=password)

    return client


@pytest.fixture
def client_query(logged_in_client):
    """Do a GraphQL query with a logged-in client."""
    def func(*args, **kwargs):
        return graphql_query_multipart(*args, **kwargs, client=logged_in_client)

    return func

@pytest.fixture
def picture():
    buf = BytesIO()
    im = PIL.Image.new(mode="RGB", size=(200, 200))
    im.save(buf, format="JPEG")
    return buf

@pytest.fixture
def uploaded_picture(picture):
    return InMemoryUploadedFile(picture, None, 'test.jpg', 'image/jpeg', None, None)
