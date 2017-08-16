acme
====

Getting Started
---------------

- Change directory into your newly created project.

    cd acme

- Create a Python virtual environment.

    python3 -m venv env

- Upgrade packaging tools.

    env/bin/pip install --upgrade pip setuptools

- Install the project in editable mode with its testing requirements.

    env/bin/pip install -e ".[testing]"

- Run your project's tests.

    env/bin/pytest

- Run your project.

    env/bin/pserve development.ini



Regarding network hash rate, since ppcoin is designed with variable spacing target for proof-of-work blocks, you cannot directly compare network hash rate to other block chains based on proof-of-work difficulty. To estimate network hash rate you would need to first get an estimate of current proof-of-work spacing target (in seconds), by counting the number of proof-of-work blocks in the last 24 hours for example. The formula to calculate the total network hash rate is: hash rate = difficulty * 4G / spacing target.

----------------------------

The hashrate can be calculated from the expected rate of finding a block (144 a day), the actual rate of finding a block and the current difficulty.

So let's calculate the average hash_rate for a single day:

expected_blocks = 144
difficulty = 11187257.461361 # this is on May 22nd 2013
blocks_found = 155 # Also May 22nd 2013
hash_rate = (blocks_found/expected_blocks*difficulty * 2**32 / 600)
The reason we use a day to average out the hash_rate is that taken block by block the variance would be really high and we would not get anything meaningful.

According to WolframAlpha this gives us an averagge hash_rate for the 22nd May 2013 of 86.19 THashes/s. Numbers of course may vary depending on how you chose your interval, which appears to be the reason numbers don't match with the ones on Blockchain.info

-------------------------------

Here's an updated formula for calculating blocks/day:

blocks/day = chains/day * (0.97 * (1 - fracDiff) + 0.03)

Here fracDiff is the fractional part of the difficulty, i.e. fracDiff = diff - floor(diff).

This is simply assuming that it's a 0.03 probability for the (k+1)'th number being prime in a chain. These result in longer chains which are not subject to the fractional difficulty. This number was produced by the function EstimateNormalPrimeProbability() in my latest code. It's a bit smaller than my previous estimate of 0.035 being the probability.

--------------

mikaelhJan '14
Ok, here's my attempt to answer many of the questions in this thread. Let's take our latest 13-chain from yesterday as an example:

    {
        "time" : "2014-01-20 11:57:59 UTC",
        "epoch" : 1390219079,
        "height" : 368051,
        "ismine" : false,
        "mineraddress" : "AeKNrjNjtSncLJjUrDnQbrfzMS1NEq95Ta",
        "primedigit" : 107,
        "primechain" : "1CC0d.c48332",
        "primeorigin" : "12512390300891276190682243916246636610000954402441740274147501230375694290702478259358177371388272647651840",
        "primorialform" : "106680560818292299253267832484567360951928953599522278361651385665522443588804123392*61#"
    }
This is a Cunningham chain of the first kind (1CC). Other possible types are the second kind (2CC) and BiTwin (TWN).
The numbers of a 1CC chain look like this:
origin * 2^i - 1

Here 'i' starts from zero. So the first prime in the chain is origin - 1, the second prime is origin * 2 - 1, and then origin * 4 - 1, etc.

In Primecoin mining the origin is composed like this:
origin = headerHash * primorial * candidateMultiplier

The header hash is an intermediate hash calculated from the block header (it is NOT the final block hash). It's a 256-bit number that is required to be greater than 2^255.

The primorial p# is defined as the product of all primes up until 'p', which means that 61# = 2 * 3 * 5 * 7 * 11 * 13 * 17 * 19 * 23 * 29 * 31 * 37 * 41 * 43 * 47 * 53 * 59 * 61 = 117288381359406970983270.

The candidate multiplier is a number produced by sieve. It's typically less than 1 million. The sieve uses an efficient algorithm to filter out a large number of prime factors. The sieve rejects all candidates x for which headerHash * primorial * x * 2^i - 1 is divisible by one of the first 8000 prime numbers.

Side note: The "extended" sieve algorithm considers multipliers of the form 2^j * x. So we are multiplying all the candidate numbers by powers of 2. It turns out that these new candidates can be checked efficiently because we are shifting the origin so that the second prime becomes the first prime and the third prime becomes the second prime etc.

I think many people are still wondering what "1CC0d.c48332" means. I already explained that 1CC is a Cunningham chain of the first kind. '0d' is the length of the chain in hexadecimal (that is 13). 'c48332' is the 24-bit representation of the fractional length. We can convert it into the usual decimal notation:
0xc48332 / 0xffffff = 0.7676

So our example chain would meet a difficulty of 13.7676.

Ghashes are not applicable to Primecoin. I'm guessing some websites are trying to interpret the Primecoin difficulty like it would be Bitcoin/Litecoin difficulty, which doesn't produce any sensible results. My Primecoin charts show the average prime chain rate for the network:
http://xpm.muuttuja.org/charts/

Right now it's about 1.94 chains/min. So the total 'chainsperday' of the whole network would be about 2793 chains/day.

