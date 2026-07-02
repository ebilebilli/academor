def calculate_level(score: int, total: int) -> str:
    if total <= 0:
        return 'N/A'
    percent = (score / total) * 100
    if percent < 20:
        return 'A1'
    if percent < 40:
        return 'A2'
    if percent < 60:
        return 'B1'
    if percent < 75:
        return 'B2'
    if percent < 90:
        return 'C1'
    return 'C2'

