June 26, 2021. Please use the python3_master branch.

This is a tor scraper. Some artifacted code remains that loops through all tor sites one at a time, but then it was computed that even with multi-threading and a timeout at 1/10th of a second, this would take 2^80 divided by 12 (number of threads) divided by 10 (tenth of a second per timeout) seconds to complete.

In order to run this, use the Python console: "torify python3" or "torify python."
