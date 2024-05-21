import copy

class ITTTime:
    def __init__(self, time_in_seconds, frame_rate):
        self.frame_rate = frame_rate
        hours, remainder = divmod(time_in_seconds, 3600)
        minutes, full_seconds = divmod(remainder, 60)
        self.hours = int(hours)
        self.minutes = int(minutes)
        self.seconds = int(full_seconds)
        self.frames = int((time_in_seconds % 1) * frame_rate)

    def __str__(self):
        return f"{self.hours:02}:{self.minutes:02}:{self.seconds:02}:{self.frames:02}"

class Word:
    def __init__(self, word, frame_rate=None):
        self.start = word["start"]
        self.end = word["end"]
        self.text = word["word"]
        self.score = word.get("score", None)
        self.highlighted = word.get("highlighted", False)
        self.frame_rate = frame_rate
        self.itt_start = None
        self.itt_end = None

    def __repr__(self):
        return f"Word({self.start} -> {self.end}, {self.text}, highlighted={self.highlighted}, frame_rate={self.frame_rate})"

    def calculate_itt_time(self):
        if self.frame_rate:
            self.itt_start = ITTTime(self.start, self.frame_rate)
            self.itt_end = ITTTime(self.end, self.frame_rate)
    
    def convertToDictionary(self):
        return {
            "start": self.start,
            "end": self.end,
            "word": self.text,
            "score": self.score,
            "highlighted": self.highlighted
        }

class Segments:
    def __init__(self, segment, frame_rate=None):
        self.start = segment["start"]
        self.end = segment["end"]
        self.text = segment["text"]
        self.words = [Word(word, frame_rate) for word in segment["words"]]
        self.frame_rate = frame_rate
        self.itt_start = None
        self.itt_end = None

    def __repr__(self):
        return f"Segments({self.start}, {self.end}, {self.text}, frame_rate={self.frame_rate}, words={self.words})"
    
    def generate_subsegments(self):
        self.calculate_itt_times()  # Calculate iTT times for the entire segment first
        newSegments = []
        for idx, word in enumerate(self.words):
            newWords = copy.deepcopy(self.words)
            currentWord = newWords[idx]
            currentWord.highlighted = True
            newSegment = Segments({"start": word.start, "end": word.end, "text": self.text, "words": [w.convertToDictionary() for w in newWords]}, self.frame_rate)
            newSegment.calculate_itt_times()  # Update iTT times based on the new segment's timeframe
            newSegments.append(newSegment)
        return newSegments

    def calculate_itt_times(self):
        if self.frame_rate:
            self.itt_start = ITTTime(self.start, self.frame_rate)
            self.itt_end = ITTTime(self.end, self.frame_rate)
        for word in self.words:
            word.calculate_itt_time()

    def updateFrameRate(self, new_frame_rate):
        self.frame_rate = new_frame_rate
        for word in self.words:
            word.frame_rate = new_frame_rate
        self.calculate_itt_times()

    def to_itt_string(self, region="bottom", highlight_color="yellow"):
        if not self.itt_start or not self.itt_end:
            raise ValueError("ITT start or end times are not calculated.")

        # Begin the paragraph tag with the formatted iTT start and end times
        result = f'<p begin="{self.itt_start}" end="{self.itt_end}" region="{region}">\n'

        # Iterate through each word in the segment to format it appropriately
        for word in self.words:
            if word.highlighted:
                # Wrap highlighted words with a span tag and the specified color
                result += f'<span tts:color="{highlight_color}">{word.text}</span> '
            else:
                # Add non-highlighted words directly
                result += f'{word.text} '

        # Close the paragraph tag
        result += '</p>\n'

        return result

def closeGapBetweenListOfSegments(segments, gap):
    if(len(segments) <= 1):
        return segments
    newSegments = copy.deepcopy(segments)
    for idx in range(1, len(newSegments)):
        previousSegment = newSegments[idx - 1]
        currentSegment = newSegments[idx]
        if currentSegment.start - previousSegment.end < gap:
            # First see if the gap can be closed by just adjusting the frame rate ITT times
            # Check if they are the same time and the only difference is the frame
            sameTime = previousSegment.itt_end.seconds == currentSegment.itt_start.seconds and previousSegment.itt_end.minutes == currentSegment.itt_start.minutes and previousSegment.itt_end.hours == currentSegment.itt_start.hours

            if sameTime:
                # Close the gap by manually adjusting the frame of the iTT time
                # Previous segment adjustment
                previousSegment.itt_end.frames = currentSegment.itt_start.frames
                previousSegment.end = currentSegment.start

                # Current segment adjustment
                currentSegment.itt_start.frames = previousSegment.itt_end.frames
                currentSegment.start = previousSegment.end
            else:
                # If they are not the same time, we still know that the difference is less than the gap so we need to adjust by taking the avg of the two times, adjusting their time + frames
                # Calculate the average time between the two segments
                avgTime = (currentSegment.start + previousSegment.end) / 2
                avgITTTime = ITTTime(avgTime, currentSegment.frame_rate)
                # Previous segment
                previousSegment.itt_end = avgITTTime
                previousSegment.end = avgTime

                # Current segment
                currentSegment.itt_start = avgITTTime
                currentSegment.start = avgTime
    
    # Post-fix to adjust any segments that start and end on the same frame
    for idx in range(len(newSegments)):
        segment = newSegments[idx]
        # If the segment starts and ends on the same frame, adjust the start/end time to before and after
        # Check if a before exists
        if idx > 0:
            previousSegment = newSegments[idx - 1]
            if segment.start == segment.end:
                segment.start = previousSegment.end
                segment.itt_start = previousSegment.itt_end
        # Check if an after exists
        if idx < len(newSegments) - 1:
            nextSegment = newSegments[idx + 1]
            if segment.start == segment.end:
                segment.end = nextSegment.start
                segment.itt_end = nextSegment.itt_start

    return newSegments

def createSegmentsList(segments):
    return [Segments(segment) for segment in segments]

def generateFlattenedSegments(segments):
    flattenedSegments = []
    for segment in segments:
        flattenedSegments.extend(segment.generate_subsegments())
    return flattenedSegments

def updateFrameRateForSegments(segments, new_frame_rate):
    for segment in segments:
        segment.updateFrameRate(new_frame_rate)
    return segments