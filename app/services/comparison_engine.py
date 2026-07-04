CATEGORIES = ("liked", "disliked", "recurring_topics")


def compare_audience_reports(latest_report, baseline_report):
    comparison_report = {}

    for category in CATEGORIES:
        comparison_report[category] = _compare_insight_category(
            latest_report.get(category, []),
            baseline_report.get(category, []),
        )

    return comparison_report


def _compare_insight_category(latest_insights, baseline_insights):
    latest_by_id = _index_insights_by_id(latest_insights)
    baseline_by_id = _index_insights_by_id(baseline_insights)
    insight_ids = sorted(set(latest_by_id) | set(baseline_by_id))

    return [
        _compare_insight(
            latest_by_id.get(insight_id),
            baseline_by_id.get(insight_id),
        )
        for insight_id in insight_ids
    ]


def _index_insights_by_id(insights):
    return {
        insight["id"]: insight
        for insight in insights
    }


def _compare_insight(latest_insight, baseline_insight):
    source_insight = latest_insight or baseline_insight
    latest_mentions = _get_mentions(latest_insight)
    baseline_mentions = _get_mentions(baseline_insight)
    difference = latest_mentions - baseline_mentions

    return {
        "id": source_insight["id"],
        "topic": source_insight["topic"],
        "summary": source_insight["summary"],
        "latest_mentions": latest_mentions,
        "baseline_mentions": baseline_mentions,
        "difference": difference,
        "percent_change": _calculate_percent_change(
            difference,
            baseline_mentions,
            latest_mentions,
        ),
        "latest_evidence": _get_evidence(latest_insight),
        "baseline_evidence": _get_evidence(baseline_insight),
    }


def _get_mentions(insight):
    if insight is None:
        return 0

    return insight.get("mentions", 0)


def _get_evidence(insight):
    if insight is None:
        return []

    return list(insight.get("evidence", []))


def _calculate_percent_change(difference, baseline_mentions, latest_mentions):
    if baseline_mentions == 0:
        if latest_mentions == 0:
            return 0.0

        return None

    return round((difference / baseline_mentions) * 100, 2)


__all__ = ["compare_audience_reports"]
