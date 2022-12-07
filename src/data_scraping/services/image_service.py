from functools import lru_cache


def lev_dist(a, b):
    @lru_cache(None)  # for memorization
    def min_dist(s1, s2):

        if s1 == len(a) or s2 == len(b):
            return len(a) - s1 + len(b) - s2

        # no change required
        if a[s1] == b[s2]:
            return min_dist(s1 + 1, s2 + 1)

        return 1 + min(
            min_dist(s1, s2 + 1),  # insert character
            min_dist(s1 + 1, s2),  # delete character
            min_dist(s1 + 1, s2 + 1),  # replace character
        )

    return min_dist(0, 0)


def get_most_close(word: str, list_words: list[str]) -> str | None:
    min_distance = float("inf")
    most_similar_word = None
    for guessed_word in list_words:
        curr_distance = lev_dist(word, guessed_word)
        if curr_distance < min_distance:
            most_similar_word = guessed_word
            min_distance = curr_distance
    return most_similar_word
