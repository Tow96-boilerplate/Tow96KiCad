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
  'Qty',
  'Manufacturer',
  'Mfg Part #',
  'Description/Value',
  'Package/Footprint',
  'Type',
  'LCSC-Part',
  'Your Instructions/Notes'
])

# Gets all of the components in groups of matching parts + values
grouped = net.groupComponents()

i = 0
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

  # prints the row
  out.writerow([
    i,
    refs,
    len(group),
    c.getField("Manufacturer"),
    c.getField("MfgPart"),
    c.getField("Description"),
    c.getField("Package"),
    c.getField("Type"),
    c.getField("LCSC"),
    c.getField("Note"),
  ])