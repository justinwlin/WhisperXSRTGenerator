import srt

class SRTConverter:
    """
    A class to convert and manipulate segments from a WhisperX transcription into SRT (SubRip Text) format.

    Attributes:
        segments (list): A list of segment dictionaries.
        original_text (str, optional): The original text for comparison and correction.

    Methods:
        ... [existing methods] ...
    """

    def __init__(self, segments, original_text=None):
        """
        Initializes the SRTConverter with given segments and optional original text.
        Automatically corrects missing start or end times in segments.

        Ex. segments
        [
            {
                "start": 0.27,
                "end": 1.632,
                "text": " Hello world.",
                "words": [
                    {"word": "Hello", "start": 0.27, "end": 0.61, "score": 0.862},
                    {"word": "world.", "start": 0.69, "end": 1.091, "score": 0.779},
                ],
            },
            {
                "start": 1.632,
                "end": 3.055,
                "text": "Nice to meet you.",
                "words": [
                    {"word": "Nice", "start": 1.632, "end": 1.913, "score": 0.868},
                    {"word": "to", "start": 1.953, "end": 2.033, "score": 0.832},
                    {"word": "meet", "start": 2.093, "end": 2.274, "score": 0.788},
                    {"word": "you.", "start": 2.294, "end": 2.454, "score": 0.849},
                ],
            },...
        ]
        """

        self.segments = self.correct_missing_times(segments)
        
        if original_text is not None:
            self.original_text = original_text
        else:
            texts = []
            for segment in segments:
                if isinstance(segment, dict) and 'text' in segment:
                    texts.append(segment['text'])
            self.original_text = " ".join(texts)

    def correct_missing_times(self, segments):
        """
        Corrects missing start or end times in segments by using the times of adjacent words.
        """
        for segment in segments:
            words = segment.get('words', [])
            for i, word in enumerate(words):
                prev_word = words[i - 1] if i > 0 else None
                next_word = words[i + 1] if i < len(words) - 1 else None

                if 'start' not in word:
                    word['start'] = prev_word['end'] if prev_word and 'end' in prev_word else (next_word['start'] if next_word and 'start' in next_word else 0)

                if 'end' not in word:
                    word['end'] = next_word['start'] if next_word and 'start' in next_word else (prev_word['end'] if prev_word and 'end' in prev_word else word['start'])
        return segments
    
    def extract_word_segments(self, segments):
        """
        Extracts word segments from the given list of segments.

        Parameters:
            segments (list): A list of segment dictionaries.

        Returns:
            list: A list of word segment dictionaries.
        """
        word_segments = []
        for segment in segments:
            # Check if the segment is a dictionary and has the 'words' key
            if isinstance(segment, dict) and 'words' in segment:
                word_segments.extend(segment['words'])
        return word_segments


    def adjust_word_per_segment(self, words_per_segment=5):
        """
        Adjusts the number of words per segment in the word segments.

        This method reorganizes the word segments into new segments based on the specified number of words per segment.

        Parameters:
            words_per_segment (int): The number of words to include in each segment. Default is 5.

        Postcondition:
            The object's `segments` attribute is updated with the newly formed segments.
        """
        new_segments = []
        word_segments = self.extract_word_segments(self.segments)
        for i in range(0, len(word_segments), words_per_segment):
            chunk = word_segments[i: i + words_per_segment]

            # Construct the new segment
            start_time = chunk[0]["start"]  # Start time of the first word in the chunk
            end_time = chunk[-1]["end"]     # End time of the last word in the chunk
            segment_text = " ".join(word["word"] for word in chunk)

            segment = {
                "start": start_time,
                "end": end_time,
                "text": segment_text,
                "words": chunk,
            }
            new_segments.append(segment)

        self.segments = new_segments
        return new_segments
    
    def to_srt_highlight_word(self, color="red"):
        """
        Generates an SRT (SubRip Subtitle) formatted string with specific words highlighted.

        For each word in the segments, it creates an SRT entry where the word is highlighted in the specified color.

        Parameters:
            color (str): The color used for highlighting words. Default is "red".

        Returns:
            str: A string formatted in SRT format with highlighted words.
        """
        srt_data = []
        entry_index = 1
        for segment in self.segments:
            split_text = segment["text"].split()

            for idx, word_info in enumerate(segment["words"]):
                start_time = self.format_time(word_info["start"])
                end_time = self.format_time(word_info["end"]) if idx == len(segment["words"]) - 1 else self.format_time(segment["words"][idx + 1]["start"])

                # Highlight the word
                modified_text = split_text.copy()
                modified_text[idx] = f'<font color="{color}">{modified_text[idx]}</font>'
                highlighted_text = " ".join(modified_text)

                # Add entry to SRT data
                srt_data.append(f"{entry_index}\n{start_time} --> {end_time}\n{highlighted_text}\n")
                entry_index += 1

        return '\n'.join(srt_data)



    def to_srt_single_words(self):
        """
        Generates an SRT (SubRip Subtitle) formatted string with each word as a separate entry.

        For each word in the segments, it creates an SRT entry with the word's start and end times.

        Returns:
            str: A string formatted in SRT format with each word as a separate subtitle entry.
        """
        srt_entries = []
        entry_index = 1
        for segment in self.segments:
            for idx, word in enumerate(segment["words"]):
                start_time = self.format_time(word["start"])
                end_time = self.format_time(word["end"]) if idx == len(segment["words"]) - 1 else self.format_time(segment["words"][idx + 1]["start"])

                text = word["word"]
                srt_entries.append(f"{entry_index}\n{start_time} --> {end_time}\n{text}")
                entry_index += 1

        return '\n\n'.join(srt_entries)
    
    def to_srt_plain_text(self, words_per_segment=None):
        """
        Generates an SRT (SubRip Subtitle) formatted string with plain text segments.

        Each segment's text is presented as a subtitle entry, without highlighting any specific words.
        Optionally, segments can be divided based on the specified number of words per segment.

        Parameters:
            words_per_segment (int, optional): The number of words to include in each segment. If None, use existing segments.

        Returns:
            str: A string formatted in SRT format with plain text subtitles.
        """
        srt_entries = []
        entry_index = 1

        if words_per_segment is not None:
            # Adjust the word segments according to the specified words per segment
            adjusted_segments = self.adjust_word_per_segment(words_per_segment)
        else:
            # Use existing segments
            adjusted_segments = self.segments

        for segment in adjusted_segments:
            start_time = self.format_time(segment["start"])
            end_time = self.format_time(segment["end"])

            text = segment["text"]
            srt_entries.append(f"{entry_index}\n{start_time} --> {end_time}\n{text}")
            entry_index += 1

        return '\n\n'.join(srt_entries)

    @staticmethod
    def create_segments_from_words(word_segments, words_per_segment=5):
        """
        Creates new segments from a list of word dictionaries, with a specified number of words per segment.
        If a word lacks start or end times, it fills the gap using the nearest available times from adjacent words.

        Parameters:
            word_segments (list): A list of word dictionaries.
            words_per_segment (int): Number of words to include in each segment. Defaults to 5.

        Returns:
            list: A list of new segment dictionaries.
        """
        new_segments = []

        # Function to fill in missing start/end times
        def fill_missing_times(words):
            for i, word in enumerate(words):
                if 'start' not in word or 'end' not in word:
                    prev_word = words[i - 1] if i > 0 else None
                    next_word = words[i + 1] if i < len(words) - 1 else None

                    if 'start' not in word:
                        word['start'] = prev_word['end'] if prev_word and 'end' in prev_word else next_word['start'] if next_word and 'start' in next_word else 0

                    if 'end' not in word:
                        word['end'] = next_word['start'] if next_word and 'start' in next_word else prev_word['end'] if prev_word and 'end' in prev_word else word['start']

        for i in range(0, len(word_segments), words_per_segment):
            chunk = word_segments[i: i + words_per_segment]

            # Avoid creating a segment with no words
            if not chunk:
                break

            fill_missing_times(chunk)

            start_time = chunk[0]["start"]  # Start time of the first word in the chunk
            end_time = chunk[-1]["end"]     # End time of the last word in the chunk
            segment_text = " ".join(word["word"] for word in chunk)

            segment = {
                "start": start_time,
                "end": end_time,
                "text": segment_text,
                "words": chunk,
            }
            new_segments.append(segment)

        return new_segments

    
    @staticmethod
    def format_time(time_in_seconds):
        hours, remainder = divmod(time_in_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        milliseconds = (seconds - int(seconds)) * 1000
        return f"{int(hours):02d}:{int(minutes):02d}:{int(seconds):02d},{int(milliseconds):03d}"

    @staticmethod
    def write_to_file(filename, srt_string):
        isValid = SRTConverter.is_valid_srt_string(srt_string)
        if isValid:
            with open(filename, "w", encoding="utf-8") as file:
                file.write(srt_string)
        else:
            Exception("Invalid SRT string")

    @staticmethod
    def is_valid_srt_string(srt_string):
        try:
            list(srt.parse(srt_string))
            return True
        except:
            return False

    @staticmethod
    def is_valid_srt_file(file_path):
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                srt.parse(file.read())
            return True
        except:
            return False
        
    @staticmethod
    def initialize_with_normalized_timestamps(segment_arrays):
        """
        Initializes the SRTConverter with multiple arrays of segments, normalizing their timestamps. This is helpful
        if you had transcribed a long audio file in multiple parts, and want to combine the segments into one SRT file.

        Parameters:
            segment_arrays (list of lists): A list containing arrays of segment dictionaries.

        Returns:
            SRTConverter: An initialized SRTConverter object with normalized segments.
        """
        normalized_segments = []
        total_elapsed_time = 0.0

        for segments in segment_arrays:
            if not segments:
                continue

            # Calculate the time offset for the current array of segments
            first_segment_start = segments[0]["start"]
            time_offset = total_elapsed_time - first_segment_start

            for segment in segments:
                # Normalize start and end times
                segment["start"] += time_offset
                segment["end"] += time_offset

                for word in segment.get("words", []):
                    word["start"] += time_offset
                    word["end"] += time_offset

                normalized_segments.append(segment)

            # Update total elapsed time for the next iteration
            total_elapsed_time = normalized_segments[-1]["end"]

        # Create an SRTConverter instance with the normalized segments
        return SRTConverter(normalized_segments)