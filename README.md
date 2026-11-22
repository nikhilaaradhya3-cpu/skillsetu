# SkillSetu

**A verified skill passport for people who learned their trade by doing it.**

Built by Team GENTECH (Presidency University, Bengaluru) for wHACKiest 2026, Mystery Track (UnlockED), Problem 1: Localized Vocational Skill Verification.

> Status: ideation stage. The pitch deck and architecture are done; the demo is being built. This README says what we plan to build, and marks what already works.

## The problem

A plumber, electrician or mason can have ten years of real skill and still have nothing a stranger can check. Every new job starts from zero trust.

- India's informal workforce is roughly 80-90% of workers (SBI Research, 2026).
- Only 4.1% of people aged 15-59 have formal vocational training, while 30.6% learned a trade informally: family, self-taught, on the job (PLFS 2023-24).
- Certificates need enrolment or a centre visit. Job apps mostly rely on self-declared profiles. Word of mouth only works inside one neighbourhood.

## Our idea

SkillSetu turns a two-minute phone video of a real task into a verified, shareable skill passport, in Kannada, Hindi or English.

1. The worker picks a trade and a **task card** (for example: wire a two-way switch, fix a joint leak).
2. They record a short video, narrate what they are doing, and read out a random **on-screen code** so the video cannot be reused.
3. An AI model checks the video against a **trade rubric** and returns what passed, what did not, and why. This is a pre-score, not the final verdict.
4. A contractor or past client **vouches** for the worker through a link and OTP. The Verified badge needs a human.
5. The worker gets a **passport page** with a QR code and a WhatsApp link. Employers can search by trade and area.

## Why two layers of trust

AI alone can misjudge, and vouches alone can be faked or biased. SkillSetu uses both: the AI gives an instant, consistent rubric result, and local vouches add accountability. Neither is enough on its own.

## Example rubric (electrician, two-way switch)

The rubric is a plain JSON file, so adding a new trade means adding a new file, not new code.

- Wires are stripped to the right length and fully seated in the terminals
- Live and neutral are connected to the correct terminals
- Insulation is intact, with no exposed copper outside the terminal
- Power is isolated before work starts
- The worker explains each step in their own words

## Architecture

```
Worker app (React PWA)  ->  API (FastAPI on AWS)  ->  Integrity checks (ffmpeg, imagehash, liveness code)
Voucher web link (OTP)  ->                         ->  AI scoring (Gemini video + ElevenLabs Scribe)
                                                   ->  Database + storage (Supabase Postgres, AWS S3)
                                                   ->  Passport page + employer search (React, QR code)
```

## Tech stack

| Layer | Tool |
|---|---|
| Frontend | React + Tailwind (PWA), MediaRecorder API |
| Voice | ElevenLabs (speech to text and text to speech), i18n JSON |
| Backend | FastAPI (Python) |
| Database / storage | Supabase Postgres, AWS S3 |
| AI | Gemini multimodal API, structured JSON output |
| Integrity | ffmpeg, imagehash |

## What the demo will cover

- [ ] Pick a task card and upload a video
- [ ] AI scores the video against the rubric and shows the result
- [ ] Passport page with a QR code

Not in the first demo (shown as mockups only): vouch link with OTP, employer search, Kannada voice prompts.

## Risks and how we handle them

- **AI misjudges:** it only pre-scores. Verified needs a human vouch.
- **Fake vouches:** OTP, rate limits, and more weight to vouchers who are verified themselves.
- **Weak network:** client-side compression and a retry queue.
- **Privacy:** explicit consent, a delete-my-data option, and the public page shows only fields the worker picks.

## Team GENTECH

- Nikhil D P (lead)
- V Aishwarya
- Manya S M
- Monisha M

## Licence

MIT
