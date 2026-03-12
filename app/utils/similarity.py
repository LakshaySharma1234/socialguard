from collections import deque

recent_comments = deque(maxlen=50)

def is_repeated(comment):

    count = 0

    for prev in recent_comments:
        if prev == comment:
            count += 1

    recent_comments.append(comment)

    return count >= 2