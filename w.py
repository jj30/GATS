import urllib.request
import string
from multiprocessing import Pool
import time
import requests as requests
from bs4 import BeautifulSoup
import re

# tor address schema
symbols = string.ascii_lowercase + "".join(map(str, range(2, 8)))
known_tor = []
known_down = []
success_file = open('success.txt', 'a')
proxies = {
    "http": "socks5h://127.0.0.1:9050",
    "https": "socks5h://127.0.0.1:9050"
}
regexp_onion_url = r'http\S*?\.onion'

# urllib.request.ProxyHandler(proxies=proxies)

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
    sites = []

    for l in lines:
        # http://w.com/x/y/z.html => http://w.com
        line_array_first3 = "/".join(l.split("/")[0:3])
        if not(line_array_first3 in sites):
            sites.append(line_array_first3)

    crawl_array(sites)


def crawl_array(arry):
    def root_site(s):
        # http://x.onion/y/z => http://x.onion/
        all_matches = re.findall(regexp_onion_url, s)
        return all_matches[0] if len(all_matches) > 0 else s

    def filename(site):
        root = site.split("/")[2]
        return root.split(".onion")[0]

    # if you don't, 403
    send_headers = {
         'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
         'Accept-Encoding': 'gzip, deflate, br',
         'Accept-Language': 'en-US,en;q=0.5',
         'Connection': 'keep-alive',
         'Upgrade-Insecure-Requests': '1',
         'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:76.0) Gecko/20100101 Firefox/76.0',
    }

    #     'Cache-Control': 'max-age=0',
    #     'Cookie': '_pk_id.1.97a3=c501706669b695a6.1624642928.; _pk_ses.1.97a3=1',
    #     'DNT': '1',
    #     'Host': 'thehiddenwiki.cc',
    #     'Sec-GPC': '1',
    #     'TE': 'Trailers',
    #     'Referer': 'https://www.host.com/bla/bla/',
    #     'Content-Type': 'application/json',
    #     'X-Requested-With': 'XMLHttpRequest',
    #     'Origin': 'https://www.host.com',

    for site in arry:
        try:
            # urllib.request.ProxyHandler(proxies=proxies)
            # res = requests.get('https://3g2upl4pq6kufc4m.onion/', proxies=proxies)
            # site = 'https://3g2upl4pq6kufc4m.onion/'

            # if (site == 'http://www.darkfailenbsdla5mal2mxn2uz66od5vtzd5qozslagrfzachha3f3id.onion/'):
            #    print ('hit it')

            with requests.get(site, proxies=proxies, headers=send_headers) as response:
                try:
                    html = response.content
                    code = response.status_code

                    if len(html) > 0 and code == 200:
                        file_name = filename(root_site(site))
                        # grab the HTML and save to disk
                        scrape = open("HTMLPages/" + file_name + ".html", 'w')
                        html_string = html.decode("utf-8", errors="ignore")
                        scrape.write(html_string)

                        # get all onion links
                        link_array = re.findall(regexp_onion_url, html_string)

                        # filter out current site
                        link_array = [ea for ea in link_array if root_site(ea) != site]

                        if len(link_array) > 0:
                            print("FOUND SOME: " + "\n".join(link_array))
                            crawl_array(link_array)

                except Exception:
                    pass

        except requests.exceptions.ConnectionError:
            pass

        except Exception as e:
            print("SITE: " + site + ":::" + e.message)
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
