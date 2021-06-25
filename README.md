This has been upgraded to Python3.9.5.

This is a tor crawler/scraper. Some artifacted code remains that loops through all tor sites one at a time, but then it was computed that even with multi-threading and a timeout at 1/10th of a second, this would take 2^80 divided by 12 (number of threads) divided by 10 (tenth of a second per timeout) seconds to complete. It is true that brute force is probably the only way to get to sites that don't no other sites link to, but the crawler works pretty well. I was able to find 34 new onion sites in 15 minutes.

In order to run this, edit your \Tor Browser\Browser\TorBrowser\Data\torrc file and add at the bottom:

SocksPort 9050

and restart Tor. This allows Python to use Tor by proxy on port 9050.

There have been substantial improvements to the dark web since I ran this code some years back. First, even with headers, some sites manage to detect that the code is indeed a bot. 