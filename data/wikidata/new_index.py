'''
Create new index from name and person data that was extracted from a wikidata dump

'''

import pickledb as p

#.................................
import os, sys
from IPython.core.ultratb import ColorTB
import yaml

sys.excepthook = ColorTB()

WKSPACE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PATH_CFG = './config.yml'

sys.path.append(WKSPACE)
PATH_CFG = os.path.join(WKSPACE, PATH_CFG)

with open(PATH_CFG, 'r') as file:
    PARAMS = yaml.safe_load(file)
#.................................

################################################################################
# USER PARAMETER
################################################################################

# Import
path_all_new_names = PARAMS['path']['db_all_new_names']
path_name_data = PARAMS['path']['db_name_data']             # Update with `new_names.py``
path_all_new_labels = PARAMS['path']['db_all_new_labels']

# Export
path_new_index = PARAMS['path']['db_new_index']


################################################################################
if __name__ == "__main__":

    # Import the databases

    path_all_new_names = os.path.join(
        WKSPACE, 
        path_all_new_names,
    )
    path_name_data = os.path.join(
        WKSPACE, 
        path_name_data,
    )
    path_all_new_labels = os.path.join(
        WKSPACE, 
        path_all_new_labels,
    )

    path_new_index = os.path.join(
        WKSPACE, 
        path_new_index,
    )

    print(f"--- Loading the databases ...", flush=True)
    people = p.load(path_all_new_names, False)
    names = p.load(path_name_data, False)
    label = p.load(path_all_new_labels, False)

    # Creation of a new database
    index = p.load(path_new_index, False)

    # all = len(people.getall())

    print(f"--- Starting to create the index ...", flush=True)
    for t,i in enumerate(people.getall()):
        # print("")
        # i: Q23 (= George Washington)
        # Finds all the people who have Washington as a root
        # The db people has already parsed the name
            # res = [['Q15921732'], ['Q2550388'], ['Vater der Vereinigten Staaten']]
            # Equivalent to ["George", "Washington", President ff the USA] -> male given name, family name, alias
        res = people.get(i)
        
        # print(f"--- i: {i}")
        # print(f"--- res: {res}")

        #.................................
        # First name
            # If no first name: checks if the only name is not a
            # composition of "last_name first_name". If it is the case, then
            # we only take the first name
        if len(res[0]) == 0:
            # label_name = label.get(i)
            label_name = label.get(i)[0]
            # print(f"--- label_name [first]: {label_name}")
            if label_name != False:
                label_name = label_name.split()

                # We can have label.get(i) = ['']
                if len(label_name) == 0:
                    label_name = [""]

                label_name.pop(-1)
                for l in label_name:
                    check = index.get(l)
                    if check == False:
                        index.set(l,[[i,'first']])
                    else:
                        check.append([i,'first'])
                        index.set(l,check)
        
            # For all the candidate-persons
        for j in res[0]:
            first_name = names.get(j)
            # print(f"--- first_name: {first_name}")
            if first_name != False:
                check = index.get(first_name[0])
                if check == False:
                    index.set(first_name[0],[[i,'first']])
                else:
                    check.append([i,'first'])
                    index.set(first_name[0], check)

        #.................................
        # Last Name
        if len(res[1]) == 0:
            # label_name = label.get(i)
            label_name = label.get(i)[0]
            # print(f"--- label_name [last]: {label_name}")
            if label_name != False:
                label_name = label_name.split()

                # We can have label.get(i) = ['']
                if len(label_name) == 0:
                    label_name = [""]
                
                check = index.get(label_name[-1])

                if check == False:
                    index.set(label_name[-1], [[i,'last']])
                else:
                    check.append([i,'last'])
                    index.set(label_name[-1], check)
                if '-' in label_name[-1]:
                    double = label_name[-1].split('-')
                    for d in double:
                        check = index.get(d)
                        if check == False:
                            index.set(d,[i,'last'])
                        else:
                            check.append([i,'last'])
                            index.set(d,check)
        for j in res[1]:
            last_name = names.get(j)
            # last_name = names.get(j)[0]
            # print(f"--- last name: {last_name}")
            if last_name != False:
                check = index.get(last_name[0])
                if check == False:
                    index.set(last_name[0],[[i,'last']])
                else:
                    check.append([i,'last'])
                    index.set(last_name[0], check)

        #.................................
        # Alias
        for j in res[2]:
            check = index.get(j)
            if check == False:
                index.set(j, [[i,'alias']])
            else:
                check.append([i,'alias'])
                index.set(j, check)

        #.................................
        # Label
        # res = label.get(i)
        res = label.get(i)[0]
        # print(f"--- label: {res}")
        # print('\u001b[44m{}\u001b[0m'.format(res))
        if res != False:
            check = index.get(res)
            # print(f"--- check_label_in_index: {check}")
            if check == False:
                index.set(res, [[i, 'full']])
            else:
                check.append([i, 'full'])
                index.set(res, check)

        if t % 100000 == 0 or t == len(people.getall()) - 1:
            print(f"{t} / {len(people.getall())}")

    #---------------------------------
    # Export
    index.dump()
