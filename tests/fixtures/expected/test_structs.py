from typing import List, Optional

class Point:
    def __init__(self):
        self.x: int = 0
        self.y: int = 0

class Rectangle:
    def __init__(self):
        self.top_left: Point = Point()
        self.bottom_right: Point = Point()

class Array:
    def __init__(self):
        self.data: List[int] = [0] * 10
        self.name: str = ""

class Node:
    def __init__(self):
        self.value: int = 0
        self.next: Optional['Node'] = None 