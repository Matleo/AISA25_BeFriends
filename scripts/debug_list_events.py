"""
Debug script: List all events in the persistent catalog to verify data presence and inspect fields.
"""
from befriends.catalog.repository import CatalogRepository
repo = CatalogRepository()
events = repo.list_recent(20)
for e in events:
    print(e)
