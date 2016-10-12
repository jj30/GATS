import urllib.request
import string
from multiprocessing import Pool
import time
from bs4 import BeautifulSoup

# tor address schema
symbols = string.ascii_lowercase + "".join(map(str, range(2, 8)))
known_tor = []
known_down = []
success_file = open('success.txt', 'a')

def increment(start):
    # if right - most digit is not max, add 1 to
    # it if it is, zero it out, add one to the right - most
    # minus that digit val
    digit = start[len(start) - 1]
    rest = start[0:len(start) - 1]

    if digit == "7":
        return increment(rest) + "a"
    else:
        # get next in list (add 1)
        return rest + symbols[symbols.find(digit) + 1]

def tor_ping(start, log=True):
    try:
        print("TESTING: http://" + start + ".onion/")
        with urllib.request.urlopen('http://' + start + '.onion/', timeout=2) as response:
            html = response.read()
            code = response.getcode()

            if len(html) > 0 and code == 200:
                if (log):
                    success_file.write('\nSuccess: http://' + start + '.onion')
                print('success http://' + start + '.onion/')
                return True

    except:
        print("FAILED: http://" + start + ".onion/")
        return False

def main():
    # torify curl http://3g2upl4pq6kufc4m.onion/
    # start = "a" * 16
    # start = "3g2upl4pq6kufc4m"
    start = "aaaaaaaaaaaamg4b"
    i = n = 0

    while (True):
        file_target = open('out.txt', 'a')

        all = []
        while (i in range(255 * n, 255 * (n + 1))):
            all.append(start)
            start = increment(start)
            i = i + 1

        # now that 'all' is 255, throw at pool
        with Pool(processes = 12) as pool:
            pool.map(tor_ping, all)

            # tor can only handle 255 at a time
            pool.terminate()

        # n is the outer loop
        n = n + 1
        file_target.write("\nLast address: " + all[len(all) -1])
        file_target.close()

def calc_ms(file):
    nCounter = 0
    elasped = 0
    minimum = 60 # 60 seconds
    maximum = 0
    get_contents = open(file, 'r')

    for line in get_contents:
        # a little string manipulation
        start_string = min(line.find("http://"), 0) + len("http://")
        end_string = line.find(".onion")
        address = line[start_string : end_string]

        start = time.time()
        bResult = tor_ping(address, False)
        end = time.time()

        if (bResult):
            elapsed = elasped + (end - start)
            nCounter = nCounter + 1

            # compare min and max with elapsed time
            minimum = min(minimum, elapsed)
            maximum = max(maximum, elapsed)

    get_contents.close()
    avg = elapsed / nCounter
    return [minimum, avg, maximum]

def crawl():
    # open known_tor_sites
    get_known_tor = open("known_tor_sites", 'r')
    lines = get_known_tor.readlines()
    for l in lines:
        original_line = l
        # hit site as in the file and base of site, ie, http://w.com/x/y/z.html and http://w.com
        l = [ l.strip() ]
        l2 = "/".join(original_line.split("/")[0:3])
        if (l != l2):
            l += [ l2 ]
        crawl_array(l)
def crawl_array(arry):
    def root_site(site):
        root = site.split("/")[2]
        return root.split(".onion")[0]
    for site in arry:
        try:
            with urllib.request.urlopen(site, timeout=10) as response:
                html = response.read()
                code = response.getcode()
                if len(html) > 0 and code == 200:
                    file_name = root_site(site)
                    # top level only
                    scrape = open("HTMLPages/" + file_name + ".html", 'w')
                    scrape.write(html.decode("utf-8", errors="ignore"))
                    soup = BeautifulSoup(html, 'html.parser')
                    link_array = soup.find_all('a')
                    #print ("link_array length:" + str(len(link_array)))
                    link_array = [x for x in link_array if ".onion" in x]
                    if len(link_array) > 0:
                        print ("FOUND SOME: " + "\n".join(link_array))
                        crawl_array(link_array)
        except Exception as e:
            print("SITE: " + site + ":::" + e)
            pass

if __name__ == '__main__':
    crawl()

    # [nMSTorMin, nMSTorAvg, nMSTorMax] = calc_ms("known_tor_sites")
    # [m, nAvg, ax] = calc_ms("known_tor_sites")
    # print("\nminimum: ".format(m))
    # print("\naverage: ".format(nAvg))
    # print("\nmaximum: ".format(ax))

    # success_file.close()
    #main()
