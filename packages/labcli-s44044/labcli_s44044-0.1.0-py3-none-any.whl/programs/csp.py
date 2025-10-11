import random

colors = ['Red','Green','Blue']
neighbors = {'A':['B','C'], 'B':['A','C','D'], 'C':['A','B','D'], 'D':['B','C']}

def valid(assignment):
    for region in neighbors:
        for n in neighbors[region]:
            if region in assignment and n in assignment and assignment[region]==assignment[n]:
                return False
    return True

def csp(assignment={}):
    if len(assignment) == len(neighbors):
        return assignment
    var = [v for v in neighbors if v not in assignment][0]
    for color in colors:
        assignment[var] = color
        if valid(assignment):
            result = csp(assignment)
            if result: return result
        assignment.pop(var)
    return None

if __name__ == '__main__':
    print('CSP solution:', csp())
