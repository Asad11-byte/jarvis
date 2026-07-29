"""
Thin builders around googleapiclient.discovery.build so every
service module doesn't repeat this boilerplate.
"""
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials


def gmail_client(credentials: Credentials):
    return build("gmail", "v1", credentials=credentials, cache_discovery=False)


def calendar_client(credentials: Credentials):
    return build("calendar", "v3", credentials=credentials, cache_discovery=False)


def tasks_client(credentials: Credentials):
    return build("tasks", "v1", credentials=credentials, cache_discovery=False)