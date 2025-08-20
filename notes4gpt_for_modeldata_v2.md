split-adjusted ohlcv

use nyse trading calendar via pmc

note that all trades considered are P only (open mkt buy)

alr have trade2file and trade2file\_td as cols

set a trade index based on oip\_boost1\_csv ROW# or something, save/remember for later

adj\_close always i think



Define a canonical entry for training (e.g., open on filing+1) but also compute alt-entry returns (close, VWAP proxy = (H+L+C+O)/4) to later choose entry policy by context.





date indexing

-buy at market open (only if hasn't drifted up insanely from filing/trade maybe)

&nbsp;	-of next trading day (p0=m0) after filing date(m1), call this mebuydate(p0=m0)



**main price value to track**:/add as columns for ea row of trade data eventually

av\_p\_p1 = avg(o,h,l,c) price (as the most likely tradeable value)

&nbsp;	note: \_p1 =data for 1 trading day after mebuydate(p0=m0)

ea day also has:(ie)

or\_p1 = (o-av)/av (open of that day, relative to the av^ of that day)

hr\_p1 = (h-av)/av (high of that day, relative to...

lr\_p1 = (l-av)/av (low..

cr\_p1 = (c-av)/av (close...

do this^ for 30td into the future, ie up to \_p30. 

and for lookback too: 





RETURNS - need buy price/timing info first tho -@open/close/avg of mebuy? when exactly is mebuy?

add:

av\_r\_p1 = 



add: (c-o)/o on trade date, and (c-o)/o on filing date











&nbsp;



