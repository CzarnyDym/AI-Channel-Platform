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


def should_keep_comment(comment):
    if is_metadata_comment(comment):
        return False

    if len(comment) < 8:
        return False

    return True


def filter_comments(comments):
    filtered_comments = []

    for comment in comments:
        cleaned = clean_comment_for_ai(comment)

        if not should_keep_comment(cleaned):
            continue

        filtered_comments.append(cleaned)

    return filtered_comments
