import requests

def analyze_comment(comment):
    prompt = f"""
You are a sentiment analyzer for mini-drama comments.

Rules:
- Wanting part 2 is positive.
- Story is more important than ending.
- Too short + wants sequel = positive.
- Ignore ML/FL ratings.
- If the comment is about YouTube ads, subscriptions, or technical issues, answer neutral.

Comment:
{comment}

Answer only:
positive
negative
neutral
"""

    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "qwen2.5:3b",
            "prompt": prompt,
            "stream": False
        }
    )

    return response.json()["response"].strip().lower()


while True:
    comment = input("Komentarz: ")

    if comment.lower() in ["exit", "quit", "koniec"]:
        break

    result = analyze_comment(comment)
    print("AI:", result)