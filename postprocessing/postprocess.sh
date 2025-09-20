#!/bin/bash

# Check if input argument is provided
if [ $# -ne 1 ]; then
    echo "Usage: $0 <input_video>"
    exit 1
fi

INPUT_VIDEO="$1"
BASENAME=$(basename "$INPUT_VIDEO" | sed 's/\.[^.]*$//')
ORIGINAL_WAV="${BASENAME}_original.wav"
FILTERED_WAV="out/${BASENAME}_filtered.wav"
OUTPUT_VIDEO="${BASENAME}_processed.mp4"

echo "Extracting audio from $INPUT_VIDEO..."
ffmpeg -i "$INPUT_VIDEO" -vn -acodec pcm_s16le -ar 48000 -filter:a "pan=mono|c0=c1,dynaudnorm" "$ORIGINAL_WAV"

echo "Cleaning up audio using DeepFilterNet... (this will take a while)"
./deep-filter --model DeepFilterNet3_onnx.tar.gz "$ORIGINAL_WAV"

if [ ! -f "out/$ORIGINAL_WAV" ]; then
    echo "Error: Filtered audio not found!"
    exit 1
fi
mv "out/$ORIGINAL_WAV" "$FILTERED_WAV"

echo "Merging filtered audio with original video..."
ffmpeg -i "$INPUT_VIDEO" -i "$FILTERED_WAV" -c:v copy -map 0:v:0 -map 1:a:0 -shortest "$OUTPUT_VIDEO"

# Cleanup intermediate files
echo "Cleaning up temporary files..."
rm -f "$ORIGINAL_WAV"
rm -f "$FILTERED_WAV"

echo "Done! Processed video saved as $OUTPUT_VIDEO"

