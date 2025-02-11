import re

################################################################################

def get_candidates(
        query,
        prefix,
        suffix,
        # linx,
        index,
    ):

    #---------------------------------
    # Remove '-'
    query = query.replace('-', ' ').rstrip()

    # **********
    # Remove extras: streetname (extras)
    if query.endswith(')') == True:
        try:
            extra = re.findall('\(.*\)', query)
            query = query.replace(extra[0],'').rstrip()
        except:
            return False
        
    # **********
    # Remove initials
    initials = re.findall('[A-Z]\. ',query)
    for init in initials:
        query = query.replace(init,'').rstrip().lstrip()

    # **********
    # Remove suffix
    for s in suffix:
        if query.endswith(s) == True:
            query = query.replace(s,'').rstrip().lstrip()
            break
    
    # **********
    # Remove prefix
    for p in prefix:
        query = query.replace(p,'').rstrip().lstrip()

    # **********
    # Skip street if the query is empty after filtering
    if len(query) == 0:
        return False
    
    #---------------------------------
    # Popularity Ranking
    result = index.get(query)
    # Add a '-' if between the last two names if no result was returned
    if result == False:
        backspace = query.rfind(' ')
        if backspace > -1:
            query_list = list(query)
            query_list[backspace] = '-'
            query = ''.join(query_list)
            result = index.get(query)

    # **********
    # Remove the last 's' if there is still no result (e.g. 'Müllersweg')
    # If there are still no results after that, skip to this street
    if result == False:
        if query.endswith('s') == True:
            query_list = list(query)
            query_list = query_list[:-1]
            query = ''.join(query_list)
            if len(query) == 0:
                return False
            result = index.get(query)
            if result == False:
                return False
        else:
            return False

    return result

################################################################################

def get_hierarchy(
        start, 
        places,
    ):

    list_containment = []
    list_containment.append(start)
    item = None
    while item != False:
        # Example places: ('Q15321', [['Q656', 'Q270196']])
        item = places.get(start)

        if item != False:
            # print(f">>> start: {start}, item:{item}")
            # list_containment.append(item[2])
                # We choose the first item by default - at worse, the is a common node at a lower rank
            parent = item[0][0]
            list_containment.append(parent)
            # start = item[2]
            start = parent
            # try:
            #     # Example places: ('Q15321', [['Q656', 'Q270196']])
            #     item = places.get(start)
            #     print(f">>> start: {start}, item:{item}")
            #     # list_containment.append(item[2])
            #         # We choose the first item by default - at worse, the is a common node at a lower rank
            #     parent = item[0][0]
            #     list_containment.append(parent)
            #     # start = item[2]
            #     start = parent
            # except:
            #     break
    try:
        list_containment.remove('')
    except:
        pass
    return list_containment

################################################################################

def get_highest_relation_score(
        street_hier, 
        person_hier, 
        places,
    ):

    length = len(street_hier)
    max_score, current_val = 0, 0
    for j in person_hier:
        place_hier = get_hierarchy(j, places)
        for i in place_hier:
            if i in street_hier:
                current_val = (length-street_hier.index(i))/length
#                current_val = 3
                if current_val > max_score:
                    max_score = current_val
    return max_score


################################################################################

def get_candidate_relations(
        street, 
        candidate, 
        places, 
        person_places,
    ):

        # Initiating data
    rel = [0, 0, 0, 0, 0]
    place_list = person_places.get(candidate)
    if place_list == False:
        return rel
    #    street_hier = get_hierarchy(street, places)
    street_hier = street

    # Calculate relation score for birth place#
    rel[0] = get_highest_relation_score(street_hier, place_list[0], places)
    # Calculate relation score for death place
    rel[1] = get_highest_relation_score(street_hier, place_list[1], places)
    # Calculate relation score for burial place
    rel[2] = get_highest_relation_score(street_hier, place_list[2], places)
    # Calculate relation score for education place
    rel[3] = get_highest_relation_score(street_hier, place_list[3], places)
    # Calculate relation score for residence place
    rel[4] = get_highest_relation_score(street_hier, place_list[4], places)

    return rel

################################################################################

def get_occupations(
        candidate, 
        occDB,
    ):

    occ_data = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    occs = occDB.get(candidate)
    if occs == False:
        return occ_data

    for o in occs:
        # Politician
        if o == 'Q82955':
            occ_data[0] = 1
        # Writer
        if o == 'Q36180':
            occ_data[1] = 1
        # University teacher 
        if o == 'Q1622272':
            occ_data[2] = 1
        if o == 'Q49757':
            occ_data[3] = 1
        if o == 'Q4964182':
            occ_data[4] = 1
        if o == 'Q1028181':
            occ_data[5] = 1
        if o == 'Q1930187':
            occ_data[6] = 1
        if o == 'Q36834':
            occ_data[7] = 1
        if o == 'Q169470':
            occ_data[8] = 1
        if o == 'Q214917':
            occ_data[9] = 1
        if o == 'Q1234713':
            occ_data[10] = 1
        if o == 'Q6625963':
            occ_data[11] = 1
        if o == 'Q333634':
            occ_data[12] = 1
        if o == 'Q81096':
            occ_data[13] = 1
        if o == 'Q37226':
            occ_data[14] = 1
        if o == 'Q205375':
            occ_data[15] = 1
        if o == 'Q185351':
            occ_data[16] = 1
        if o == 'Q39631':
            occ_data[17] = 1
        if o == 'Q482980':
            occ_data[18] = 1
        if o == 'Q131524':
            occ_data[19] = 1

    return occ_data

################################################################################

def get_names(
        candidate,
    ):

    name_list = [0,0,0,0]

    if candidate[1] == 'full':
        name_list[0] = 1
    if candidate[1] == 'first':
        name_list[1] = 1
    if candidate[1] == 'last':
        name_list[2] = 1
    if candidate[1] == 'alias':
        name_list[3] = 1

    return name_list

################################################################################

def get_max_N(
        candidate_list, 
        links,
        N=50,
    ):

    candidate_dict = {}
    for c in candidate_list:
        count = 0
        try:
            count = int(links.loc[c[0]][1])
        except:
            pass
        candidate_dict[c[0]] = count

    sorted_list = sorted(candidate_dict.items(), key=lambda x: x[1])
    test = []
    for t,i in enumerate(sorted_list):
        if t == N:
            break
        test.append(i)
    return test

