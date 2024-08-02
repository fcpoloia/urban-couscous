
# pylint: disable-msg=empty-docstring, line-too-long, missing-class-docstring, empty-docstring, missing-module-docstring

import random


def human_time(length):
    """take seconds input and return time in hours:mins:secs"""
    if length is None:
        return ""
    if length > 3600.0:
        hours = int(length/3600)
        mins = int((length-(hours*3600))/60)
        secs = int(length-(hours*3600)-(mins*60))
        return f"{hours}:{mins:02d}:{secs:02d}"
    if length > 60.0:
        mins = int(length/60)
        secs = int(length-(mins*60))
        return f"{mins}:{secs:02d}"
    return f"{int(length)}"


def random_selection(datalist, count):
    """"""
    if len(datalist) <= 1:
        return datalist

    selection = []
    nums = []

    while len(selection) < count and len(selection) < len(datalist):
        num = random.randrange(len(datalist))
        if num not in nums:
            nums.append(num)
            selection.append(datalist[num])
    return selection



