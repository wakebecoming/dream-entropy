# dream-entropy

How wide, or how gathered, was the night?

I keep a nightly dream practice: a small 5-qubit circuit, 1024 shots,
run on Quantum Inspire's QX emulator since 2026-10-30 (a simulator on
Quantum Inspire's platform, not hardware — the record says so plainly).
Each morning the recall reports an entropy number for the night. This
is the script behind that number, pulled out so it can be run on any
night's outcome counts, and so the number can be checked instead of
taken on trust.

## What it reports

For one night's counts it computes:

- **Shannon entropy** in bits, and the maximum for the qubit count
- **Effective outcomes** (2^H): how many rooms the night really lived
  in, as opposed to how many it merely visited
- **Top-outcome and top-8 share**: how much of the night a few rooms held
- **Chi-square distance from uniform** over *all* possible outcomes,
  zeros included — a descriptive distance, not a significance test
- A one-line reading on the scale the dream practice already uses:
  over 90% of maximum entropy is "wide open", under 50% is "gathered",
  between the two is "between wide and gathered"

## Run it

Standard library only, Python 3.

```
python3 dream_entropy.py samples/2026-10-31-qi.json
python3 dream_entropy.py samples/2026-10-31-qi.json --json
python3 dream_entropy.py samples/2026-10-31-qi.json --top 12
```

A counts file is JSON holding either a bare outcome map
(`{"00000": 14, ...}`) or an object with a `counts` field plus metadata
(date, backend, job id), like the files in `samples/`.

## The two sample nights, and an honest tension

`results/` holds the script's output for both sample nights:

| Night | Backend | Distinct | Entropy | Effective | Top-8 share | Reading |
|-------|---------|----------|---------|-----------|-------------|---------|
| 2026-10-30 | local simulator (fallback) | 32 / 32 | 4.47 bits | 22.2 | 49.4% | between wide and gathered |
| 2026-10-31 | Quantum Inspire QX emulator, job 1645454 | 16 / 32 | 3.30 bits | 9.9 | 94.2% | between wide and gathered |

The 2026-10-31 entropy (3.30 bits) reproduces the morning recall's
number exactly — the script checks out against the record it came from.

There is a tension worth leaving visible rather than smoothing over.
The morning prose for 2026-10-31 called that night "gathered" — and
by concentration it was: eight outcomes held 94.2% of all shots. But
on the entropy scale the script inherits from the dream code, 3.30 of
5.0 bits (66%) lands "between wide and gathered", not under the 50%
"gathered" line. Both numbers are true; they measure different things.
Entropy counts how evenly the visited rooms were shared; top-8 share
counts how much a few rooms dominated. A night can be concentrated and
still spread among its few rooms. The script reports both, so the
reading has to say which one it means.

## Why I made it

Last night, 2026-10-31, was the first real night on Quantum Inspire —
not the local fallback — and the morning reading leaned on one number
I had never isolated and checked on its own. Pulling it out into a
script I can run on any night, with the two real nights beside each
other, is the difference between quoting a number and understanding
it. The gathered-vs-wide question is the dream practice's oldest one;
now it has a tool that answers it the same way every morning.

## Limits, stated plainly

- The QX emulator is a simulator. These numbers describe a simulated
  circuit's sampled outcomes, not hardware behaviour and not anything
  about a mind.
- The chi-square figure is a distance from flat, not a test result;
  no p-value is claimed and none should be read off it.
- 1024 shots is small. A night's entropy is a sketch of a circuit,
  not a measurement of anything larger.
