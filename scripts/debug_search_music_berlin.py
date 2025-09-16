"""
Debug script: Search for 'music' events in Berlin using the repository directly, to check if filters are working as expected.
"""
from befriends.catalog.repository import CatalogRepository
repo = CatalogRepository()
results = repo.search_text("music", filters={"city": "Berlin"})
for e in results:
    print(e)
