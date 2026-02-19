"""パズル状態の妥当性検証"""
from __future__ import annotations

from collections import Counter

from src.models import BOTTLE_CAPACITY, PuzzleState, ValidationResult


def is_solved(state: PuzzleState, bottle_capacity: int = BOTTLE_CAPACITY) -> bool:
    """全ボトルが満杯かつ単色、または空の場合 True を返す。"""
    for bottle in state:
        if len(bottle) == 0:
            continue
        # 満杯でない、または複数の異なる色がある場合は未解決
        if len(bottle) != bottle_capacity or len(set(bottle)) > 1:
            return False
    return True


def validate(
    state: PuzzleState,
    bottle_capacity: int = BOTTLE_CAPACITY,
) -> ValidationResult:
    """
    PuzzleState を検証して ValidationResult を返す。
    Postconditions: valid=True かつ already_solved=True の場合は解決済み通知
    Invariants: valid=False の場合 error_message は None でない
    """
    # ボトル数 0 チェック
    if len(state) == 0:
        return ValidationResult(
            valid=False,
            already_solved=False,
            error_message="ボトル数が 0 です。少なくとも 1 本以上のボトルが必要です。",
        )

    # 各色の合計セグメント数が bottle_capacity の倍数であるか検証
    counter: Counter[str] = Counter()
    for bottle in state:
        counter.update(bottle)

    invalid_colors = [
        f"{color}({count}セグメント)"
        for color, count in counter.items()
        if count % bottle_capacity != 0
    ]
    if invalid_colors:
        return ValidationResult(
            valid=False,
            already_solved=False,
            error_message=(
                f"色のセグメント数が不正です（容量 {bottle_capacity} の倍数でない色）: "
                f"{', '.join(invalid_colors)}"
            ),
        )

    already_solved = is_solved(state, bottle_capacity)
    return ValidationResult(
        valid=True,
        already_solved=already_solved,
        error_message=None,
    )
