import logging
log = logging.getLogger("submodels")

def submodel_generator(result, pat, current, maxn, countonly=False):
    if pat:
        curmax = max(pat)
    else: 
        curmax = 0
    for i in range(current):
        if i-1 <= curmax:
            newpat = pat[:]
            newpat.append(i)
            if current == maxn:
                if not countonly:
                    result.append(newpat)
                else:
                    result[0] += 1
            else:
                submodel_generator(result, newpat, current+1, maxn, countonly)


def a_choose_b(n,k):
    return reduce(lambda a,b: a*(n-b)/(b+1),xrange(k),1)

def count_greedy_schemes(N):
    count = 1
    for i in range(N-1):
        j = i + 1
        count = count+a_choose_b(j,2)
    return count

def count_greedy_parts(N):
    count = N
    count = count + a_choose_b(N,2)
    count = count + sum(range(N-1))
    return count


def bell_numbers(N):
    ## Return the bell number for N subsets
    # script modified from Wikipedia: http://en.wikipedia.org/wiki/Bell_number
    N = N+1                          ## Bell numbers are indexed from zero 
    t = [[1]]                        ## Initialize the triangle as a two-dimensional array
    c = 1                            ## Bell numbers count
    while c <= N:
        if c >= N:
            return t[-1][0]          ## Yield the Bell number of the previous row
        row = [t[-1][-1]]            ## Initialize a new row
        for b in t[-1]:
            row.append(row[-1] + b)  ## Populate the new row
        c += 1                       ## We have found another Bell number
        t.append(row)                ## Append the row to the triangle
 

def get_submodels(N):
    """Return all the submodels

    Let's do a test case:
    >>> submodels = get_submodels(4)
    >>> for s in submodels:
    ...     print s
    [0, 0, 0, 0]
    [0, 0, 0, 1]
    [0, 0, 1, 0]
    [0, 0, 1, 1]
    [0, 0, 1, 2]
    [0, 1, 0, 0]
    [0, 1, 0, 1]
    [0, 1, 0, 2]
    [0, 1, 1, 0]
    [0, 1, 1, 1]
    [0, 1, 1, 2]
    [0, 1, 2, 0]
    [0, 1, 2, 1]
    [0, 1, 2, 2]
    [0, 1, 2, 3]
    """
    log.debug("Generating submodels for %s partitions", N)
    result = []
    submodel_generator(result, [], 1, N)
    log.debug("Resulting number of partitions is %s", len(result))
    return result

def count_submodels(N):
    """Count the number of submodels we've got
    These are the right numbers...
    >>> print count_submodels(1)
    1
    >>> print count_submodels(5)
    52
    >>> print count_submodels(10)
    115975
    """
    result = [0]
    submodel_generator(result, [], 1, N, countonly=True)
    return result[0]

if __name__ == "__main__":
    import doctest
    doctest.testmod()
    
    print "Getting All Submodels for N=5"
    result = get_submodels(5)
    for a in result:
        print a