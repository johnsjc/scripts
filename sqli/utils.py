def binary_search_with_predicate(bounds, predicate_fn, *args):
    # Binary search using a predicate function. 
    # Returns the index corresponding to the first element
    # in the ordered list for which the predicate function is True
    # and how many iterations it took to find the index.

    low_index, high_index = bounds
    iterations = 0

    while low_index < high_index:
        mid_index = int(low_index + (high_index - low_index) / 2)
        if predicate_fn(mid_index, *args):
            high_index = mid_index
        else:
            low_index = mid_index + 1
        
        iterations += 1

    if not predicate_fn(low_index, *args):
        # Something went wrong.
        print("Warning: Predicate is False for all elements!")
    
    return low_index, iterations
