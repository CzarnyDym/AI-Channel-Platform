import requests

comments = [
    "Amazing drama",
    "Need part 2",
    "Worth watching",
    "Great chemistry",
    "Ending was rushed",
    "Story was boring"
]

all_comments = "\n".join(
    f"- {comment}"
    for comment in comments
)

prompt = f"""

Important interpretation rules:

- "Need part 2", "Want season 2", "Need sequel",
  "I want more", "Too short" are POSITIVE comments.

- If viewers want more episodes, this means they enjoyed the drama.

- Never classify wanting a sequel as negative.

- Story quality is more important than ending quality.

If any comment says the story is boring, weak, bad or confusing, mention story quality as a weakness.

You are analyzing audience comments.

Use ONLY information explicitly present in the comments.

Do NOT invent strengths or weaknesses.

If there is not enough evidence, write:
- None

Comments:
{all_comments}

Return exactly:

Audience Summary:
...

Strengths:
- ...
- ...

Weaknesses:
- ...
- ...

Rating:
X/10
"""

response = requests.post(
    "http://localhost:11434/api/generate",
    json={
        "model": "qwen2.5:3b",
        "prompt": prompt,
        "stream": False
    }
)
print(all_comments)
print(response.json()["response"])