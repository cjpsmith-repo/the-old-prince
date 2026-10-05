# Split, start, or neither? The Old Prince 1871

Source: 796 finished games from the 18xx.games bulk export (`old_prince_games_2026-07-26.json`, 897 games in total; 99 still active and 2 that the current engine can no longer replay were excluded). Every game was replayed through the 18xx.games engine, and the replay reproduced each game's recorded final scores exactly, so the board state at every decision is real rather than reconstructed.

Outcome measure: a player's final net worth divided by the table average (1.00 = average). A difference of +0.03 is about 3% of average net worth, roughly **$140** (average final net worth was about $4,700). Every comparison controls for the player's standing at the moment of the decision, their skill (finish in their *other* games), phase and player count, with errors clustered by game.

## What the data says

### 1. Use the slot. Splitting and starting are worth about the same on average
In the 4,475 player-stock-rounds where a split was legal, taking the open tranche slot (by splitting or starting) beat doing neither by about **+0.02**. Split and start were indistinguishable on average (+0.019 each).

The exception is the endgame. Once phase 7 or D is reached, or in the final stock round, a new company was worth nothing or slightly negative. The strongest windows were phases 3+ and 4+ (about +0.06 and +0.04) and the early H phases.

### 2. Split instead of start when the parent's other shares sit in the market, not with opponents
This is the clearest result, and it holds for 3- and 4-player games, for older and newer games, and when each player is only compared with themselves.

| Parent's non-president shares are held... | Split minus start |
|---|---|
| mostly by the open market | **+0.030** |
| mixed | +0.004 |
| mostly by other players | **-0.026** |

### 3. Don't split a parent with no trains
Splitting a trainless parent instead of starting cost about **-0.11** (roughly $500). This was the largest effect found, though only 73 such splits exist.

### 4. More parent treasury cash favours splitting
Each extra $100 in the parent's treasury moved the comparison about +0.009 toward splitting.

### 5. Inside a split: float the branch this round, and give it some cash
- A branch that did not float in the same stock round (9% of splits) cost about **-0.05**.
- Moving cash from parent to branch: **+0.024**. Moving a train: +0.016 (not conclusive).
- Giving away more than the one required station: -0.029 (not conclusive).
- The gap between parent share price and branch par, and therefore the immediate paper loss, did **not** predict outcomes.

### Things that did not matter
- Whether an opponent or the starter held the PEIR share of the company being started.
- Your own percentage of the parent, once co-holders are accounted for.

## Why: the logic behind it

### What each move actually does
**Starting a PEIR company.** You pay twice par for the president's certificate. Then you (or others) buy shares until 60% is out of the bank, at which point the bank pays the company 10 times par. Every share purchase is a cash-for-stock swap at par, so it doesn't change your net worth. Your existing holdings are untouched.

**Splitting.** The bank pays the new branch par times the branch shares still in the market, which is about $450 to $530. Nobody pays into it. In exchange you give up three things:
- **Paper value.** Two of your parent shares, plus half of any others, become branch shares at par. The parent shares you hand over sit in the parent's treasury, and treasury shares count toward nobody's net worth until a player buys them. That paper loss had a median of $62.
- **Stations.** The parent permanently loses at least one station.
- **Your action and your place in the pass order.** Splitting uses your stock-round action and takes you out of the pass order.

The new branch still needs 60% of its shares out of the market to float, so you will usually spend cash on about three more branch shares.

**The new company itself is the same either way.** Branches and started companies of the same age ran the same number of operating rounds. They paid out about the same total (about $1,600 to $1,650 each on average) and gained the same median share price (+$20). The difference between the two moves is entirely in what each does to *your other holdings* and to *who owns the new company*.

### Two companies under one president act as one pooled system
Companies may sell trains to each other at any price from $1 up to the buyer's entire treasury. In practice this lets one president move cash and trains freely between their companies. It happened 4,566 times between companies with the same president and only 42 times between different presidents. The typical sale took most of the buyer's treasury, with a median of 83% to 97% depending on the companies involved. A split therefore doesn't just add a company. It adds a second treasury, a second train allowance under the train limit, and a second set of station slots to one pool you control. Train sales directly between a parent and its own branch occurred in about 40% of games that had a split, with money flowing both ways in similar amounts.

### Losing a station: how much does it hurt the parent?
Track isn't owned. Any company can run on any track. What the parent loses is a **station**, which matters in three ways:
1. Every route must include one of the company's own stations.
2. A company can only lay track connected to its own stations.
3. A full city blocks any company without a station there. The branch's station can therefore turn a city the parent used to run *through* into a wall.

To measure it, I replayed every split and, at the parent's next three runs, re-optimised its routes twice: once as the board really was, and once with the given-away stations handed back to the parent. The optimiser reproduced the revenue players actually ran in 97% of cases.

| Situation | Runs where the parent earns less | Average revenue lost |
|---|---|---|
| All parent runs after a split | 36% | 5% |
| Given-away city still has an open slot | 7% | under 1% |
| Given-away city is now full, so it blocks the parent | 52% | 8% |
| Gave away two stations instead of one | 58% | 10% |
| Split in phase 7 or D (long trains) | 45% | 8% |

So yes, it hurts, but usually modestly, and almost entirely through blocking. **Give away a station in a city that still has an open slot, or one at the end of a line, never a city on the parent's main through-route.** Give away one station, not two.

**Why it rarely shows up in your final score:** in 1871 a company's share price moves one step right for paying *any* dividend and one step left for withholding. The size of the payout doesn't matter. Losing $15 of revenue costs the parent's shareholders a little cash, not share price. Only the 11% of splits that cost the parent more than 15% of its revenue leaned negative for the splitter (-0.028, not conclusive).

