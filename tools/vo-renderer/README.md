# END-VO-A renderer (built Nov 4, 2026 for the 6x video)
1. vo.mp3 (Kui's clone take) -> `ffmpeg -i vo.mp3 -ar 16000 -ac 1 vo16.wav`
2. `python3 seg.py` (silence segments, needs sherpa-onnx whisper base.en) -> segs.json
3. `python3 words.py` (word timestamps, sherpa-onnx-zipformer-en-2023-06-26 from k2-fsa GitHub releases) -> words.json
4. Edit CAP / scenes in render.py. `python3 render.py stills 1.0 5.0 ...` -> stills sheet to Kui first.
5. `python3 render.py` -> mp4 (atempo 1.12). Pull frames from the mp4 and check captions vs words before sending.
Fonts: Inter (system), Instrument Serif Italic + JetBrains Mono from @fontsource (woff -> ttf via fontTools) into ./fonts/.
