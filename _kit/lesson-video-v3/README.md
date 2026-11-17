# Lesson-of-the-week animation kit v3 (Endura Universe look) — Nov 16, 2026

First approved build: Lesson 04 "ChatGPT pricing" (videos/2026-11/2026-11-17_L04_chatgpt-pricing_FINAL.mp4). Kui: "this is the best you've done."

## Look (Kui's rules)
- White slides, 1080x1920, 30fps. Slide content centered. Kui bottom-left (~520px tall), captions to his right (max 4 words, active word gold #FBC550 on a dark pill).
- ONLY Kui's real Endura Universe art. **From v12 (Nov 16): art/ORIGINAL_APPROVED_ENDURA_HOST.png (1122x1402, from Kui's "Endura Animation Starter V1" pack) via hdhost.py (HostHD)** — about 4x sharper than the old art/host_front.png. Never a lookalike or a ChatGPT-made kit. The pack's 9 pose PNGs are only ~284px tall: too soft to use full size.
- Kui: full body, arms down, no arm animation. Only a blink (clean full eye swap, ~0.12s every 3.3s) + mouth driven by the voice volume. Class: HostHD in hdhost.py (render12.py). Old class HostStill3 in rig.py = fallback only.
- Eyes: keep the art's own eyes and pupils (HostHD does). Never redraw them big and close together (looks cross-eyed).
- No other people except the opening pain character (sad roofer on slide 1, SadRoofer in rig.py: hammer down, looking down, no rain cloud).
- Use icons for ideas (icons.py: people → chat bubbles → money stack), popping in centered as the words are spoken.
- End card: headline right above Kui, caption right under him, no extra pills.
- Proof slide: real screenshot, circle the source + the dollar value in gold, blur the phone after the area code.

## Build steps
1. Voice: ElevenLabs "Kui Teaching" (GIOrDlUaJqLczq2St7ik), no square brackets in text (eleven_v4 reads them as tags). Kui downloads the MP3 if the file host is blocked.
2. Word timings: ElevenLabs Scribe (free) → words.json [{text,start,end}].
3. Slide backgrounds: frames.py with NOHOST=1 NOCHAR=1 OUTDIR=bases2/ (edit each scene's text/layout there).
4. Set scene start times in the render script from words.json; set icon pop times to the spoken word.
5. Render: python3 render12.py (character drawn at the HOSTPOS height; ~1 min for 60s) (PIL frames piped to ffmpeg libx264 veryfast crf 20 + aac). ~5 min for 60s.
6. Check stills at 4–5 times (faces, captions, overlaps) before sending Kui the cut.
7. Fonts: Inter / Inter Display (system). Paths in the scripts assume /home/claude/lesson; adjust.
