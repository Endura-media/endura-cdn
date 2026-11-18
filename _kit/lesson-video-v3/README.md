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

## Layout v19 (Kui approved Nov 17: "perfect") — use render19.py
- **TikTok safe zone:** nothing under the top search bar (final y < ~200), the right button rail (x > ~960) or the bottom caption (y > ~1700).
- **Final frame step:** render the slide at 1080x1920, crop rows 150–1780, scale to 972x1467, paste on white at (54, 160). Equal side margins, whole layout slightly high.
- **No slow zoom.** Slides stay still (only the short slide-in at each cut).
- **Kui:** always bottom-left, same size on every slide (HOSTPOS (440, 250, 1745) before the final step), arms down, blink + lip sync. Never centered/large on end slides.
- **Captions:** ONE fixed spot for the whole video: one line, fixed dark box x 420–980, y 1546–1636 (before the final step), text centered in it, max ~500px of text per chunk. Never move between slides.
- **Slide content start height:** every slide's content starts at the same height (top of content = y 538 before the final step; Kui's pick: where "No price on your site?" sits). Tall slides (steps, proof) start higher only if they would hit Kui's head (content bottom max y 1270). Slide 1 (pain character, no Kui) shift 120.
- **Top pill + slide number removed** (they would float mid-screen after the shift).
- Check: stills with a TikTok UI overlay (top bar, right rail, bottom caption) before sending a cut.

## Build steps
1. Voice: ElevenLabs "Kui Teaching" (GIOrDlUaJqLczq2St7ik), no square brackets in text (eleven_v4 reads them as tags). Kui downloads the MP3 if the file host is blocked.
2. Word timings: ElevenLabs Scribe (free) → words.json [{text,start,end}].
3. Slide backgrounds: frames.py with NOHOST=1 NOCHAR=1 OUTDIR=bases2/ (edit each scene's text/layout there).
4. Set scene start times in the render script from words.json; set icon pop times to the spoken word.
5. Render: python3 render19.py (character drawn at the HOSTPOS height; ~1 min for 60s) (PIL frames piped to ffmpeg libx264 veryfast crf 20 + aac). ~5 min for 60s.
6. Check stills at 4–5 times (faces, captions, overlaps) before sending Kui the cut.
7. Fonts: Inter / Inter Display (system). Paths in the scripts assume /home/claude/lesson; adjust.
