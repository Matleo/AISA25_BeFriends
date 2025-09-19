# Test Coverage Report

**Date:** 2025-09-19

## Summary
- **Total statements:** 1359
- **Missed statements:** 101
- **Coverage:** 93%

## Coverage by Module (Top Level)

| Module/File                                 | Statements | Missed | Coverage | Missing Lines                |
|---------------------------------------------|------------|--------|----------|------------------------------|
| befriends/app.py                            | 72         | 8      | 89%      | 108-113, 117-118, 134-136    |
| befriends/catalog/orm.py                    | 45         | 5      | 89%      | 64, 67-70                    |
| befriends/catalog/repository.py             | 94         | 1      | 99%      | 100                          |
| befriends/chatbot_client.py                 | 46         | 10     | 78%      | 21, 54-56, 67-73             |
| befriends/common/config.py                  | 32         | 4      | 88%      | 42-43, 48, 59                |
| befriends/common/telemetry.py               | 8          | 1      | 88%      | 19                           |
| befriends/domain/search_models.py           | 38         | 1      | 97%      | 30                           |
| befriends/ingestion/base.py                 | 9          | 2      | 78%      | 14, 19                       |
| befriends/ingestion/deduper.py              | 22         | 11     | 50%      | 17-21, 28-30, 34-39          |
| befriends/ingestion/normalizer.py           | 27         | 12     | 56%      | 20-23, 27, 40-45, 52-56      |
| befriends/response/formatter.py             | 81         | 6      | 93%      | 34, 75, 77, 79-81            |
| befriends/search/relevance.py               | 44         | 3      | 93%      | 44, 62, 64                   |
| befriends/search/service.py                 | 19         | 3      | 84%      | 27-29                        |
| befriends/web/admin_controller.py           | 13         | 1      | 92%      | 25                           |
| befriends/web/search_controller.py          | 24         | 3      | 88%      | 52-54                        |
| load_events_from_csv.py                     | 63         | 9      | 86%      | 17, 21-26, 45, 97            |
| tests/conftest.py                           | 49         | 6      | 88%      | 26, 64-65, 68, 71-72         |
| ... (all other test files)                  | 100%       |        |          |                              |

## Notes
- All test files except `conftest.py` have 100% coverage.
- Main coverage gaps are in ingestion, chatbot client, and some utility modules.
- All business logic, formatter, and controller code is well covered.

---

*Generated automatically by GitHub Copilot on 2025-09-19.*
