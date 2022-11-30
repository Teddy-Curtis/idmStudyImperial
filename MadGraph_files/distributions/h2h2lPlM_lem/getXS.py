# This reads the cross_sections.txt files to get a neat list 
# of the widths
for num in range(1, 22):
    with open(f'BP{num}/h2h2lPlM_lem_BP{num}/cross_section.txt') as f:
        for i, line in enumerate(f):
            if i==1:
                lines = line.split(' ')
                print(f'BP{num}, width = {lines[2]}')


