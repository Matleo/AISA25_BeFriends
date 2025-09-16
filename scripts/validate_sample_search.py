"""
Test script to validate search and response formatting with sample data in persistent storage.
"""
from befriends.catalog.repository import CatalogRepository
from befriends.search.service import SearchService
from befriends.search.relevance import RelevancePolicy
from befriends.response.formatter import ResponseFormatter
from befriends.web.search_controller import SearchController
from befriends.common.telemetry import Telemetry

# Compose dependencies
repo = CatalogRepository()
policy = RelevancePolicy()
service = SearchService(repo, policy)
formatter = ResponseFormatter()
telemetry = Telemetry()
controller = SearchController(service, formatter, telemetry)

# Perform a search for 'music' events in Berlin
response = controller.handle_search(query_text="music", city="Berlin")
print("Narrative:")
print(response["narrative"])
print("\nCards:")
for card in response["cards"]:
    print(card)
