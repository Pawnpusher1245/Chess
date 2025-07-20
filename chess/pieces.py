class Piece:
    def __init__(self, color, piece_type) -> None:
        self.color = color
        self.type = piece_type

    def __str__(self):
        return f"{self.color}{self.type}"