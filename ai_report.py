import requests
print("URUCHAMIAM AI_REPORT")

score = 8

positive = 18
negative = 4
neutral = 8

top_positive = [
    "Need part 2",
    "Amazing drama",
    "Worth watching"
]

top_negative = [
    "Story was boring",
    "Ending was rushed"
]

prompt = f"""
You are a YouTube audience analyst.

Data:

Overall score: {score}/10

Positive comments: {positive}
Negative comments: {negative}
Neutral comments: {neutral}

Most common positive feedback:
{chr(10).join('- ' + x for x in top_positive)}

Most common negative feedback:
{chr(10).join('- ' + x for x in top_negative)}

Write a report with this format:

Audience Summary:
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
"""

response = requests.post(
    "http://localhost:11434/api/generate",
    json={
        "model": "qwen2.5:3b",
        "prompt": prompt,
        "stream": False
    }
)

print(response.json()["response"])