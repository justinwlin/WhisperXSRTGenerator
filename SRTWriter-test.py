import unittest
from SRTWriter import SRTConverter


class TestSRTConverter(unittest.TestCase):
    def setUp(self):
        # Sample segment data
        self.segments = [
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
            },
            {
                "start": 3.055,
                "end": 5.1,
                "text": "My name is John Doe.",
                "words": [
                    {"word": "My", "start": 3.055, "end": 3.216, "score": 0.996},
                    {"word": "name", "start": 3.276, "end": 3.476, "score": 0.979},
                    {"word": "is", "start": 3.556, "end": 3.637, "score": 0.63},
                    {"word": "John", "start": 3.737, "end": 4.017, "score": 0.684},
                    {"word": "Doe.", "start": 4.057, "end": 4.358, "score": 0.531},
                ],
            },
            {
                "start": 5.1,
                "end": 6.803,
                "text": "Here's a funny story about a dog.",
                "words": [
                    {"word": "Here's", "start": 5.1, "end": 5.4, "score": 0.619},
                    {"word": "a", "start": 5.44, "end": 5.46, "score": 0.999},
                    {"word": "funny", "start": 5.52, "end": 5.781, "score": 0.812},
                    {"word": "story", "start": 5.841, "end": 6.162, "score": 0.789},
                    {"word": "about", "start": 6.222, "end": 6.422, "score": 0.901},
                    {"word": "a", "start": 6.462, "end": 6.482, "score": 0.999},
                    {"word": "dog.", "start": 6.523, "end": 6.803, "score": 0.993},
                ],
            },
        ]

        self.converter = SRTConverter(self.segments)

    def test_extract_word_segments(self):
        extracted_word_segments = self.converter.extract_word_segments(self.segments)

        # Dynamically check the number of words in all segments
        expected_word_count = sum(len(segment["words"]) for segment in self.segments)
        self.assertEqual(len(extracted_word_segments), expected_word_count)

        # Check for the presence of key fields in the first word segment
        for key in ["word", "start", "end"]:
            self.assertIn(key, extracted_word_segments[0])

    def test_to_srt_highlight_word(self):
        srt_highlighted = self.converter.to_srt_highlight_word("red")
        self.assertIsInstance(srt_highlighted, str)

        # Check if the first word of the first segment is correctly highlighted
        first_word = self.segments[0]["words"][0]["word"]
        expected_highlighted_word = f'<font color="red">{first_word}</font>'
        self.assertIn(expected_highlighted_word, srt_highlighted)

    def test_to_srt_single_words(self):
        srt_single_words = self.converter.to_srt_single_words()
        self.assertIsInstance(srt_single_words, str)

        # Check the format for the first word in the SRT output
        first_word = self.segments[0]["words"][0]["word"]
        first_word_start_time = self.converter.format_time(
            self.segments[0]["words"][0]["start"]
        )
        first_word_end_time = self.converter.format_time(
            self.segments[0]["words"][1]["start"]
        )  # End time is start of next word

        expected_first_entry = (
            f"1\n{first_word_start_time} --> {first_word_end_time}\n{first_word}"
        )
        self.assertIn(expected_first_entry, srt_single_words)

    def test_adjust_word_per_segment(self):
        words_per_segment = 3
        adjusted_segments = self.converter.adjust_word_per_segment(words_per_segment)

        for segment in adjusted_segments:
            self.assertLessEqual(len(segment['words']), words_per_segment)

            # Ensure that the words in the segment are a continuous subset of the original words
            original_words = [word['word'] for segment in self.segments for word in segment['words']]
            adjusted_words = [word['word'] for word in segment['words']]
            self.assertTrue(all(word in original_words for word in adjusted_words))

            # Check that start and end times of segments are set correctly
            self.assertEqual(segment['start'], segment['words'][0]['start'])
            self.assertEqual(segment['end'], segment['words'][-1]['end'])

    def test_to_srt_plain_text(self):
        # Test without specifying words_per_segment
        srt_plain_text = self.converter.to_srt_plain_text()
        self.assertIsInstance(srt_plain_text, str)

        # Check the format for the first segment in the SRT output
        first_segment_text = self.segments[0]["text"]
        first_segment_start_time = self.converter.format_time(self.segments[0]["start"])
        first_segment_end_time = self.converter.format_time(self.segments[0]["end"])

        expected_first_entry = (
            f"1\n{first_segment_start_time} --> {first_segment_end_time}\n{first_segment_text}"
        )
        self.assertIn(expected_first_entry, srt_plain_text)

        # Test with specifying words_per_segment
        words_per_segment = 3
        srt_plain_text_adjusted = self.converter.to_srt_plain_text(words_per_segment)
        self.assertIsInstance(srt_plain_text_adjusted, str)

        # Check the number of words in the first segment of the adjusted SRT output
        first_adjusted_segment_words = srt_plain_text_adjusted.split('\n')[2].split()
        self.assertLessEqual(len(first_adjusted_segment_words), words_per_segment)

    def test_create_segments_from_words(self):
        word_segments = [
            {"word": "Hello", "start": 0.0, "end": 0.5},
            {"word": "world", "start": 0.6, "end": 1.1},
            {"word": "this", "start": 1.2, "end": 1.7},
            {"word": "is", "start": 1.8, "end": 2.3},
            {"word": "a", "start": 2.4, "end": 2.9},
            {"word": "test", "start": 3.0, "end": 3.5}
        ]

        words_per_segment = 2
        created_segments = SRTConverter.create_segments_from_words(word_segments, words_per_segment)

        # Check if the number of created segments is correct
        expected_segment_count = len(word_segments) // words_per_segment
        self.assertEqual(len(created_segments), expected_segment_count)

        # Check the first created segment
        first_segment = created_segments[0]
        self.assertEqual(first_segment["start"], 0.0)
        self.assertEqual(first_segment["end"], 1.1)
        self.assertEqual(first_segment["text"], "Hello world")

        # Check the last created segment
        last_segment = created_segments[-1]
        self.assertEqual(last_segment["start"], 2.4)
        self.assertEqual(last_segment["end"], 3.5)
        self.assertEqual(last_segment["text"], "a test")

        # Check for correct number of words in each segment
        for segment in created_segments:
            self.assertLessEqual(len(segment['words']), words_per_segment)
            
    def test_initialize_with_normalized_timestamps(self):
        segment_array_1 = [
            {"start": 0.0, "end": 2.0, "text": "Segment 1", "words": [{"word": "Segment", "start": 0.0, "end": 1.0}, {"word": "1", "start": 1.0, "end": 2.0}]},
            {"start": 2.0, "end": 4.0, "text": "Segment 2", "words": [{"word": "Segment", "start": 2.0, "end": 3.0}, {"word": "2", "start": 3.0, "end": 4.0}]}
        ]

        segment_array_2 = [
            {"start": 0.0, "end": 2.0, "text": "Segment 3", "words": [{"word": "Segment", "start": 0.0, "end": 1.0}, {"word": "3", "start": 1.0, "end": 2.0}]},
            {"start": 2.0, "end": 4.0, "text": "Segment 4", "words": [{"word": "Segment", "start": 2.0, "end": 3.0}, {"word": "4", "start": 3.0, "end": 4.0}]}
        ]

        # Assuming the lengths of the audio segments are 4 seconds and 6 seconds respectively
        audio_lengths = [4, 6]

        converter = SRTConverter.initialize_with_normalized_timestamps([segment_array_1, segment_array_2], audio_lengths)

        # Check if the number of segments is correct
        self.assertEqual(len(converter.segments), 4)

        # Check if the timestamps of the second array are normalized correctly
        self.assertEqual(converter.segments[2]["start"], 4.0)
        self.assertEqual(converter.segments[2]["end"], 6.0)
        self.assertEqual(converter.segments[3]["start"], 6.0)
        self.assertEqual(converter.segments[3]["end"], 8.0)  # Corrected expectation

        # Check if words in the segments have normalized timestamps
        for word in converter.segments[2]["words"]:
            self.assertTrue(4.0 <= word["start"] < 6.0)
            self.assertTrue(4.0 <= word["end"] <= 6.0)
        for word in converter.segments[3]["words"]:
            self.assertTrue(6.0 <= word["start"] < 8.0)  # Corrected expectation
            self.assertTrue(6.0 <= word["end"] <= 8.0)   # Corrected expectation


if __name__ == "__main__":
    unittest.main()
