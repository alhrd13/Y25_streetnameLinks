'''
Create new index from name and person data that was extracted from a wikidata dump

'''

import pickledb as p

people = p.load('all_new_names.db', False)
names = p.load('name_data.db', False)
label = p.load('all_new_labels.db', False)

index = p.load('new_index.db', False)

all = len(people.getall())

for t,i in enumerate(people.getall()):
    res = people.get(i)

    # First name
    if len(res[0]) == 0:
        label_name = label.get(i)
        if label_name != False:
            label_name = label_name.split()
            label_name.pop(-1)
            for l in label_name:
                check = index.get(l)
                if check == False:
                    index.set(l,[[i,'first']])
                else:
                    check.append([i,'first'])
                    index.set(l,check)
    for j in res[0]:
        first_name = names.get(j)
        if first_name != False:
            check = index.get(first_name[0])
            if check == False:
                index.set(first_name[0],[[i,'first']])
            else:
                check.append([i,'first'])
                index.set(first_name[0], check)

    # Last Name
    if len(res[1]) == 0:
        label_name = label.get(i)
        if label_name != False:
            label_name = label_name.split()
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
        if last_name != False:
            check = index.get(last_name[0])
            if check == False:
                index.set(last_name[0],[[i,'last']])
            else:
                check.append([i,'last'])
                index.set(last_name[0], check)

    # Alias
    for j in res[2]:
        check = index.get(j)
        if check == False:
            index.set(j, [[i,'alias']])
        else:
            check.append([i,'alias'])
            index.set(j, check)

    # Label
    res = label.get(i)
    if res != False:
        check = index.get(res)
        if check == False:
            index.set(res, [[i, 'full']])
        else:
            check.append([i, 'full'])
            index.set(res, check)

    print('{} von {}'.format(t,len(people.getall())))

index.dump()
