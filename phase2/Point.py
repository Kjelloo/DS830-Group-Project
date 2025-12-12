from __future__ import annotations
from typing import Union
import math

Number = Union[int, float]

class Point:
    def __init__(self, x: Number, y: Number) -> None:
        if not isinstance(x, (int, float)):
            raise TypeError(f"x must be int or float, got {type(x).__name__}")
        if not isinstance(y, (int, float)):
            raise TypeError(f"y must be int or float, got {type(y).__name__}")

        self.x = float(x)
        self.y = float(y)

    def __str__(self):
        return f"Point(x={self.x}, y={self.y})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Point):
            return NotImplemented
        return self.x == other.x and self.y == other.y

    def __add__(self, other: Point) -> Point:
        if not isinstance(other, Point):
            return NotImplemented
        return Point(self.x + other.x, self.y + other.y)

    def __sub__(self, other: Point) -> Point:
        if not isinstance(other, Point):
            return NotImplemented
        return Point(self.x - other.x, self.y - other.y)

    def __mul__(self, scalar: Number) -> Point:
        if not isinstance(scalar, (int, float)):
            return NotImplemented
        return Point(self.x * scalar, self.y * scalar)

    def __rmul__(self, scalar: Number) -> Point:
        if not isinstance(scalar, (int, float)):
            return NotImplemented
        return Point(self.x * scalar, self.y * scalar)

    def __iadd__(self, other: Point) -> Point:
        if not isinstance(other, Point):
            return NotImplemented
        self.x += other.x
        self.y += other.y
        return self

    def __isub__(self, other: Point) -> Point:
        if not isinstance(other, Point):
            return NotImplemented
        self.x -= other.x
        self.y -= other.y
        return self

    def distance_to(self, other: Point) -> float:
        if not isinstance(other, Point):
            raise TypeError("distance_to() requires a Point")
        return math.sqrt((self.x - other.x) ** 2 + (self.y - other.y) ** 2)