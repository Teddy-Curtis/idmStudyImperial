# You input the name of the process this then loops over 
# each BP and finds the xs for each run
import sys
from optparse import OptionParser

def get_options():
  parser = OptionParser()
  parser.add_option('--process', dest='process', default='', help="This is the name of the process")
  return parser.parse_args()
(opt,args) = get_options()

process = str(opt.process)

for num in range(1, 22):
    with open(f'{process}/BP{num}/{process}_BP{num}/cross_section.txt') as f:
        for i, line in enumerate(f):
            if i==1:
                lines = line.split(' ')
                print(f'BP{num}, cross-section = {lines[2]}')


