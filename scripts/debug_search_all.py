"""
Debug script: Search for all events with no filters to check if search_text returns anything.
"""
from befriends.catalog.repository import CatalogRepository
repo = CatalogRepository()
results = repo.search_text("")
for e in results:
    print(e)
