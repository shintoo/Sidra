import re
import sys

class SIR(object):
    def __init__(self):
        self.facts = []
        self.debug = False
        

    def add_fact(self, group, phrases):
        for p in phrases.split('|'):
            f = (group[int(p[0])], p[1], group[int(p[2])])
            if self.debug:
                self.debug_print("[*] adding fact: {0}".format(f))
            self.facts.append(f)

        self.debug_print("[*] understood")

    def clear(self):
        self.facts = []

    def get_path(self, group, rule):
        pattern = rule[1:-1]
        start = group[int(rule[0])]
        stop = group[int(rule[-1])]
        ans = []

        p = self.path(pattern, start, stop, ans=ans)
        if self.debug:
            detail = "{0} {1}".format(pattern, ans)
        else:
            detail = ''
        if ans:
            self.debug_print("[*] yes")
            return True
        else:
            self.debug_print("[*] not sure {0}".format(detail))
            return False

    def path(self, pat, start, end, before={}, ans=[], sofar="", indent=" "):
        used = {}
        used.update(before)

        if self.debug:
            self.debug_print("[*]{0}path - {1} to {2}".format(indent, start, end))
        if len(indent) > 20:
            return
        
        for fact in self.facts:
            if used.get(fact):
                continue
            a, rel, b = fact
            if a != start:
                continue
            sts = self.ok_so_far(pat, sofar+rel)
            used[fact] = 1
            if b == end:
                if sts == 2:
                    ans.append(sofar+rel)
            else:
                self.path(pat, b, end, used, ans, sofar+rel, indent+"  ")

    def ok_so_far(self, a, b):
        ans = 2
        while a:
            if re.match("^{0}$".format(a), b):
                return ans
            if a[-1] == '*':
                a = a[:-2]
            else:
                a = a[:-1]
            ans = 1
        return a

    def debug_print(self, string):
        if self.debug:
            print(string)


    def dump(self):
        for p, rel, q in self.facts:
            self.debug_print(" {0}: {1} : {2}".format(p, rel, q))

if __name__ == '__main__':
    sir = SIR()
    while 1:
        sent = raw_input("? ")
        sir.match_sent(sent)
