class Word:
    def __init__(self, word):
        self.start = word["start"]
        self.end = word["end"]
        self.text = word["word"]
        self.score = word.get("score", None)

    def __repr__(self):
        return f"Word({self.start}, {self.end}, {self.text})"

class Segments:
    def __init__(self, segment):
        self.start = segment["start"]
        self.end = segment["end"]
        self.text = segment["text"]
        self.words = [Word(word) for word in segment["words"]]
    
    def __repr__(self):
        return f"Segments({self.start}, {self.end}, {self.text}, {self.words})"

def createSegmentsList(segments):
    return [Segments(segment) for segment in segments]