### Why the parent's other shareholders matter so much
It isn't that opponents get rich. Opponents who held parent shares at a split finished no better or worse than other opponents. They gain branch shares but take the same paper loss you do. What changes is how much of the new company *you* end up owning, and how secure it is.

| Parent's loose shares held by... | Branch starting cash | Your branch % after float | Opponents' branch % | Branch later taken over |
|---|---|---|---|---|
| Mostly the market | $530 | 54% | 9% | 1.4% |
| Mixed | $512 | 51% | 15% | 2.4% |
| Mostly other players | $462 | 47% | 25% | 5.5% |

When the loose shares sit in the market, the exchange costs nothing. The market's half goes into the parent's treasury, and the parent can sell those shares later to raise cash. The market's branch shares still count toward the branch's starting money. You end up owning most of a well-funded branch. When opponents hold the loose shares, they walk away owning a quarter of your new company with a base to take it over. The branch also starts with one share less of bank money.

Watch the parent too. After a split your parent stake can shrink to the president's certificate alone, and the parent's treasury now holds shares anyone can buy. **When an opponent's parent stake tied or beat yours right after the split, you lost the parent later half the time** (versus 5% otherwise).

### Why a trainless parent is a trap
Every company with a valid route must own a train. After a split, both companies need one. The branch's bank money usually covers one train. The parent must then emergency-sell its new treasury shares, which drops its price a step per sale, or you pay from your own pocket. Starting a fresh company instead leaves the parent to buy its train with its own treasury.

### Why the branch needs cash, especially late
The branch's money is about par × 8. That fits the mid-game trains well. At $65 par in phase 3+ or 4+, $455 to $520 buys a 3+ ($240) plus a 4+ ($200). In phase 7 the only legal par is $58, so a branch gets at most $464, **less than the cheapest train left** (a 7 at $500, or a D at $600). A late branch that isn't handed cash or a train can't operate. Two-thirds of late splitters gave the branch cash or a train.

### Why timing matters, and why the endgame kills the move
- **The arc of a typical game.** Stock round 4 is usually 4H, round 5 ranges from 4H to 2+, round 6 is 2+ to 4+, round 7 is 7, and round 8 onward is D. Tranche slots fill around rounds 4, 5, 5, 6, 6 and 7. Splits fill few early slots (4% of the first) and half of the last, because a parent needs two stations first.
- **Slots are scarce.** All six slots were used in 82% of games, so the slot you take is often one an opponent wanted.
- **A new company needs time to pay back.** It turns free bank cash into value only by paying dividends, one share-price step at a time. Company treasury cash counts for no one at game end. Branches finished with a median $127 stranded in their treasuries. Started late, a company gets too few operating rounds, which is why the move is worth about nothing from phase 7 on.
- **The best windows are phases 3+ and 4+.** Games then still have two or three sets of three operating rounds left, trains are cheap relative to a branch's bank money, and parents have typically placed their second station.

### Other rules worth knowing
- **Certificate limit.** A split swaps two 10% parent certificates for one 20% branch certificate, which frees a certificate slot. This is logic from the rules, not measured.
- **Paper loss.** The gap between the parent's price and the branch par didn't predict results. The value isn't destroyed, just parked in the parent's treasury.

### Published strategy sources
BoardGameGeek, YouTube and podcast sites are blocked from the environment this analysis ran in, so none of the published discussion could be read. Promising sources to read and compare: the BGG thread "General strategy discussion" (https://boardgamegeek.com/thread/2974175), written by a player with about 20 games, mostly 3-player; Choo Choo Crew episode 18, chapter "Tranches, Splitting, and New Companies" at 125:32; and the Heavy Cardboard 3-player teach. The designer's rules PDF contains no strategy notes.

## Rule of thumb
Take the slot unless it is phase 7 or later. **Split** when all of these hold:
- the parent has a train and some cash;
- most of its non-president shares are in the market, not with opponents;
- no opponent's parent stake will match yours after the exchange;
- you can float the branch this round;
- you can give away a station in a city with an open slot.

Give the branch cash, and treat the two companies as one pool for trains and money. **Start a new company instead** when opponents own a big chunk of your parent or the parent has no train.

## Caveats
These are observational results from online play, not a controlled experiment. The controls remove the obvious biases, but players who split well may differ in ways skill does not capture. Effects of about 0.02 to 0.03 are real but modest, worth $100 to $150. Win rate alone is too noisy to confirm or refute them.

## Reproducing
1. Clone https://github.com/tobymao/18xx and set `ENGINE_LIB` to its `lib/` folder. `gem install require_all`; `pip install pandas statsmodels`.
2. Unzip the games JSON, then run `ruby extract.rb games.json out0.jsonl 0 1` (or shard with `SHARD NSHARDS`) and concatenate the output into `all.jsonl`.
3. Run `build.py`, `skill.py`, `m1.py`, `m2.py` (writes `cs.pkl`), `m3.py` (writes `d_ss.pkl`), then `m4.py`, `m5.py`, `m6.py` and `peir.py`.
4. Context analyses: `ctx1.py` (branch vs started company lifetimes), `ctx2.py` (opponents holding the parent), `ctx3.py` (parent strength), `ctx4.py` and `ctx5.py` (lost presidencies), `ctx6.py` (ownership after float), `ctx7.py` (tranche filling and phase by round).
5. Station counterfactual: `ruby extract2.rb games.json cf0.jsonl 0 1`, then `cfan.py` and `blockout.py`. `extract2.rb` includes a local fix for an argument-count bug in the engine's hex-train distance check.
