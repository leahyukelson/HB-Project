""" Helper functions to sort """

import datetime

def mergesort_plans_by_date(plans):
    """ Helper function to mergesort lists of plans by their event time dates """
    
    # Split list in half - right side and left side, unless list is split to a single plan or is empty
    # If list is one plan or empty, return that plan
    if len(plans) == 0 or len(plans) == 1:
        return plans
    else:
        mid = len(plans)//2
        left = plans[:mid]
        right = plans[mid:]

        # Keep splitting and sorting lists recursively 
        left = mergesort_plans_by_date(left)
        right = mergesort_plans_by_date(right)

        # Merge the sorted left side with the sorted right side
        return merge_plans(left, right)


def merge_plans(a, b):
    """ Helper function for mergesort - merges two lists based on event time of plans 

    Returns a merged sorted list with the soonest plan first
    """
    
    # Create third empty list
    c = []

    # Loop through lists a and b until either list is empty
    # Add soonest plan to third list, remove from original list
    while len(a) != 0 and len(b) != 0:
        if a[0].event_time.date() < b[0].event_time.date():
            c.append(a[0])
            a.remove(a[0])
        else:
            c.append(b[0])
            b.remove(b[0])

    # Add elements from not empty list if the other list empties first
    if len(a) == 0:
        c += b
    else:
        c += a

    return c