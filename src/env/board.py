import numpy as np
from typing import List, Tuple, Optional
import config


class Board:
    def __init__(self, size: int = config.BOARD_SIZE):
        self.size = size
        self.grid = np.zeros((size, size), dtype=int)
        self._setup_initial_position()
        self.current_player = config.ATTACKER  # Ходят атакующие

    def _setup_initial_position(self) -> None:
        """Расставляет фигуры по стартовой позиции (упрощённый вариант 7x7)."""
        # Король в центре
        center = self.size // 2
        self.grid[center, center] = config.KING
        self.grid[center, center] = config.KING

        # Защитники вокруг короля
        defenders = [
            (center - 1, center), (center + 1, center),
            (center, center - 1), (center, center + 1)
        ]
        for r, c in defenders:
            self.grid[r, c] = config.DEFENDER

        # Атакующие по периметру
        attackers_pos = [
            (0, 2), (0, 3), (0, 4),
            (6, 2), (6, 3), (6, 4),
            (2, 0), (3, 0), (4, 0),
            (2, 6), (3, 6), (4, 6),
            (1, 3), (5, 3), (3, 1), (3, 5)
        ]
        for r, c in attackers_pos:
            self.grid[r, c] = config.ATTACKER

    def is_valid_pos(self, r: int, c: int) -> bool:
        return 0 <= r < self.size and 0 <= c < self.size

    def get_valid_moves(self, r: int, c: int) -> List[Tuple[int, int]]:
        """Возвращает список допустимых клеток для хода с позиции (r, c)."""
        if not self.is_valid_pos(r, c) or self.grid[r, c] == config.EMPTY:
            return []

        moves = []
        piece = self.grid[r, c]

        for dr, dc in config.DIRECTIONS:
            nr, nc = r + dr, c + dc
            while self.is_valid_pos(nr, nc):
                target = self.grid[nr, nc]
                if target != config.EMPTY:
                    break  # Блок фигурой
                # Король может встать на трон, другие нет (упрощение)
                if (nr, nc) == (self.size // 2, self.size // 2) and piece != config.KING:
                    break
                moves.append((nr, nc))
                nr += dr
                nc += dc
        return moves

    def make_move(self, from_pos: Tuple[int, int], to_pos: Tuple[int, int]) -> bool:
        """Выполняет ход. Возвращает True, если ход валиден и выполнен."""
        fr, fc = from_pos
        tr, tc = to_pos

        if not self.is_valid_pos(fr, fc) or not self.is_valid_pos(tr, tc):
            return False
        if self.grid[fr, fc] == config.EMPTY:
            return False
        if self.grid[tr, tc] != config.EMPTY:
            return False
        if to_pos not in self.get_valid_moves(fr, fc):
            return False

        # Перемещаем фигуру
        self.grid[tr, tc] = self.grid[fr, fc]
        self.grid[fr, fc] = config.EMPTY

        # Проверяем захваты и победу
        self._capture_pieces(tr, tc)
        return True

    def _capture_pieces(self, r: int, c: int) -> None:
        """Упрощённая логика захвата: фигура удаляется, если зажата с двух противоположных сторон."""
        for dr, dc in config.DIRECTIONS:
            opp_r, opp_c = r + dr, c + dc
            back_r, back_c = r - dr, c - dc

            if not (self.is_valid_pos(opp_r, opp_c) and self.is_valid_pos(back_r, back_c)):
                continue

            opp_piece = self.grid[opp_r, opp_c]
            back_piece = self.grid[back_r, back_c]

            # Захват возможен только между вражескими фигурами
            if self.grid[r, c] == config.ATTACKER:
                enemy = config.DEFENDER
            else:
                enemy = config.ATTACKER

            if opp_piece == enemy and back_piece == enemy:
                self.grid[r, c] = config.EMPTY
                return

    def check_winner(self) -> Optional[str]:
        """Возвращает 'defenders', 'attackers' или None."""
        center = self.size // 2
        if self.grid[center, center] == config.EMPTY:
            # Король захвачен или сдвинут. Проверяем, не на краю ли он.
            pass

        # Проверка победы защитников: король на любой границе
        for r in range(self.size):
            for c in range(self.size):
                if self.grid[r, c] == config.KING:
                    if r in (0, self.size - 1) or c in (0, self.size - 1):
                        return 'defenders'
        return None

    def render(self) -> str:
        symbols = {0: '.', 1: 'A', 2: 'D', 3: 'K', 4: 'T'}
        lines = []
        lines.append("  " + " ".join(str(i) for i in range(self.size)))
        for r, row in enumerate(self.grid):
            line = f"{r} " + " ".join(symbols[val] for val in row)
            lines.append(line)
        return "\n".join(lines)

    def copy(self) -> 'Board':
        new_board = Board(self.size)
        new_board.grid = self.grid.copy()
        new_board.current_player = self.current_player
        return new_board