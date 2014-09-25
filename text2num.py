import re
import unittest

__author__ = "rodic"
__email__  = "alec.rodic@gmail.com"


nums = {
    "zero"      : 0,
    "one"       : 1,
    "two"       : 2,
    "three"     : 3,
    "four"      : 4,
    "five"      : 5,
    "six"       : 6,
    "seven"     : 7,
    "eight"     : 8,
    "nine"      : 9,
    "ten"       : 10,
    "eleven"    : 11,
    "twelve"    : 12,
    "thirteen"  : 13,
    "fourteen"  : 14,
    "fifteen"   : 15,
    "sixteen"   : 16,
    "seventeen" : 17,
    "eighteen"  : 18,
    "nineteen"  : 19,
    "twenty"    : 20,
    "thirty"    : 30,
    "forty"     : 40,
    "fifty"     : 50,
    "sixty"     : 60,
    "seventy"   : 70,
    "eighty"    : 80,
    "ninety"    : 90,
    "hundred"   : 100,
    "thousand"  : 1000,
    "million"   : 1000000,
    "billion"   : 1000000000,
    "trillion"  : 1000000000000
}

def group_by_type(xs):
    """
    Split list on sequences of same types. Example:
      * [1, 2, 'a', 4, 'b', 'v', 6] => [[1, 2], ['a'], [4], ['b', 'v'], [6]]
    """
    if xs == []: return [ [] ]
    
    t = type(xs[0])
    start = 0
    groups = []

    for i in range(len(xs)):
        if type(xs[i]) is not t:
            groups.append(xs[start:i])
            start = i
            t = type(xs[i])
    groups.append(xs[start:])
    return groups

def calc_value(xs):
    """
    Take list on numbers and convert them to single value.
    Example (forty-four thousand one hundred and sixty-three):
      * [40, 4, 1000, 1, 100, 60, 3] => 44163
    """
    magnitude = [1000000000000, 1000000000, 1000000, 1000, 100]
    
    for mag in magnitude:
        if mag in xs:
            i = xs.index(mag)
            return mag * calc_value(xs[:i]) + calc_value(xs[i+1:])
    return sum(xs)

def join_tokens(xs):
    """
    Split list of strings and ints on sequences of same type,
    calculate value of each seq and join results.
    """
    xs = group_by_type(xs)
    res = ""
    for i in range(len(xs)):
        if type(xs[i][0]) is str:
            res = "%s %s" % (res, " ".join(xs[i]))
        else:
            res = "%s %d" % (res, calc_value(xs[i]))
    return res.strip()

def word_to_number(word):
    """
    If word is a number return its numeric value
    For compound words check each word
    """
    if word.find("-") != -1:
        left, right = word.split("-")
        return "%s-%s" % (word_to_number(left), word_to_number(right))
    try:
        return nums[word.lower()]
    except:
        return word
    
def make_or_reg(xs):
    """
    Join list of words on '|'. 
    Each word is capitalized, in all lower and in all upper cases
    """
    r = "|".join(xs) + "|" + \
        "|".join(map(lambda x: x.capitalize(), xs)) + "|" + \
        "|".join(map(lambda x: x.upper(), xs))
    return r

def text2num(string):
    """
    Convert english number names to their decimal representation
    """
    # Remove 'and' when it is between certain numbers
    left  = [ "hundred", "thousand", "million", "billion", "trillion" ]
    right = nums.keys()

    left, right = make_or_reg(left), make_or_reg(right)
    reg    = r"(%s)\s+and\s+(%s)" % (left, right)
    string = re.sub(reg, r"\1 \2", string) 

    # Remove '-' when it is between certain numbers
    left = [ "twenty", "thirty", "forty", "fifty",
             "sixty", "seventy", "eighty", "ninety" ]
    right = [ "one", "two", "three", "four", "five",
              "six", "seven", "eight", "nine" ]
    left, right = make_or_reg(left),make_or_reg(right)
    reg    = r"(%s)\s?-\s?(%s)" % (left, right)
    string = re.sub(reg, r"\1 \2", string)

    # Replace text for decimal values
    strings  = re.split(r"\s+", string)
    tokens   = map(word_to_number, strings)
    return join_tokens(tokens)


class Text2NumTests(unittest.TestCase):

    # Big nums are from: http://peter-ajtai.com/examples/numbers.php
    
    def testNumsAlone(self):
        self.assertEqual(text2num("zero"), "0")
        self.assertEqual(text2num("Twenty five"), "25")
        self.assertEqual(text2num("ELEVEN"), "11")
        self.assertEqual(text2num("two hundred thirty four"), "234")
        self.assertEqual(text2num("One thousand eleven"), '1011')
        self.assertEqual(text2num(
            "three thousand five hundred sixty seven"), '3567')
        self.assertEqual(text2num(
            "forty four thousand one hundred sixty three"), '44163')
        self.assertEqual(text2num("one thousand thirty two"), "1032")
        self.assertEqual(text2num(
            """
            six hundred sixty two million eight hundred 
            twenty six thousand two hundred six
            """), "662826206")

    def testNumsWithHyphens(self):
        self.assertEqual(text2num("Twenty-three hundred sixty-one"), "2361")
        self.assertEqual(text2num("twenty-three hundred"), "2300")
        self.assertEqual(text2num("one-two"), "1-2")
        self.assertEqual(text2num("fifty-fifty"), "50-50")
        self.assertEqual(text2num(
            """
            six trillion one hundred and sixty-eight billion one hundred 
            seventy-three million three hundred eighteen thousand seven 
            hundred twenty-eight
            """), "6168173318728")

    def testNumsWithAnd(self):
        self.assertEqual(text2num("Two hundred and twenty one"), "221")
        self.assertEqual(text2num("one and two and three"), "1 and 2 and 3")
        self.assertEqual(text2num(
            """
            one hundred and twelve trillion three hundred and fourteen 
            billion one hundred and forty-eight million one hundred and 
            fifty-four thousand one hundred and nine
            """), "112314148154109")
        
    def testNumsInText(self):
        self.assertEqual(text2num(
            "Fifty-six bottles of pop on the wall, fifty-six bottles of pop"),
            "56 bottles of pop on the wall, 56 bottles of pop")
        self.assertEqual(text2num(
            "forty-three people were injured"), "43 people were injured")
        self.assertEqual(text2num(
            "Twenty-seven of them were hospitalized in Hong-Kong!"),
            "27 of them were hospitalized in Hong-Kong!")
        self.assertEqual(text2num(
            "He had only sixty cents."), "He had only 60 cents.")

    def testGroupByType(self):
        self.assertEqual(group_by_type([1, 2, 'a', 4, 'b', 'v', 6, 2]),
                         [ [1, 2], ['a'], [4], ['b', 'v'], [6, 2] ])
        self.assertEqual(group_by_type([]), [ [] ])
        self.assertEqual(group_by_type([1, 2, 3]), [ [1, 2, 3] ])
        self.assertEqual(group_by_type(['a', 'b', 'c']), [ ['a', 'b', 'c'] ])
        self.assertEqual(group_by_type(['1', '2', 3, 4, '5', 6]),
                         [ ['1', '2'], [3, 4], ['5'], [6] ])

if __name__ == "__main__":
    unittest.main()
