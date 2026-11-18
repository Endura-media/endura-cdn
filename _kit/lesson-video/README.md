# Endura Lessons video build kit (V008, Oct 26 2026)

- build.py: builds the whiteboard lesson video (PIL frames → ffmpeg, word-timed captions, sound kit, 4% zoom per scene).
- frames.py: styles (white, navy #0E2033, gold #B8860B, red #CD3232) and drawing helpers.
- words.json: ElevenLabs Scribe word timings for the Lesson #01 voiceover.
- sfx/: pop, whoosh, ding, buzz, thud.
- Voiceover MP3 is NOT stored here, on purpose: a clean voice track could be used to clone Kui's voice. Get it back from the ElevenLabs flow (Kui voice 1qirMZmpTjNydJJDGjWI) with the built-in-browser download trick in claude/endura-lessons-log.md, and save it as lesson01_vo.mp3 next to build.py.
- No secrets and no client data belong in this repo.
