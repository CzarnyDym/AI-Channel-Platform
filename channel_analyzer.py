from app.services.youtube import get_comments, get_latest_videos


def is_metadata_comment(comment):
    text = comment.strip().lower()

    if text.startswith("ml:"):
        return True

    if text.startswith("fl:"):
        return True

    if "ml:" in text and "fl:" in text:
        return True

    if text in ["first", "first one here", "first comment"]:
        return True

    return False


def clean_comment_for_ai(comment):
    return comment.replace("\n", " ").strip()


def count_topic(comments, keywords):
    count = 0

    for comment in comments:
        text = comment.lower()
        if any(keyword in text for keyword in keywords):
            count += 1

    return count


videos = get_latest_videos(20)

print(f"Znaleziono {len(videos)} filmów")

for video in videos:
    print("\n==============================")
    print(video["title"])

    comments = get_comments(video["video_id"])

    print(f"Komentarzy: {len(comments)}")

    for comment in comments[:3]:
        print("-", comment[:120])

all_comments = []

for video in videos:
    comments = get_comments(video["video_id"])
    all_comments.extend(comments)

print()
print("Łącznie komentarzy:", len(all_comments))

filtered_comments = []

for comment in all_comments:
    cleaned = clean_comment_for_ai(comment)

    if is_metadata_comment(cleaned):
        continue

    if len(cleaned) < 8:
        continue

    filtered_comments.append(cleaned)

print("Po filtrze:", len(filtered_comments))

sample_comments = filtered_comments[:20]

sample = "\n".join(
    f"- {c}"
    for c in sample_comments
)

print("Komentarzy wysłanych do Qwena:", len(sample_comments))


ai_quality_count = count_topic(filtered_comments, [
    "ai", "slop", "temu", "hogwarts", "harry potter"
])

actor_praise_count = count_topic(filtered_comments, [
    "love this male lead",
    "love this ml",
    "acting",
    "actor",
    "badass"
])

story_criticism_count = count_topic(filtered_comments, [
    "plot",
    "story",
    "far fetched",
    "boring",
    "secondary"
])

ending_criticism_count = count_topic(filtered_comments, [
    "ending",
    "rushed",
    "not complete",
    "incomplete"
])

humor_count = count_topic(filtered_comments, [
    "funny",
    "hilarious",
    "killed me",
    "😂",
    "🤣"
])

print("AI quality:", ai_quality_count)
print("Actor praise:", actor_praise_count)
print("Story criticism:", story_criticism_count)
print("Ending criticism:", ending_criticism_count)
print("Humor:", humor_count)

import requests

prompt = f"""
You are a YouTube mini-drama channel analyst.

Use the topic counts as the main evidence.
Use the sample comments only as extra context.

Topic counts:
- AI quality criticism: {ai_quality_count}
- Actor / male lead praise: {actor_praise_count}
- Story / plot criticism: {story_criticism_count}
- Ending / incomplete criticism: {ending_criticism_count}
- Humor mentions: {humor_count}

Sample comments:
{sample}

Return ONLY this format:

Summary:
...

Strengths:
- ...
- ...

Weaknesses:
- ...
- ...

Recommendations:
- ...
- ...

Rules:
- Maximum 120 words.
- Do not quote comments.
- Do not repeat comments.
- Do not repeat sections.
"""
print("Wysyłam do Qwena...")

response = requests.post(
    "http://localhost:11434/api/generate",
    json={
        "model": "qwen2.5:3b",
        "prompt": prompt,
        "stream": False
    },
    timeout=120
)
print("Qwen odpowiedział")

print("\n===== CHANNEL REPORT =====\n")
print(response.json()["response"])

ai_keywords = [
    "ai",
    "hogwarts",
    "harry potter",
    "temu"
]

ai_mentions = 0

print("Filmów do analizy:", len(videos))

for comment in all_comments:
    text = comment.lower()

    if any(word in text for word in ai_keywords):
        ai_mentions += 1

print("AI mentions:", ai_mentions)

