
"""
Mobs in the world all are genetic decendants of an alpha and beta monster.

all mobs have a body, skin, and mouth.  everything else is optional.
the other traits if no present, may randomly be added to
offspring.

gene codes/modifier are even, gene value and gene is odd

gene code and modifers are not processed, although
is possible the offspring may aquire a gene from a parent

value is aquired by ANDing together

skin, body, and mouth traits will always be the first 6 bytes

lower generation creatures have a smaller code to work with
as monster generations grow, they have larger code for qualities

off spring are created by bit operations

random bits may be flipped, creating very different monsters

bits have a higher chance of persiting, rather than not
since the opperation is AND on the bits.

this creates a situation where eventually, the dna will be completely full

"""

gene_code = {
"bodyType"        : 0,
"bodyDex"         : 1,
"bodyStr"         : 2,
"bodySize"        : 3,

"skinColor"       : 4,
"skinTexture"     : 5,
"skinHair"        : 6,
"skinPoison"      : 7,

"mouthNum"        : 8,
"mouthLocation"   : 9,
"mouthPoison"     : 10,
"mouthSpit"       : 11,
"mouthSpitDamage" : 12,
"mouthBiteDamage" : 13,
"mouthType"       : 14,

"limbNum"         : 15,
"limbLocation"    : 16,
"limbLength"      : 17,
"limbWidth"       : 18,
"limbTexture"     : 19,
"limbType"        : 20,
"limbStrength"    : 21,
"limbGrasp"       : 22,
"limbDamage"      : 23,

"earNum"          : 24,
"earLocation"     : 25,
"earSkill"        : 26,
"earType"         : 27,

"eyeNum"          : 28,
"eyeLocation"     : 29,
"eyeSkill"        : 30,
"eyeType"         : 31,

"headType"        : 32,
"headLocation"    : 33,
"headHorns"       : 34,

"brainInt"        : 35,
"brainSpeak"      : 36,

"toughness"       : 37,
"spirit"          : 38,

"sexDrive"        : 39,
"sexPotency"      : 40,

"wings"           : 41
}

gene_code_r = dict([(v, k) for (k, v) in gene_code.iteritems()])

import struct
import random
import math
import base64
from gzip import GzipFile
from StringIO import StringIO

class mDNA(object):
    def __init__(self, d, g):
        """
        i tried to make this a system that could include the ability for
        resessive gene traits.

        a gene can onyl be expressed in the create if the gene is active.
        each gene has a value that when combined with the proper partners
        can cause the gene to become active
        """

        self.d = d
        self.g = g

    @staticmethod
    def deconstruct(mdna):
        """
        given a mDNA sequence, return a proper mDNA data

        d = value of the gene
        g = sequence that determines heiredity
        """

        d = {}
        g = {}

        for i in range(len(mdna)):
            if i % 2 == 0:
                key = gene_code_r[ord(mdna[i])]
            else:
                v = ord(mdna[i])
                d[key] = v >> 4
                g[key] = v & 15
 
        return d, g

    @staticmethod
    def create_gene(code, mod, her):
        """
        create a byte sequence that represents this gene sequence

        code = gene code
        mod = modifier
        her = ???
        """

        if mod > 15: mod = 15
        if her > 15: mod = 15
        return chr(code) + chr(mod << 4 | her)

    def mate(self, *parents):
        """
        mate this mDNA with another parent, or parents.
        return a new mDNA object
        """

        parents = list(parents)
        parents.append(self)
        parents = [p.serialize() for p in parents]

        d = {}
        g = {}

        for mdna in parents:
            for i in range(len(mdna)):
                if i % 2 == 0:
                    key = gene_code_r[ord(mdna[i])]
                else:
                    v = ord(mdna[i])
                    mod    = v >> 4
                    genome = v & 15
                    if key in d.keys():
                        dice = random.randint(0,4)
                        if dice == 0:
                            g[key] = g[key] | genome
                        if dice == 1:
                            AND = g[key] & genome
                            OR  = g[key] | genome
                            g[key] = AND | OR
                        if dice == 2:
                            pass
                        if dice == 3:
                            g[key] = genome
                        dice = random.randint(0,2)
                        if dice == 0:
                            pass
                        if dice == 1:
                            d[key] = mod
                        if dice == 2:
                            d[key] = int(math.ceil((d[key] + mod) / 2))
                    else:
                        d[key] = mod
                        g[key] = genome

        return mDNA(d, g)

    def serialize(self):
        # return a string of characters that represents this mDNA
        mdna = ""
        for k, v in self.d.items():
            code = gene_code[k]
            mdna += self.create_gene(code, v, self.g[k])
        return mdna

    def tag(self):
        """
        return a compressed version of the mDNA sequence in base64
        """

        #sio = StringIO()
        #gz = GzipFile(fileobj=sio, mode='wb')
        #gz.write(self.serialize())
        #gz.close()
        print self.serialize()
        return base64.b64encode(self.serialize())

    def mutate(self, chance=100):
        """
        mutate the mDNA by flipping some bits in the the sequence
        """

        mdna = self.serialize()
        mutant = ""
        for i in mdna:
            if random.randint(0,chance) == 0:
                v = ord(i)
                v = v & random.randint(0,15)
                mutant = mutant + chr(v)
            else:
                mutant += i

        self.d, self.g = mDNA.deconstruct(mutant)
        print self.d


def random_beast():
    mdna = ""
    for k, v in gene_code.items():
        mdna += mDNA.create_gene(v, random.randint(0,3), random.sample([0,1,2,4],1)[0])
    return mDNA(*mDNA.deconstruct(mdna))

def calc_score(mdna):
    # used to judge one's gene's over another's
    l = len(mdna)
    score = 0.0
    genes = 0.0
    for i in range(l):
        if i % 2 == 0:
            pass
        else:
            score += ord(mdna[i])
            genes += (ord(mdna[i]) & 15)

    score = int(score / (l/2))
    genes = int(genes / (l/2))
    return score, genes


if __name__ == "__main__":
    
    alpha = random_beast()
    beta  = random_beast()
    gamma = random_beast()
    delta = random_beast()
    population = [alpha, beta, gamma, delta]

    for i in range(4):
        print "generation %d:" % (i + 1)
        for i in range(0, int(math.ceil(len(population) * 0.80))):
            l = len(population) - 1
            if l >= 50:
                for x in range(int(l - (l*.10))):
                    population.pop()
                l = len(population) - 1

            b0 = population[random.randint(0,l)]
            b1 = population[random.randint(0,l)]
            offspring = b0.mate(b1)
            if random.randint(0,10)==0:
                offspring.mutate()
            population.append(offspring)
            print offspring.tag()
