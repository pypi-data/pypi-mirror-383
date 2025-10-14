from importlib import resources
from typing import List


def load_oldict_words() -> List[str]:
    """
    패키지 내 datasets/oldict.txt를 읽어서 각 줄을 리스트로 반환
    """
    with resources.open_text("generalized_geography.datasets", "oldict.txt", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]
