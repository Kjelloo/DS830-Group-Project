from __future__ import annotations
import math


class Point:
    def __init__(self, x: float, y: float) -> None:
        self.x = x
        self.y = y

    def __str__(self):
        return f"Point(x={self.x}, y={self.y})"

    def distance_to(self, other: 'Point') -> float:
        return math.sqrt((self.x - other.x) ** 2 + (self.y - other.y) ** 2)

    def __add__(self, other: 'Point') -> 'Point':
        return Point(self.x + other.x, self.y + other.y)

    def __sub__(self, other: 'Point') -> 'Point':
        return Point(self.x - other.x, self.y - other.y)

    def __mul__(self, scalar: float | int) -> 'Point':
        return Point(self.x * scalar, self.y * scalar)

    def __iadd__(self, other: 'Point') -> None:
        self.x += other.x
        self.y += other.y

    def __isub__(self, other: 'Point') -> None:
        self.x -= other.x
        self.y -= other.y

    def __rmul__(self, scalar: float | int) -> 'Point':
        return Point(self.x * scalar, self.y * scalar)
