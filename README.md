
# SRTConverter Usage Guide

The `SRTConverter` is a Python class designed to manipulate segments from a WhisperX transcription into SRT (SubRip Text) format. This guide provides examples on how to use this class effectively.

## Initialization

To initialize the `SRTConverter`, you need a list of segment dictionaries. Each segment dictionary should contain `start`, `end`, `text`, and a list of `words` with their respective start, end times, and scores.

```python
from SRTConverter import SRTConverter

segments = [
    {
        "start": 0.27,
        "end": 1.632,
        "text": "Hello world.",
        "words": [
            {"word": "Hello", "start": 0.27, "end": 0.61, "score": 0.862},
            {"word": "world.", "start": 0.69, "end": 1.091, "score": 0.779}
        ],
    },
    # ... more segments ...
]

converter = SRTConverter(segments)
```

## Generating SRT Files

### Highlight Words in SRT

To generate an SRT file with specific words highlighted:

```python
srt_highlighted = converter.to_srt_highlight_word(color="red")
print(srt_highlighted)
```

### SRT with Single Words

To create an SRT file where each word is a separate entry:

```python
srt_single_words = converter.to_srt_single_words()
print(srt_single_words)
```

### Plain Text SRT

To generate an SRT file with plain text segments:

```python
srt_plain_text = converter.to_srt_plain_text()
print(srt_plain_text)
```

Optionally, you can specify the number of words per segment:

```python
srt_plain_text_custom = converter.to_srt_plain_text(words_per_segment=3)
print(srt_plain_text_custom)
```

## Adjusting Words per Segment

If you need to reorganize the word segments based on a specific number of words per segment:

```python
new_segments = converter.adjust_word_per_segment(words_per_segment=4)
```

## Static Methods

### Create Segments from Words

To create new segments from a list of word dictionaries:

```python
word_segments = [
    # ... list of word dictionaries ...
]
new_segments = SRTConverter.create_segments_from_words(word_segments, words_per_segment=5)
```

### Writing to a File

To write the generated SRT string to a file:

```python
SRTConverter.write_to_file("output.srt", srt_highlighted)
```

### Validating SRT Strings and Files

To check if an SRT string or file is valid:

```python
is_valid_string = SRTConverter.is_valid_srt_string(srt_string)
is_valid_file = SRTConverter.is_valid_srt_file("output.srt")
```

## Method: `initialize_with_normalized_timestamps`

### Description

The `initialize_with_normalized_timestamps` static method of the `SRTConverter` class initializes the converter with multiple arrays of segments while normalizing their timestamps. This method is particularly useful in scenarios where a long audio or video file has been transcribed in multiple parts (perhaps in parallel), and there's a need to combine these segmented transcriptions into one continuous SRT file.

By normalizing timestamps, this method ensures that each segment follows sequentially from the end of the previous segment, regardless of the starting timestamp of each individual transcription.

### Parameters

- `segment_arrays` (list of lists): A list containing arrays of segment dictionaries. Each array represents a separate part of the transcription, and each segment dictionary within the array should contain keys for `start`, `end`, `text`, and optionally `words`.

### Returns

- `SRTConverter`: An initialized instance of `SRTConverter` with segments that have normalized timestamps.

NOTE NEED TO FIX. IMPLEMENTATION IS WRONG.

I assumed the last transcription time from A would be the end time of the audio, but that is not true. I need to check the actual audio lengths.

### Usage Example

```python
# Assuming you have multiple arrays of segments from parallel transcription processes
segment_array_1 = [
    # ... segments from the first part of the transcription ...
]

segment_array_2 = [
    # ... segments from the second part of the transcription ...
]

# Initialize the SRTConverter with normalized timestamps
converter = SRTConverter.initialize_with_normalized_timestamps([segment_array_1, segment_array_2])

# Now the converter.segments will have a continuous timeline combining segment_array_1 and segment_array_2

```

### Usage Ex. using WhisperX API

https://github.com/m-bain/whisperX?tab=readme-ov-file#python-usage--

```python
# 1. Transcribe with original whisper (batched)
model = whisperx.load_model("large-v2", device, compute_type=compute_type)

audio = whisperx.load_audio(audio_file)
result = model.transcribe(audio, batch_size=batch_size)
print(result["segments"]) # before alignment

# delete model if low on GPU resources
# import gc; gc.collect(); torch.cuda.empty_cache(); del model

# 2. Align whisper output
model_a, metadata = whisperx.load_align_model(language_code=result["language"], device=device)
result = whisperx.align(result["segments"], model_a, metadata, audio, device, return_char_alignments=False)

print(result["segments"]) # after alignment

# 3. Initialize SRTConverter and generate SRT to highlight words
converter = SRTConverter(result["segments"])
highlighted_srt = converter.to_srt_highlight_word(color="red")
SRTConverter.write_to_file("output.srt", highlighted_srt)
```
