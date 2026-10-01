def rank_candidates(results):
    return sorted(
        results,
        key=lambda x: x["score"],
        reverse=True
    )