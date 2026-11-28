# Dialogue, ambience, and music

## Cast the episode

Listen to the exchange before assigning voices. Use the recording, visible mouths, microphone distance, and who answers whom to identify each turn. Keep a speaker's voice consistent across cuts. One person on screen can be answering an off-camera host. A silent shot with captions may need only captions and location sound.

Use your own authorized voice or a licensed stock voice for the host. Assign distinct voices to other recurring speakers. Keep unrelated crowd chatter as ambience where appropriate. Use the original picture and sound to identify turns. Once the dub is mixed, use its final words for the English dialogue captions and SRT. Keep the display intervals locked to the corresponding Chinese captions when adjusting speech placement. Overlapping speech can overlap in the English version.

## Generate and place turns

Resolve permitted voice and model IDs in your ElevenLabs account, then create a local JSON plan. Replace all example IDs. Times are seconds from the first displayed frame.

```json
{
  "model_id": "YOUR_MODEL_ID",
  "cast": {"host": "YOUR_HOST_VOICE_ID", "vendor": "YOUR_VENDOR_VOICE_ID"},
  "turns": [
    {"id": "t01", "speaker": "host", "start": 0.3, "end": 2.4, "text": "What are you cooking?"},
    {"id": "t02", "speaker": "vendor", "start": 2.3, "end": 3.8, "text": "Fresh fish."}
  ]
}
```

Review the uncached character count before generating speech. The count estimates input volume; the service determines the price. Use the same local cache for retries and edits.

```sh
python3 scripts/voice.py plan.json voice-cache
```

For paid generation, provide the authorized key in the process environment as `ELEVENLABS_API_KEY`. Confirm any needed spending approval before using the generation flag.

```sh
python3 scripts/voice.py plan.json voice-cache --generate
python3 scripts/place_voices.py plan.json voice-cache --duration 90 --output narration.wav
```

Generated speech, character timings, and receipts are stored under a hash of the voice ID and request payload. A run with an incomplete submission stops so you can reconcile its receipt with the provider's history. Changing only a turn's start and end reuses its speech. If a line runs too long, shorten its translation or extend its placement into available silence. After changing a take or its wording, update the corresponding English cues and SRT from the accepted audio. The placement script allows modest pitch-preserving acceleration and reports turns that cannot fit. For an episode without dialogue, skip TTS and omit the voice input when mixing.

## Build the mix

Use a clean ambience stem aligned to the first video frame. If the original includes dialogue, separate the voices from the room or street using a source-separation tool. Audition overlapping speech and cooking sounds. Repair audible speech leakage with a short, crossfaded passage of similar background sound from the scene. Keep action sounds such as a ladle hitting a wok in sync with the picture.

The mixer accepts any combination of ambience, narration, and user-supplied music. Each example below assumes a 90-second timeline.

```sh
python3 scripts/mix-audio.py --duration 90 --bed ambience.wav --voice narration.wav --output mix.wav
```

Lock the picture edit before scoring. Apply its cuts to the isolated dialogue, clean ambience and captions. Then lay a continuous score across the finished timeline and copy the final AAC to both video formats. Listen across every cut as well as the ending.

To loop your own score, pick two matching downbeats and audition the join. The following example repeats the section from 0.75 to 12.75 seconds. A 0.15-second crossfade reads the score through 12.90 seconds. Pick new values for each recording. Without loop points, the score plays once and any remaining time is silent on that stem.

```sh
python3 scripts/mix-audio.py --duration 90 --music score.wav \
  --loop-start 0.75 --loop-end 12.75 --loop-fade 0.15 \
  --bed ambience.wav --voice narration.wav --output mix-scored.wav
ffmpeg -v error -n -i mix-scored.wav -c:a aac -b:a 256k -metadata:s:a:0 language=eng mix.m4a
```

Outputs are 48 kHz stereo PCM WAV files of the requested sample length. The mixer ducks the background during speech. Listen through a quiet answer, a loud cooking action, and a loop boundary before delivering. Keep voices, API credentials, generated dialogue, and licensed music in your private episode workspace.
