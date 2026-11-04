import unittest
from datetime import date, timedelta
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

import bot


TODAY = date(2026, 11, 4)


class FixedDate(date):
    @classmethod
    def today(cls):
        return TODAY


class HabitDetailTests(unittest.IsolatedAsyncioTestCase):
    async def test_rate_counts_distinct_days_in_the_last_30_days(self):
        cases = [
            ("empty", [], 0),
            ("old only", [30, 45, 90], 0),
            ("window boundaries", [0, 29, 30], 7),
            ("future excluded", [-1, 0], 3),
            ("duplicate days", [0, 0, 29, 29], 7),
            ("long history", list(range(60)), 100),
        ]
        for name, offsets, expected_rate in cases:
            with self.subTest(name=name):
                completions = [(TODAY - timedelta(days=n)).isoformat() for n in offsets]
                data = {"123": {"habits": [{
                    "id": "synthetic-habit", "name": "Read", "completions": completions,
                }]}}
                query = SimpleNamespace(
                    data="habit_detail_synthetic-habit", from_user=SimpleNamespace(id=123),
                    answer=AsyncMock(), edit_message_text=AsyncMock(),
                )
                with patch.object(bot, "date", FixedDate), patch.object(bot, "load_data", return_value=data):
                    await bot.habit_detail(SimpleNamespace(callback_query=query), None)

                query.edit_message_text.assert_awaited_once()
                text = query.edit_message_text.await_args.args[0]
                self.assertIn(f"30-day rate: *{expected_rate}%*", text)
                self.assertIn(f"Total done: *{len(completions)} times*", text)
                self.assertIn("*Last 4 weeks*", text)
                self.assertEqual(data["123"]["habits"][0]["completions"], completions)


if __name__ == "__main__":
    unittest.main()
