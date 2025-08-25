split-adjusted ohlcv

set a trade index based on oip\_boost1\_csv ROW# or something, save/remember for later



Def a canonical entry for training (e.g., open on filing+1) but also compute alt-entry returns (close, VWAP proxy = (H+L+C+O)/4) to later choose spec entry by context?



**date indexing**

-buy at market open (only if hasn't drifted up insanely from filing/trade maybe)

 	-of next trading day (p0=m0=t0) after filing date(m1=t-1), call this mebuydate(p0=m0)

**Pentry** = **Open**\_p0 = Open\_mebuydate

note: parquet dates are yyyy-mm-dd, oip\_mega\_boost1 dates are mm/dd/yyyy or m/d/yyyy



add as columns (for ea row of trade data)

**FORWARD** RETURNS EVAL DATA: do this for 30td into the future, ie up to \_p030 inclusive.

o\_ret\_p001 = (open\_p1/Pentry)-1

h\_ret\_p001 = (high\_p1/Pentry)-1

volume\_p001 = volume of mebuydate +1td



**LOOKBACKS**: for ea trade, eaday in past60td also has:(ie)

note: \_m001 is t-1td where t=0=mebuydate, so m001 is filing date lol.

o\_m001 = open price of mebuydate minus 1 td (from ticker's parquet open\_sa column

h\_m001 = high"

l\_m001 = low

c\_m001 = close

volume\_m001 = volume

avp\_m001 = avg(o,h,l,c) price (as the most likely tradeable value-ish?) "av"

o\_rel\_m001 = (o-av)/av (open of that day, relative to the av^ of that day)

h\_rel\_m001 = (h-av)/av (high of that day, relative to...

l\_rel\_m001 = (l-av)/av (low..

c\_rel\_m001 = (c-av)/av (close...

c2clog\_m001 =Close-to-close log return = ln(c\_m001/c\_m002).

onlog\_m001 = Overnight= ln(o\_m001/c\_m002).

intrad\_m001 =Intraday: = ln(c\_m001/o\_m001).

volume\_m001 = volume\_sa from parquet



add: relative volume(s) metrics?

add: current price/vol vs historical price/vol indicators-a few lookbacks? capture "a recent drawdown" at the very least - maybe as a 0/1

add: lookback rollings?:range position, gap size, true range/atr, **rangebasedvolatility (sig close simple, sig gk, and then c/gk)**, momentum-rolling log-returns d2d, liquidity, price loc vs rolling x-day high/low, rolling ADV, zscoring? Include recent lags (last 5–10 days) of key features to capture dynamics. **Normalize by rolling ATR/σ to be regime-agnostic?**

norm by ticker? trade lookback only? across all tickers? years? month? idek.



**TRADE DATA:**

OG-keep/use these ie:(filing\_date	trade\_date	ticker	company\_name	insider\_name	title	trade\_type	qty	owned	value	insider\_price	d\_own\_plus%\_isnew	d\_own\_plus%	mebuydate

10/11/2022	10/11/2022	PLAY	Dave \& Buster'S Entertainment, Inc.	Quartieri Michael	CFO	P - Purchase	5000	41185	158633	31.73	0	14	10/12/2022

)

NEW compute from csv^ and new market data/ticker pricing data:

title\_COB = 1/0 if 'COB' is anywhere in title (someppl have multiple listed)

same for title\_CEO,Pres,COO,CFO,GC,VP,Dir,10%,Co-,

trade2file\_raw = raw (all) days from trade\_date to filing\_date

trade2file\_td = trading days between the two

trade\_close\_v\_open = (c-o)/o on trade\_date

filing\_close\_v\_open = (c-o)/o on filing\_date

filing\_v\_insider = (close price on filing\_date - insider\_price)/insider\_price

fvi\_v\_retm001\_m015 = filing\_v\_insider / ((close price on m001 - close on m015)/close on m015)



**MARKET DATA -S\&P500**

sp500\_ft1.csv has raw and features local (all lookbacks)

upload to hpc

new script adding to those^: build\_sp500\_features.py

result is parquet in rawdata sp500\_features.parquet

**then compute beta/alpha rolling stuff relative to ea trade when join later by date**

**(join by filing date so dont have data from mebuydate yet)**



**PREDICTION/TARGETS/MODEL**

need hard af classifer that successfully drops the shit out of any/all trades that do not go positive at any point so i dont even enter them.

&nbsp;	-target label for training - 0 if no positive return from entry in p015 td? thoughts on this? any of ohlc counts? or whats a good metric for being able to reasonably break even + a little buffer? then do the following predictions for the 1s (had any reasonable + return):

 	-im thinking of trading semi-manually (if goes above 2/3/4/5/10/15% return at any point in next couple days (**up to ~14 trading days seems dece tbh, ez sell**)

 	-ideally predict hold duration til significant return relative to entry (ie <2,<3, <10, <20, <30, notsig, ALLNEG)-or maybe continuous hold and predicts the magnitude of return (maybe across all windows for better manual checking? so i know what to look for when trading)

&nbsp;	-maybe model stop loss at -5/10/15% to start? ideally model will weed out any that are predicted to tank super bad, and i can just hold through any small (1-5% drawdowns until they go up).

&nbsp;	-need to see if this strat even plays out tbh. gonna play around a lot with targeting / strategy mix 

3\) Forward path outcomes (use H/L)

MFE\_H (max favorable excursion): max\_{k∈\[1,H]} (H\*\_{t+k}/C\*\_{t} - 1).

MAE\_H (max adverse excursion): min\_{k∈\[1,H]} (L\*\_{t+k}/C\*\_{t} - 1).

Time-to-hit to ±barriers (first k where return crosses target/stop).

End return at H: (C\*\_{t+H}/C\*\_{t} - 1).











 

