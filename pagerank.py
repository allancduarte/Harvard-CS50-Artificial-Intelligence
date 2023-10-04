import os
import random
import re
import sys

DAMPING = 0.85
SAMPLES = 10000


def main():
    if len(sys.argv) != 2:
        sys.exit("Usage: python pagerank.py corpus")
    corpus = crawl(sys.argv[1])
    ranks = sample_pagerank(corpus, DAMPING, SAMPLES)
    print(f"PageRank Results from Sampling (n = {SAMPLES})")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")
    ranks = iterate_pagerank(corpus, DAMPING)
    print(f"PageRank Results from Iteration")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")


def crawl(directory):
    """
    Parse a directory of HTML pages and check for links to other pages.
    Return a dictionary where each key is a page, and values are
    a list of all other pages in the corpus that are linked to by the page.
    """
    pages = dict()

    # Extract all links from HTML files
    for filename in os.listdir(directory):
        if not filename.endswith(".html"):
            continue
        with open(os.path.join(directory, filename)) as f:
            contents = f.read()
            links = re.findall(r"<a\s+(?:[^>]*?)href=\"([^\"]*)\"", contents)
            pages[filename] = set(links) - {filename}

    # Only include links to other pages in the corpus
    for filename in pages:
        pages[filename] = set(
            link for link in pages[filename]
            if link in pages
        )

    return pages


def transition_model(corpus, page, damping_factor):
    """
    Return a probability distribution over which page to visit next,
    given a current page.

    With probability `damping_factor`, choose a link at random
    linked to by `page`. With probability `1 - damping_factor`, choose
    a link at random chosen from all pages in the corpus.
    """
    distribution = {}

    for web_page in corpus:
        distribution[web_page] = 0

    if len(corpus[page]) == 0:
        for web_page in distribution:
            distribution[web_page] = 1/len(corpus)
        return distribution
    else:
        for web_page in distribution:
            distribution[web_page] = (1 - damping_factor) / len(corpus) + damping_factor / len(corpus[page])

    return distribution



def sample_pagerank(corpus, damping_factor, n):
    """
    Return PageRank values for each page by sampling `n` pages
    according to transition model, starting with a page at random.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    pr = {}

    for web_page in corpus:
        pr[web_page] = 0

    current_page = random.choice(list(pr))
    for i in range(n):
        pr[current_page] += 1
        distribution = transition_model(corpus, current_page, damping_factor)
        current_page = random.choice(list(distribution))

    for page in pr:
        pr[page] = pr[page]/n

    return pr


def iterate_pagerank(corpus, damping_factor):
    """
    Return PageRank values for each page by iteratively updating
    PageRank values until convergence.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    tolerance = 0.001

    prev_ranks = {}
    for page in corpus:
        prev_ranks[page] = 1/len(corpus)

    while True:
        new_ranks = {}

        for page in corpus:
            pagerank = (1 - damping_factor) / len(corpus)
            for other_page, links in corpus.items():
                if links and page in links:
                    pagerank += damping_factor * (prev_ranks[other_page] / len(links))
                elif not links:
                    pagerank += damping_factor * (prev_ranks[other_page] / len(corpus))
            new_ranks[page] = pagerank

        # Check for convergence
        converged = all(abs(new_ranks[page] - prev_ranks[page]) < tolerance for page in corpus)

        if converged:
            return new_ranks

        prev_ranks = new_ranks.copy()

if __name__ == "__main__":
    main()
