'''
@author Xie Li
'''
import numpy as np
from z3 import *
import os

'''-----------------functions for conjunct to get new L-----------------'''
def coefDotExpr(x, coef, NumOfVars):
    result = 0
    for i in range(NumOfVars):
        result += coef[i]*x[i]
    result += coef[-1]
    return result

def coefDotExprZ3Constraint(x, coef, NumOfVars, divideConstant, isReal):
    if(isReal):
        result = RealVal(0)
        for i in range(NumOfVars):
            CoefTemp = RealVal(coef[i])
            result = Sum(result, Product(CoefTemp, x[i]))
        result = Sum(result, RealVal(coef[-1]))
        print("-----DOT RESULT: ", result)
        #print(type(result))
        return result < divideConstant

def coefDotExprZ3Arithmetic(x, coef, NumOfVars, isReal):
    if(isReal):
        result = RealVal(0)
        for i in range(NumOfVars):
            CoefTemp = RealVal(coef[i])
            result = Sum(result, Product(CoefTemp, x[i]))
        result = Sum(result, RealVal(coef[-1]))
        #print(result)
        #print(type(result))
        return result
'''
def heuristicImplicationConstraint(list_of_old_expr, new_expr, isReal):
    if(isReal):
        result = True
        for old_expr in list_of_old_expr:
            result = And(True, Implies(old_expr > 0, new_expr > 0))
        return result
'''

def ConjunctRankConstraintL(L_old, rf, isReal=True):
    # conjunct the ranking function constrain f <= 0 with the loop guard in L_old
    # to obtain a new loop L_new

    L_new = []
    # find new loop guard
    old_loopGuard = L_old[0]
    NumOfVars = L_old[2]
    coef = rf.coefficients
    addedExp = lambda x: coefDotExpr(x, coef, NumOfVars)
    divideConstant = 0
    minPoint = [0,0]
    for point in rf.sample_points_list:
        if addedExp(point) < divideConstant:
            divideConstant = addedExp(point)
            minPoint = point
    print("---------DIVIDE CONSTANT:", divideConstant)
    rf.coefficients[-1] += -divideConstant
    appendConstraint = lambda x : addedExp(x) < divideConstant
    newLoopGuard = lambda x: old_loopGuard(x) and appendConstraint(x)
    #L_new[0]
    L_new.append(newLoopGuard)

    #L_new[1]
    # find new update of the variables
    old_update = L_old[1]
    # the latter part will not happen for the loop guard is updated TODO: check
    new_update = lambda x: old_update(x) if appendConstraint(x) else [x[0], x[1]]
    L_new.append(new_update)
    
    #L_new[2]
    # num of var
    L_new.append(L_old[2])
    #L_new[3]
    # num of phases
    L_new.append(L_old[3])
    #L_new[4]
    # template
    L_new.append(L_old[4])



    
    #L_new[5]
    # z3 update
    L_new.append(lambda x: [If(coefDotExprZ3Constraint(x, coef, NumOfVars, divideConstant, isReal), L_old[5](x)[i], x[i]) for i in range(NumOfVars)])
   
    #L_new.append(L_old[5])
    #L_new[6]
    # z3 loop guard
    L_new.append(lambda x: And(coefDotExprZ3Constraint(x, coef, NumOfVars, divideConstant, isReal), L_old[6](x)))
    return L_new
'''-------------------------functions for generating templates lib---------------------------'''
def changeTemplate(L, template):
    L[4] = template

def generateTemplateLib(numOfVar, maxPower=1):
    # numOfvar represents the maximum diemension of a function
    # maxPower represents the maximum power of a variable, default 1 meaning linear functions
    # for linear template the function will finally generate a list of templates of num 2^varnum
    listOfUxVectors = []
    for i in range(numOfVar):
        UxTemplate = []
        for j in range(numOfVar):
            UxTemplate.append(0)
        UxTemplate.append(1)
        UxTemplate[i] = 1
        listOfUxVectors.append(UxTemplate)
    UxTemplate = []
    for j in range(numOfVar):
        UxTemplate.append(0)
    UxTemplate.append(1)
    listOfUxVectors.append(UxTemplate)
    UxTemplate = []
    for k in range(numOfVar+1):
        UxTemplate.append(0)
    listOfUxVectors.append(UxTemplate)
    print(listOfUxVectors)


def isUselessRankingFunction(rf):
    for c in rf.coefficients:
        if(c != 0):
            return False
    return True

    
'''--------------------Attributes for testing-------------------'''

TemplatesListTest = [
    [[1,0,1],
     [0,1,1],
     [0,0,1]]
]
''',
    [[1,0,1],
     [0,0,0],
     [0,0,1]],
    [[0,0,0],
     [0,1,1],
     [0,0,1]]
'''

TemplatesListExp = [
    
    [[1,0,-1],
     [0,1,-1],
     [0,0,-1]],
    [[1,0,-1],
     [0,0,0],
     [0,0,-1]],
    [[0,0,0],
     [0,1,-1],
     [0,0,-1]]

]


'''--------------------Print methods-------------------------'''
def printSummary(multidepth, ret, listOfRFs):
    print("--------------------LEARNING MULTIPHASE SUMMARY-------------------")
    print("MULTIPHASE DEPTH: ", multidepth)
    print("LEARNING RESULT: ", ret)
    print("-----------RANKING FUNCTIONS----------")
    for rf in listOfRFs:
        print(str(rf))
    
