#!/usr/bin/env python
#import required modules
from datetime import datetime as dt
import sys, random, optparse
try:#python 3
    import urllib.request as req
    from urllib.error import URLError, HTTPError
    three = True
except ImportError:#python 2
    import urllib2 as req
    three = False

#custom header to avoid being blocked by the website
custom_headers = {"User-Agent" : "Mozilla/5.0 (Windows NT {}; rv:{}.0) Gecko/20100101 Firefox/{}.0".format(random.randint(7,11),
                                                                                                           random.randint(40,50),
                                                                                                           random.randint(35,50))}

def adjustDomainName(domain):#correct domain name for urllib
    if domain.startswith("www."):
        domain = domain[4:]
    if not domain.startswith("http"):
        domain = "http://" + domain
    if domain.endswith("/"):
        domain = domain[:-1]
    return domain

def loadWordList(wordlist_file, ext):#load pages to check from dictionary
    try:
        with open(wordlist_file, encoding="utf8") as wlf:
            content = wlf.readlines()
        for i in range(len(content)):
            content[i] = content[i].strip("\n")
        if ext.lower() == "a":
            return content
        else:
            return [element for element in content if element.endswith(ext) or element.endswith("/")]
    except FileNotFoundError:
        sys.exit("\033[1;31;40m Couldn't find wordlist file!")

def saveResults(file_name, found_pages, progress=0):
    now = dt.now()
    with open("results.txt", "a") as f:
        stamp = "%d-%d-%d %d: %d: %d" % (now.year, now.month, now.day, now.hour, now.minute, now.second)
        print(stamp, file=f)
        for page in found_pages:
            print(page, file=f)
        print("total progress: %d\n______________________________________________" % progress, file=f)

def main(domain, progress=0, ext="a", strict=False, save=True, visible=True, wordlist_file="admin.txt"):
    print("working... press ctrl+c at any point to abort...")
    resp_codes = {403 : "request forbidden", 401 : "authentication required"}#HTTP response codes
    found = []#list to hold the results we find
    domain = adjustDomainName(domain)#correct domain name for urllib

    print("loading wordlist...")
    attempts = loadWordList(wordlist_file, ext)
    print("\033[1;33;40m scanning...")
    
    for link in attempts[progress:]:#loop over every page in the wordlist file
        try:
            site = domain + "/" + link

            if visible:#show links as they're being tested
                print("\033[1;33;40mTesting=>",  end=" ")

            panel_page = req.Request(site, headers=custom_headers)
            
            try:
                resp = req.urlopen(site)#try visiting the page
                found.append(site)
                print("\033[1;32;40m %s Valid link" % site)

            except HTTPError as e:#investigate the HTTPError we got
                if three:
                    c = e.getcode()
                else:
                    c = e.code()
                    
                if c == 404:
                    if visible:
                        print("\033[1;31;40m %s not found..." % site)
                else:
                    print("%s potential positive.. %s" % (site, resp_codes[c]))
                    if not strict:
                        found.append(site)

            except URLError:
                print("invalid link or no internet connection!")
                break
            
            except Exception as e2:
                print("an exception occured when testing {}... {}".format(site, e2))
                continue
            progress += 1
            
        except KeyboardInterrupt:#make sure we don't lose everything should the user get bored
            print()
            break

    if found:
        if save:#save results to a text file
            print("Saving results...")
            saveResults("results.txt", found)

            print("results saved to results.txt...")

        print("found the following results: " + "  ".join(found) + " total progress: %s" % progress)

    else:
        print("\033[1;35;42m could not find any panel pages... Make sure you're connected to the internet\n" \
              + "or try a different wordlist. total progress: %s" % progress)

def getRobotsFile(domain):
    print("Attempting to get robots.txt file...")
    found = []
    domain = adjustDomainName(domain)#correct domain name for urllib
    
    robots_file = domain + "/robots.txt"
    try:
        data = req.urlopen(robots_file).read().decode("utf-8")
        for element in data.split("\n"):
            if element.startswith("Disallow:"):
                panel_page = domain + element[10:]
                print("Disallow rule found: %s" % (panel_page))
                found.append(panel_page)
        if found:
            print("admin panels found... Saving results to file...")
            saveResults("results.txt", found, 0)
            print("Done...")
        else:
            print("could not find any panel pages in the robots file...")
    except:
        sys.exit("Could not retrieve robots.txt!")

if __name__ == "__main__":
    print("     \033[1;36;40m   +++++++++++++++++++Admin_Panel_Finder By Krissh++++++++++++++++++++")
    print("     \033[1;36;40m   +                subscribe my channel for more tools              +")
    print("    \033[1;36;40m    +    I am not responsible for malicious use!     KRISSH KUMAR     +")
    print("    \033[1;36;40m    +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++\n\n")
    parser = optparse.OptionParser("\033[0;35;40m Usage: python admin.py --domain <target domain> \n" \
                                   + "--progress <index of the page the script reached last run> \n" \
                                   + "--page_extension <website language> --strict <True or False> \n" \
                                   + "--save <Save the results to a text file?>\n " \
                                   + "--verbose <print links as they're tested?> --wordlist <dictionary file to use>\n" \
                                   + "--robots <if True don't enter anything else except the domain name>\n")

    domain_help = "target domain. eg: google.com or www.newidea.tech"
    progress_help = "(optional) index of the page the script reached last run. The script " \
                    + "displays and saves this value in the results file after every run. "\
                    + "0 starts from the beginning."
    page_extension_help = "(optional) whether the website uses html asp php... default value is 'a' which checks everything"
    strict_mode_help = "(optional, default False) if True, HTTP codes that correspond to forbidden or " \
                       + "authentication required will be ignored."
    save_help = "(optional, default True) if True results will be saved to a txt file."
    verbose_help = "(optional, default True) if True each link will be shown as it's being tested."
    wordlist_help = "(optional, default is the included wordlist) wordlist file to be used."
    robots_help = "(optional, default False) if True the script will try to get the robots.txt " \
                  + "file that usually contains the admin panel. If you set it to True, don't enter" \
                  + "anything else except the target domain."

    parser.add_option("--domain", dest="domain", type="string", help=domain_help)
    parser.add_option("--progress", dest="progress", type="string", help=progress_help)
    parser.add_option("--page_extension", dest="page_ext", type="string", help=page_extension_help)
    parser.add_option("--strict", dest="strict", type="string", help=strict_mode_help)
    parser.add_option("--save", dest="save", type="string", help=save_help)
    parser.add_option("--verbose", dest="verbose", type="string", help=verbose_help)
    parser.add_option("--wordlist", dest="wordlist", type="string", help=wordlist_help)
    parser.add_option("--robots", dest="robots", type="string", help=robots_help)

    (options, args) = parser.parse_args()

    if not options.domain:
        sys.exit("please enter a target domain:\n\n%s" % parser.usage)

    try:
        strict_mode = eval(options.strict.title())
    except:
        strict_mode = False

    try:
        save = eval(options.save.title())
    except:
        save = True

    try:
        verbose = eval(options.verbose.title())
    except:
        verbose = True

    if not options.page_ext:
        page_ext = 'a'
    else:
        page_ext = options.page_ext

    if not options.progress:
        progress = 0
    else:
        progress = int(options.progress)

    if not options.wordlist:
        wordlist = "admin.txt"
    else:
        wordlist = options.wordlist

    try:
        robots = eval(options.robots.title())
    except:
        robots = False

    if robots:
        getRobotsFile(options.domain)
    else:
        main(options.domain, progress, page_ext, strict_mode, save, verbose, wordlist)
