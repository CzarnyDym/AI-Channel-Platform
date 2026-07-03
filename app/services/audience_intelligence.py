TOPIC_DEFINITIONS = (
    {
        "id": "ai_quality",
        "category": "disliked",
        "topic": "AI quality criticism",
        "summary": "Viewers repeatedly mention AI quality concerns.",
        "keywords": ("ai", "slop", "temu", "hogwarts", "harry potter"),
    },
    {
        "id": "actor_praise",
        "category": "liked",
        "topic": "Actor / male lead praise",
        "summary": "Viewers praise the actor or male lead.",
        "keywords": (
            "love this male lead",
            "love this ml",
            "acting",
            "actor",
            "badass",
        ),
    },
    {
        "id": "story_criticism",
        "category": "disliked",
        "topic": "Story / plot criticism",
        "summary": "Viewers criticize the story, plot, or pacing.",
        "keywords": ("plot", "story", "far fetched", "boring", "secondary"),
    },
    {
        "id": "ending_criticism",
        "category": "disliked",
        "topic": "Ending / incomplete criticism",
        "summary": "Viewers say the ending feels rushed or incomplete.",
        "keywords": ("ending", "rushed", "not complete", "incomplete"),
    },
    {
        "id": "humor",
        "category": "liked",
        "topic": "Humor mentions",
        "summary": "Viewers react positively to funny or humorous moments.",
        "keywords": ("funny", "hilarious", "killed me", "\U0001f602", "\U0001f923"),
    },
)


def analyze_audience(
    comments,
    platform="youtube",
    max_evidence_per_insight=3,
    min_mentions=1,
):
    audience_analysis = {
        "platform": platform,
        "total_comments_analyzed": len(comments),
        "liked": [],
        "disliked": [],
        "recurring_topics": [],
    }

    for topic_definition in TOPIC_DEFINITIONS:
        matching_comments = _find_matching_comments(
            comments,
            topic_definition["keywords"],
        )

        if len(matching_comments) < min_mentions:
            continue

        insight = {
            "id": topic_definition["id"],
            "topic": topic_definition["topic"],
            "summary": topic_definition["summary"],
            "mentions": len(matching_comments),
            "evidence": matching_comments[:max_evidence_per_insight],
        }

        audience_analysis[topic_definition["category"]].append(insight)

    return audience_analysis


def _find_matching_comments(comments, keywords):
    matching_comments = []

    for comment in comments:
        text = comment.lower()

        if any(keyword in text for keyword in keywords):
            matching_comments.append(comment)

    return matching_comments
