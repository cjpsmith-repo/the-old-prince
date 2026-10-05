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

**Both moves are free capital from the bank.** In 1871 every share is bought from the market, so a started company's 10× par and a branch's par × (branch shares left in the market) are both paid by the bank. The share purchases players make are cash-for-stock swaps at par. What you are really choosing is *which* free company to take and what it costs you to get it. That is why both beat passing until the game is too short for a new company to pay back.

**A split hands each parent shareholder half their stake in your new company.** Opponents who own parent shares receive branch shares for free. They become co-owners of the company you just created, and the branch gets less bank capital because fewer branch shares remain in the market. When those parent shares sit in the market instead, the exchange costs you nothing. The market's half goes into the parent's treasury, where the parent can later sell it for cash at full price. Meanwhile the market's branch shares still count toward the branch's starting capital. A split of a market-heavy parent therefore turns the bank's stake into fuel for you. A split of an opponent-heavy parent gives them a slice of your new railroad.

**A trainless parent turns one train crisis into two.** After the split both the parent and the branch must own a train. The branch's starting cash usually buys one train. The parent must then emergency-sell its new treasury shares, which drives its price down, or you pay from your own pocket. Starting a fresh company leaves the parent to buy its train undisturbed.

**Cash in the parent is the lever you control.** You choose how to divide the parent's cash. The branch's bank capital, typically $450 to $520, buys about one mid-game train. Topping it up lets the branch run a real route immediately without starving the parent.

**A branch that doesn't float is pure cost.** The parent has already lost a station, and you have taken the paper loss on the share exchange. Until 60% of the branch leaves the market it earns nothing and misses a whole set of operating rounds. Splitting uses your action, so plan to buy the remaining float shares on your next turns in that same round. Budget for about three shares at par.

**The share-price gap looks scary but washes out.** Swapping parent shares at, say, $94 for branch shares at $74 shows an immediate paper loss. But the parent shares aren't destroyed. They go into the parent's treasury, and the branch's price climbs if it pays dividends. In the data the size of that gap had no effect on final results.

## Rule of thumb
Take the slot unless it is phase 7 or later. **Split** when the parent has a train and some cash, most of its non-president shares are in the market, and you can float the branch this round. Give the branch cash. **Start a new company instead** when opponents own a big chunk of your parent or the parent has no train.

## Caveats
These are observational results from online play, not a controlled experiment. The controls remove the obvious biases, but players who split well may differ in ways skill does not capture. Effects of about 0.02 to 0.03 are real but modest, worth $100 to $150. Win rate alone is too noisy to confirm or refute them.

## Reproducing
1. Clone https://github.com/tobymao/18xx and set `ENGINE_LIB` to its `lib/` folder. `gem install require_all`; `pip install pandas statsmodels`.
2. Unzip the games JSON, then run `ruby extract.rb games.json out0.jsonl 0 1` (or shard with `SHARD NSHARDS`) and concatenate the output into `all.jsonl`.
3. Run `build.py`, `skill.py`, `m1.py`, `m2.py` (writes `cs.pkl`), `m3.py` (writes `d_ss.pkl`), then `m4.py`, `m5.py`, `m6.py` and `peir.py`.
