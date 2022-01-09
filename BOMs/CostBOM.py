""" PCBWay.py
# Copyright (c) 2022, Towechlabs
# All rights reserved
#
# Code used to create a BOM with the format for PCBWay's SMT Assmebly
"""

import kicad_netlist_reader
import csv
import sys
import os
import math

def calculateLots(minimum, multiples, boards, qty):
  return math.ceil( float((qty*boards) - minimum) / multiples) + 1

net = kicad_netlist_reader.netlist(sys.argv[1])
outputPath = sys.argv[2] + '.csv'

try:
  if os.path.exists(outputPath):
    os.remove(outputPath); 
  f = open(outputPath, 'w')
except IOError:
  e = "Can't open output fule for writing: " + sys.argv[2]
  print(__file__, ":", e, sys.stderr)
  f = sys.stdout

# Generates the csv file
out = csv.writer(f, lineterminator='\n', delimiter=',', quotechar='\"', quoting=csv.QUOTE_ALL)

# Outputs the header row
out.writerow([
  'Item #',
  'Designator',
  'Value',
  'Description',
  'Package',
  'Type',
  'LCSC-Part',
  'Qty',
  'Lots (1brd)',
  'Lots (2brd)',
  'Lots (3brd)',
  'Lots (4brd)',
  'Lots (5brd)',
  'Total (1brd)',
  'Total (2brd)',
  'Total (3brd)',
  'Total (4brd)',
  'Total (5brd)',
  'Link',
])

# Gets all of the components in groups of matching parts + values
grouped = net.groupComponents()

i = 0
totals = [0,0,0,0,0]

# Outputs all the component information
for group in grouped:
  itemNumbers = [];

  # Extracts the numbers of each component of a group and the prefix for it, it also keeps
  # the last component of the group
  for component in group:
    itemNumbers.append(int(''.join([numb for numb in component.getRef() if numb.isdigit()])))

    prefix = ''.join([p for p in component.getRef() if not p.isdigit()])
    c = component

  # if a component shouldn't be fitted, it gets skipped
  if (c.getField("Population").upper() == "DNP" or c.getField("Population").upper() == "DNF"):
    continue
  i += 1

  # Sorts the array and creates ranges for the descriptors
  itemNumbers.sort()

  # sets the first item
  refs = prefix + str(itemNumbers[0])
  
  previousNumber = itemNumbers[0]
  chaining = False
  for element in itemNumbers:
    #skips the first element
    if element == itemNumbers[0]:
      continue

    # If the number is exactly one more than the previous, then a chain is being created
    if element == previousNumber + 1:
      chaining = True
    # If not, the chain is finished, and then end of the chain is written, and the new element is added
    else:
      if chaining == True:
        chaining = False
        refs += ('-' + prefix + str(previousNumber))

      refs += (', ' + prefix + str(element))
    
    # If the current element is the last one of a chain, then it gets appended
    if (element == itemNumbers[-1] and chaining == True):
      refs += ('-' + prefix + str(element))

    previousNumber = element

  minimumAmount = 1 if c.getField("Minimum") == '' else int(c.getField("Minimum"))
  multiples = 1 if c.getField("Multiples") == '' else int(c.getField("Multiples"))
  price = 0 if c.getField("ExtPrice") == '' else float(c.getField("ExtPrice"))
  qty = len(group)

  # Calculates the totals for the amount of boards and appends them
  lots = [0,0,0,0,0]
  subtotals = [0,0,0,0,0]
  for j in range(5):
    lots[j] = calculateLots(minimumAmount, multiples, j+1, qty)
    subtotals[j] = lots[j] * price
    totals[j] += subtotals[j]


  

  # prints the row
  out.writerow([
    i,
    refs,
    c.getValue(),
    '',
    c.getField("Package"),
    c.getField("Type"),
    c.getField("LCSC"),
    qty,
    lots[0],
    lots[1],
    lots[2],
    lots[3],
    lots[4],
    subtotals[0],
    subtotals[1],
    subtotals[2],
    subtotals[3],
    subtotals[4],
    c.getField("Link"),
  ])

# Writes the totals row
out.writerow([
  '','','','','','','','','','','','',
  'Total',
  totals[0],
  totals[1],
  totals[2],
  totals[3],
  totals[4],
])

# Writes the price per board
out.writerow([
  '','','','','','','','','','','','',
  'Total per board',
  totals[0],
  totals[1] / 2,
  totals[2] / 3,
  totals[3] / 4,
  totals[4] / 5,
])
