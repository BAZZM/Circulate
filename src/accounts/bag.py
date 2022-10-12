import sys

# import numpy as np
# import pandas as pd
# from sklearn import ...

for line in sys.stdin:
    # Finding number of digits
    num = int(line)
    tempN = int(line)
    order = len(str(tempN))
    sumN = 0
    while tempN > 0:
        individualNum = tempN % 10
        sumN += individualNum ** order

        tempN //= 10

    if num == sumN:
        print(True)
    else:
        print(False)