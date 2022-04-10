import re
import json
from typing import Dict, List, Tuple

# label example
# "D676.53\nD321D4"

def char_ord(c) -> int:
    """define unicode character order: letters < digits < '-' < otherwise"""
    unicode_ord = ord(c)
    # letters has uppermost priority
    if ord('A') <= unicode_ord <= ord('Z'):
        return unicode_ord - ord('A')
    # then '-'
    elif unicode_ord == ord('-'):
        return 100
    # then digits
    elif ord('0') <= unicode_ord <= ord('9'):
        return unicode_ord - ord('0') + 200
    else:
        print("Unrecognized Char: {}".format(c))
        return 300


def compare_segment(s1: str, s2: str) -> int:
    """compare two string using character order defined in char_ord"""
    # char-wise compare
    for c1, c2 in zip(s1, s2):
        o1, o2 = char_ord(c1), char_ord(c2)
        if o1 < o2:
            return -1
        elif o1 > o2:
            return 1
        else:
            continue
    
    # if one string is prefix of another, shorter one has greater priority
    if len(s1) < len(s2):
        return -1
    elif len(s1) > len(s2):
        return 1
    else:
        return 0


def compare_split_label(lb1: List[str], lb2: List[str]) -> bool:
    """compare two list of string segments"""
    for seg1, seg2 in zip(lb1, lb2):
        seg_cmp_res = compare_segment(seg1, seg2)
        if seg_cmp_res != 0:
            return seg_cmp_res
    
    if len(lb1) < len(lb2):
        return -1
    elif len(lb2) > len(lb2):
        return 1
    else:
        return 0
        
def split_label(label: str) -> List[str]:
    """split book label by '\n' and '.'"""
    parsed_lb = re.split("\n|\.", label)
    return parsed_lb


def compare_label(lb1: str, lb2: str) -> int:
    """compare two book labels"""
    split_lb1, split_lb2 = split_label(lb1), split_label(lb2)
    return compare_split_label(split_lb1, split_lb2)

     
def order_judge(labels: List[str]) -> list:
    """judge if a list of label is in right order"""
    for i in range(len(labels) - 1):
        if compare_label(labels[i], labels[i+1]) == 1:
            return False
    return True

# usage
if __name__ == "__main__":
    lb1 = "D676.53\nD321D5"
    lb2 = "D676.53\nF472"
    print(compare_label(lb1, lb2))