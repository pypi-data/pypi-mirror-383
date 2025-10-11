### pg_helpers/query_utils.py
"""Query preparation and cleaning utilities"""

def listPrep(iList):
    """
    Prepare a list for use in SQL queries by converting to comma-separated string
    
    Args:
        iList: List of integers, floats, or strings, or a single value
        
    Returns:
        str: Formatted string for SQL query
    """
    if type(iList) == list:
        if type(iList[0]) == int:
            iStr = ','.join(str(x) for x in iList)
        elif type(iList[0]) == float:
            iStr = ','.join(str(x) for x in iList)
        else:
            iStr = '\',\''.join(str(x) for x in iList)
            iStr = '\'' + iStr + '\''
    else:
        iStr = str(iList)
    
    return iStr

def queryCleaner(file, list1='empty', varString1='empty', list2='empty', 
                varString2='empty', startDate='START1', endDate='END1'):
    """
    Clean and prepare SQL query by replacing placeholders with actual values
    
    Args:
        file (str): Path to SQL file
        list1: First list to substitute
        varString1 (str): Placeholder string for first list
        list2: Second list to substitute  
        varString2 (str): Placeholder string for second list
        startDate: Start date value
        endDate: End date value
        
    Returns:
        str: Cleaned SQL query string
    """
    with open(file, 'r', encoding='utf-8') as myFile:
        query = myFile.read()
    
    if list1 != 'empty':
        list1IDs = listPrep(list1)
        query = query.replace(varString1, list1IDs)
    
    if list2 != 'empty':
        list2IDs = listPrep(list2)
        query = query.replace(varString2, list2IDs)
    
    if startDate != 'START1':
        if type(startDate) == str:
            startDate = f"'{startDate}'"
            endDate = f"'{endDate}'"
        
        query = query.replace('$START_DATE', str(startDate))
        query = query.replace('$END_DATE', str(endDate))
    
    return query
