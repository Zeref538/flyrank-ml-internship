# What Are You Proving? — John Andrei Martinez

## Proof statement

I can ship machine-learning results that survive honest validation instead of quietly failing on it — the kind of claim that's easy to say and rare to actually test. In Week 1 of my FlyRank internship, I fit a decision tree on 30,000 pages and scored it in-sample, where it looked competitive (Precision@50 around 0.60–0.72). Then I re-ran the same comparison with a client-holdout split — testing the tree only on clients it had never seen — and it dropped to 0.400 Precision@20 and 0.520 Precision@50, losing to my own simple hand-written rule (0.650 and 0.640). Honest validation didn't just lower my number, it flipped my conclusion: the model I would have shipped was worse than the rule I'd have thrown away. I wrote that finding up as-is instead of hiding it, and made client-holdout testing mandatory for the rest of my capstone. The one person I'm speaking to is a hiring manager screening candidates for a junior AI/ML or data role. The one action I want from them: email me at martinezjandrei8425@gmail.com to talk about it.

## Why this needs to exist

A CV can list "built a decision tree" and stop there; it can't show a hiring manager the moment my own result got worse under a harder, more honest test and I kept the worse number anyway — and that moment is the actual proof I do this the right way, not just that I know the vocabulary.
