from datetime import datetime, timedelta, timezone

import pytest

from src.config import Config
from src.models import NewsItem
from src.scoring import NewsScorer

CONFIG_YAML = """
scoring:
  keywords_high_value:
    - "breakthrough"
  keywords_medium_value:
    - "update"
  weights:
    source_authority: 0.3
    recency: 0.2
    uniqueness: 0.3
    keyword_match: 0.2
selection:
  min_score: 40
"""


@pytest.fixture
def config(tmp_path):
    config_path = tmp_path / "config.yaml"
    config_path.write_text(CONFIG_YAML)
    return Config(str(config_path))


@pytest.fixture
def scorer(config):
    return NewsScorer(config)


def make_item(age_days: float, score: float = 0.0) -> NewsItem:
    discovered = datetime.now(timezone.utc) - timedelta(days=age_days)
    item = NewsItem(
        url=f"https://example.com/{age_days}-{score}",
        title="Title",
        source="Source",
        source_weight=1.0,
        discovered=discovered,
        week="2026-W01",
    )
    item.score = score
    return item


@pytest.mark.parametrize(
    "age_days,expected",
    [
        (0, 1.0),
        (5, 0.5),
        (20, 0.1),
    ],
)
def test_score_recency_buckets(scorer, age_days, expected):
    item = make_item(age_days)
    assert scorer._score_recency(item) == expected


def test_get_shortlist_respects_min_score_and_size(scorer):
    items = [make_item(0, score=s) for s in [10, 50, 90, 45, 39.9]]
    shortlist = scorer.get_shortlist(items, size=2)

    assert len(shortlist) == 2
    assert all(item.score >= 40 for item in shortlist)
