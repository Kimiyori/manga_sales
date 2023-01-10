from functools import lru_cache


def lev_dist(word1: str, word2: str) -> int:
    """Function to calculate the Levenshtein distance

    Args:
        word1 (str)
        word2 (str)

    Returns:
        int: distance between two words
    """

    @lru_cache(None)  # for memorization
    def min_dist(s1: int, s2: int) -> int:  # pylint: disable=invalid-name

        if s1 == len(word1) or s2 == len(word2):
            return len(word1) - s1 + len(word2) - s2

        # no change required
        if word1[s1] == word2[s2]:
            return min_dist(s1 + 1, s2 + 1)

        return 1 + min(
            min_dist(s1, s2 + 1),  # insert character
            min_dist(s1 + 1, s2),  # delete character
            min_dist(s1 + 1, s2 + 1),  # replace character
        )

    return min_dist(0, 0)


def get_most_close(
    word: str, list_words: list[tuple[int, str]]
) -> tuple[int, str] | None:
    """Finding most similar string from list of string

    Args:
        word (str): string that need to be matched
        list_words (list[str]): list of potential strings

    Returns:
        str | None: most similar strins from list or None if list is empty
    """
    min_distance = float("inf")
    most_similar_word = None
    for guessed_word in list_words:
        # we align the length of the guessed word with the length of the main word so that
        # they can be compared correctly, because if the guessed string is
        # longer than the main word, this can sometimes lead to the selection of the wrong line
        # also we make all compared string lowercase for corrent comparing
        curr_distance = lev_dist(word.lower(), guessed_word[1].lower()[: len(word)])
        if curr_distance < min_distance:
            most_similar_word = guessed_word
            min_distance = curr_distance
    return most_similar_word
