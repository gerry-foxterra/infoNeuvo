#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      gerry
#
# Created:     22/11/2018
# Copyright:   (c) gerry 2018
# Licence:     <your licence>
#-------------------------------------------------------------------------------

def main():
  a = [{'Bob':{'id':1, 'type':'person'}}, \
       {'Mary':{'id':2, 'type':'person'}} \
      ]
  for b in a:
    for c in b:
      print c, b[c], b[c]['id']

if __name__ == '__main__':
    main()
