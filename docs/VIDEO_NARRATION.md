# TAM Demo — Voiceover Narration Script

Word-for-word narration for the demo video, segment by segment, with the target duration each
line has to fit. Use this to regenerate the voiceover in a premium tool (ElevenLabs, Descript,
or your own voice) and hand the audio back — one file per segment, or one continuous track.

- **Total runtime:** ~3:08 (188s).
- **Style:** calm, confident, unhurried — a product walkthrough for leadership, not an ad.
- **Sync rule:** narration for a segment starts ~0.4s after that segment's video begins. Keep
  each line at or under the "narration budget" so it doesn't run past its clip.

> Note: the committed build script (`demo/video_build/build_video.py`) contains a slightly
> respelled version of these lines (e.g. `E X L`, `T R V`, `twenty twenty`) tuned for the
> offline TTS engine. The versions below are the clean, human/premium-voice versions.

---

### 1 — Intro (title card)  ·  segment ~6.1s  ·  narration budget ~5s
> EXL TAM Intelligence. Your market data, on tap.

### 2 — The problem (`start`)  ·  segment ~15.3s  ·  budget ~14s
> Today, EXL's insurance market intelligence is scattered across a dozen workbooks — carriers,
> competitors, revenue, much of it locked in people's heads. Here's what happens when a rep can
> simply ask.

### 3 — Ingestion (`ingest-1` + `ingest-2`)  ·  segment ~41.7s  ·  budget ~40s
> First, adding data. I'm dropping in a spreadsheet the system treats as brand new — it knows
> only that it's a spreadsheet, nothing about the contents. On its own, it profiles the workbook,
> works out the structure of every sheet, figures out how recent the data is, and even learns the
> different ways companies are named. When it finishes, that file is fully queryable. And the key
> point: this exact process runs on any file you add. Nothing is hardcoded, so the system keeps
> growing as the business produces new data.

### 4 — Direct question (`top-10-1` + `top-10-2`)  ·  segment ~29.8s  ·  budget ~28s
> Now, a question: top ten EXL clients by revenue. Notice it doesn't answer from memory — it
> finds the right table, pulls the actual rows, and ranks them. Hartford leads at over eighteen
> million dollars. And every figure is traced back to its source file, and stamped "as of August
> twenty-twenty." You always know where a number came from, and how current it is.

### 5 — Reasoning question (`cognizant-1` + `cognizant-2`)  ·  segment ~21.6s  ·  budget ~20s
> Some questions need reasoning, not just a lookup: where is Cognizant competing against us? To
> answer, it connects our client data with our competitive data across several sheets, and hands
> back the accounts where Cognizant has a foothold. That's the difference between a search box and
> an analyst.

### 6 — Name normalization (`TRV-1` + `TRV-2`)  ·  segment ~30.5s  ·  budget ~29s
> It also speaks the way reps actually type. Ask about "TRV," and it knows you mean Travelers — it
> normalizes the many ways a company's name gets written, so no one needs to know the official
> spelling to get an answer. Then it pulls Travelers' full picture: the relationship, the revenue,
> and who we're up against.

### 7 — Document generation (`PDF-1` + `PDF-2` + `PDF-3`)  ·  segment ~42.8s  ·  budget ~41s
> And it doesn't stop at an answer. Ask for a brief, and it builds one — a clean, client-ready
> document, generated from the same grounded data. Every figure still traced to its source, and
> still dated. A rep goes from a question to something they can walk into a meeting with, in a
> single step. There's nothing to install and nothing to learn — they open a shared workspace,
> and ask. This is EXL's market intelligence, on tap.

---

## Swapping in a premium voiceover
1. Generate audio for each segment (or one continuous track) from the lines above.
2. Drop the files into `demo/video_build/` and point `build_video.py` at them (replace the
   `tts()` step with your audio), **or** send them to me and I'll re-mux against the same clips.
3. Re-run the build. Everything else — clip order, ingest speed-ramp, title card — stays the same.
