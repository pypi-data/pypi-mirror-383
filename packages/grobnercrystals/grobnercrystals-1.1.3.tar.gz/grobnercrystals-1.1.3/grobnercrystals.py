#!/usr/bin/env sage
# imports
import sage.all # type: ignore
import operator
import numpy as np # type: ignore
import itertools as it
import copy
from collections import defaultdict

# useful shorthands for Sage functions
import sage.interfaces.macaulay2 as m2 # type: ignore
from sage.combinat.permutation import Permutation # type: ignore
from sage.combinat.rsk import RSK # type: ignore
from sage.symbolic.ring import SymbolicRing as SR # type: ignore
from sage.rings.polynomial.polynomial_ring_constructor import PolynomialRing # type: ignore
from sage.rings.rational_field import QQ # type: ignore
from sage.matrix.constructor import matrix # type: ignore
from sage.combinat.sf.sf import SymmetricFunctions # type: ignore
from sage.combinat.schubert_polynomial import SchubertPolynomialRing # type: ignore
from sage.combinat.tableau import SemistandardTableaux,SemistandardTableau,Tableau # type: ignore
from sage.rings.integer_ring import ZZ # type: ignore
from sage.combinat.combination import Combinations # type: ignore
from sage.combinat.partition import Partition # type: ignore

# requires macaulay2 gfanInterface package
m2.macaulay2("needsPackage \"gfanInterface\"") # type: ignore

'''
PERMUTATIONS
'''
# Creates a permutation; initialize with the permutation as a list and optionally
# an effective region, either input as [(a,b),(c,d),...] or as (maxRow,maxCol)
class Perm():
    """A class for permutations

    :param perm: The permutation in one-line notation as a list of integers
    :type perm: list
    :param region: The region the permutation should be restricted to, as a  
        list of tuples (i,j) with i,j in [0,length(perm)-1] (for working with 
        usual instead of effective matrix Schubert varieties)
    :type region: list, optional

    :ivar perm: the permutation in one-line notation as a list of integers
    :ivar l: int, length of the permutation
    :ivar region: parameter region if specified, else list of tuples (i,j) of integers between 0 and l-1
    :ivar descents: list of the descents of the permutation (as integers)
    :ivar inverse: inverse of the permutation in one-line notation as a list of integers
    :ivar inverse_descents: list of the descents of the inverse of the permutation (as integers)
    :ivar vexillary: bool, True if the permutation is vexillary, else False
    :ivar max_row: int, largest i such that (i,j) is in region
    :ivar max_col: int, largest j such that (i,j) is in region
    """

    def __init__(self,perm,region=None):
        """Constructor method
        """

        self.perm = perm
        self.region = region if type(region) is not tuple else [(i,j) for i in range(region[0]) for j in range(region[1])]
        self.l = len(perm)
        self.descents = Permutation(perm).descents()
        self.inverse = Permutation(self.perm).inverse()
        self.inverse_descents = self.inverse.descents()
        self.vexillary = Permutation(perm).avoids([2,1,4,3])
        (self.max_row,self.max_col) = self.max_dim()
           
    # Returns list [effective region, (maxRow,maxCol)]
    def eff_reg(self,retMaxDim=False):
        """Calculates the effective region of the permutation, i.e.
        the set of all tuples (i,j) so that (i,j) is weakly northwest of the
        southeast most box in the Rothe diagram for the permutation.

        :param retMaxDim: whether to return the largest row and column in the effective region, defaults to False
        :type retMaxDim: bool, optional
        """
        retVal = []

	    # Find all boxes in rothe diagram
	    # Add all entries NW of boxes to list
        boxes = []
        possibleBoxes = [i for i in range(self.l)]

        for i in range(self.l):
            permVal = self.perm[i]-1
            for j in possibleBoxes[:possibleBoxes.index(permVal)]:
                boxes.append((i,j))
            possibleBoxes.remove(permVal)


        for box in boxes:
            for k in range(box[0]+1):
                for l in range(box[1]+1):
                    if not (k,l) in retVal:
                        retVal.append((k,l))
        if retVal==[]:
            maxRow = -1
            maxCol = -1
        if not retVal==[]:
            maxRow =  max(retVal,key = operator.itemgetter(0))[0]
            maxCol =  max(retVal,key = operator.itemgetter(1))[1]

        #REMOVED: Code for finding if self.perm is dominant
        if retMaxDim:
            return [retVal,(maxRow,maxCol)]
        else:
            return retVal
    
    def eff_reg_complement(self):
        effReg = self.eff_reg()[0]
        fullRegion = [(i,j) for (i,j) in it.product(range(self.l),range(self.l))]
        effRegCmplmnt = [box for box in fullRegion if not box in effReg and not self.perm[box[0]]==box[1]+1]
        return effRegCmplmnt
    
    # Find (maxRow,maxCol)
    def max_dim(self):
        if all([self.perm[i]-i-1==0 for i in range(self.l)]):
            return (0,0)
        if not self.region==None:
            return (max(self.region,key = operator.itemgetter(0))[0],max(self.region,key = operator.itemgetter(1))[1])
        if self.region==None:
            effReg = self.eff_reg(retMaxDim=True)
            return effReg[1] 

    # Returns descents of self.perm as a list [[0,i_1,...,maxRow+1],[0,j_1,...,maxCol+1]]
    # The descent is between i_k and i_k - 1
    def levi_datum(self):
        """Finds the Levi datum corresponding to the largest Levi
        group which acts on the effective matrix Schubert variety 
        corresponding to the permutation. If a region is specified,
        returns the Levi datum corresponding to the largest Levi
        group which acts on the matrix Schubert variety when restricted
        to that region.

        :return: A Levi datum [I,J], where I,J are lists of integers
        :rtype: list
        """
        #(maxRow,maxCol) = self.max_dim()
        descentsW = [0] + [descent for descent in self.descents if descent <= self.max_row+1]
        if not descentsW[-1]==self.max_row+1:
            descentsW += [self.max_row+1]

        descentsWInv = [0] + [descent for descent in self.inverse_descents if descent <= self.max_col+1]
        if not descentsWInv[-1]==self.max_col+1:
            descentsWInv += [self.max_col+1]
        return [descentsW,descentsWInv]
    
    # returns lists of (0-indexed) rows and columns that are not separated by descents
    # example: [[[0,1],[2,3,4]],[[0],[1,2,3]]]
    def comparable_rows_cols(self):
        desc = self.levi_datum()
        dim = (self.max_row,self.max_col)
        retVal = [[],[]]
        curList = []
        for k in range(len(dim)):
            for i in range(dim[k]+1):
                curList.append(i)
                if i+1 in desc[k]:
                    retVal[k].append(curList)
                    curList = []
            if not curList==[]:
                retVal.append(curList)
        return retVal 
    
    # Input: permutation w
    # Output: [list of x groups, list of y groups] (as integers)
    def levi_group(self):
        descentsW = [0] + self.descents + [self.l]
        descentsWInv = [0] + self.inverse_descents + [self.l]

        if not self.max_row==0:
            diffLs = [descentsW[i+1] - descentsW[i] for i in range(len(descentsW)-1)]
            descentsW = [0]+[descentsW[i] for i in range(1,len(descentsW)) if sum(diffLs[0:i]) <= self.max_row+1]
            if not descentsW[len(descentsW)-1]==self.max_row+1:
                descentsW += [self.max_row+1]

        if not self.max_col==0:
            diffLs = [descentsWInv[i+1] - descentsWInv[i] for i in range(len(descentsWInv)-1)]
            descentsWInv = [0]+[descentsWInv[i] for i in range(1,len(descentsWInv)) if sum(diffLs[0:i]) <= self.max_col+1]
            if not descentsWInv[len(descentsWInv)-1]==self.max_col+1:
                descentsWInv += [self.max_col]

        groupLsX = []
        groupLsY = []
        for i in range(len(descentsW)-1):
            groupLsX.append(descentsW[i+1] - descentsW[i])

        for i in range(len(descentsWInv)-1):
            groupLsY.append(descentsWInv[i+1] - descentsWInv[i])

        return [groupLsX,groupLsY]

    def is_dominant(self):
        def FindDominantPiece(rothe):
            retVal = []
            rotheCopy = rothe
            FindNextBoxes((0,0),rotheCopy,retVal)
            return retVal
        
        def FindNextBoxes(box,rothe,counter):
            if box in rothe:
                if box not in counter:
                    counter.append(box)
                    FindNextBoxes((box[0]+1,box[1]),rothe,counter)
                    FindNextBoxes((box[0],box[1]+1),rothe,counter)
            else:
                return counter
        
        retVal = []

        # Find all boxes in rothe diagram
        # Add all entries NW of boxes to list
        l = len(self.perm)
        boxes = []
        possibleBoxes = [i for i in range(l)]

        for i in range(l):
            permVal = self.perm[i]-1
            for j in possibleBoxes[:possibleBoxes.index(permVal)]:
                boxes.append((i,j))
            possibleBoxes.remove(permVal)


        for box in boxes:
            for k in range(box[0]+1):
                for l in range(box[1]+1):
                    if not (k,l) in retVal:
                        retVal.append((k,l))

        dominant = FindDominantPiece(boxes)

        isDominant = [elt for elt in retVal]
        for elt in dominant:
            isDominant.remove(elt)
		    
        if isDominant==[]:
            return True
        return False

    def ess_set(self):
        """Finds Fulton's essential set.

        :return: Fulton's essential set as a list of indices [(i,j)]
        :rtype: list
        """

        def FindBoxes(effReg,dots):
            retVal = []
            for box in effReg:
                trueVec = []
                for dot in dots:
                    if not box in retVal:
                        if (box[0]==dot[0] and box[1] >= dot[1]) or (box[1]==dot[1] and box[0] >= dot[0]):
                            trueVec.append(False)
                        else: 
                            trueVec.append(True)
                if all(trueVec):
                    retVal.append(box)
            return retVal
        
        def DivideIntoConnectedComponents(boxes):
            retVal = []
            for box in boxes:
                trueVec = []
                for elt in retVal:
                    if not box in elt:
                        trueVec.append(True)
                    else:
                        trueVec.append(False)
                if all(trueVec) or trueVec==[]:
                    retVal.append(FindConnectedComponent([box],boxes))
            return retVal
        
        # Takes in a box and finds its connected component
        def FindConnectedComponent(currentCmpnt,remainingBoxes):
            cmpntCopy = [elt for elt in currentCmpnt]
            for box in currentCmpnt:
                rowBox = (box[0]+1,box[1])
                colBox = (box[0],box[1]+1)
                if rowBox in remainingBoxes:
                    cmpntCopy.append(rowBox)
                    remainingBoxes.remove(rowBox)
                if colBox in remainingBoxes:
                    cmpntCopy.append(colBox)
                    remainingBoxes.remove(colBox)
            if cmpntCopy==currentCmpnt:
                return currentCmpnt
            else:
                return FindConnectedComponent(cmpntCopy,remainingBoxes)

        retVal = []
        dots = [(i,self.perm[i]-1) for i in range(self.max_row+1) if not self.perm[i] > self.max_col]
        boxes = FindBoxes(self.eff_reg(),dots)
        components = DivideIntoConnectedComponents(boxes)
        for elt in components:
            for box in elt:
                if ((box[0],box[1]+1) not in elt) and ((box[0]+1,box[1]) not in elt):
                    retVal.append(box)
        return retVal
    
    # returns [[(essential set box), number in that box]]
    def filled_ess_set(self):
        """Finds Fulton's essential set, together with the rank conditions imposed by 
        each box in the essential set.

        :return: A list [[essential set box, number in that box]]
        :rtype: list
        """
        
        essSet = self.ess_set()
        dots = [(i,self.perm[i]-1) for i in range(self.max_row+1) if not self.perm[i] > self.max_col]
        retVal = []
        for box in essSet:
            boxFill = 0
            for dot in dots:
                if dot[0] <= box[0] and dot[1] <= box[1]:
                    boxFill += 1
            retVal.append([box,boxFill])
        return retVal

'''
(FILTERED) RSK AND BICRYSTAL OPERATORS
'''
# Input: matrix (numpy array or matrix), i, row/col (0 for row, 1 for column)
# Output: row/column word for rows/cols i,i+1 of that matrix
# word - 0 for ), 1 for (
def par_word(M,i,rc):
    if rc==0:
        ar = M[[i-1,i],:]
        retVal = []
        retValDec = []
        for k in range(M.shape[1]):
            if not ar[0,k]==0:
                retVal += [0]*ar[0,k]
                retValDec += [[(i-1,k),0]]*ar[0,k]
            if not ar[1,k]==0:
                retVal += [1]*ar[1,k]
                retValDec += [[(i,k),1]]*ar[1,k]
        return [retVal,retValDec]

    if rc==1:
        ar = M[:,[i-1,i]]
        retVal = []
        retValDec = []
        for k in range(M.shape[0]):
            if not ar[k,0]==0:
                retVal += [0]*ar[k,0]
                retValDec += [[(k,i-1),0]]*ar[k,0]
            if not ar[k,1]==0:
                retVal += [1]*ar[k,1]
                retValDec += [[(k,i),1]]*ar[k,1]
        return [retVal,retValDec]
    
# Input: word of 0s and 1s
# Output: sequence of Trues and Falses - True if parenthesis is matched, False otherwise
def matched(word):
    iterWord = [[word[i],i] for i in range(len(word))]
    retVal = [False for elt in word]

    def helper(cur):
        if cur==[]:
            return
        
        # trim tails of 0s and 1s
        removeLs = []
        for i in range(len(cur)):
            if cur[i][0]==1:
                break
            removeLs.append(i)

        if not removeLs==[]:
            cur = cur[max(removeLs)+1:]

        removeLs = []
        for j in range(len(cur)):
            if cur[-j-1][0]==0:
                break
            removeLs.append(len(cur)-j-1)

        if not removeLs==[]:
            cur = cur[:min(removeLs)]

        if cur==[]:
            return
        
        # find last of the first occurrences of 1
        ix = 0
        for i in range(len(cur)-1):
            if cur[i+1][0]==0:
                ix = i+1
                break

        retVal[cur[ix-1][1]]=True
        retVal[cur[ix][1]]=True
        cur = cur[:ix-1] + cur[ix+1:]

        helper(cur)

    helper(iterWord)
    return retVal

# input: a numpy matrix, integer i, and rc (0 if row, 1 if column), outputs matrix raising op applied to that M
# Can also input rc='r' or rc='c'
def e(M,i,rc):
    """Raising matrix crystal operator.

    :param M: Matrix to apply the operator to
    :type M: numpy matrix
    :param i: row or column index
    :type i: int
    :param rc: 'r' or 0 if row operator, 'c' or 1 if column operator
    :type rc: str or int
    :return: Result of applying raising crystal operator to M if possible. 
        If the result of applying the operator to M is the empty symbol, return None.
    :rtype: numpy matrix or None
    """

    if rc=='r':
        rc = 0
    if rc=='c':
        rc = 1
    # Find the parenthesis sequence for M, row/column i (indexed from 1)
    parSeq = par_word(M,i,rc)
    retVal = copy.deepcopy(M)
    # Find the matched parenthesis sequence
    matchSeq = matched(parSeq[0])
    # Flip the leftmost unmatched ( (i.e. 1) to a ) (i.e. 0)
    for k in range(len(parSeq[0])):
        if parSeq[0][k]==1 and not matchSeq[k]:
            if rc==0:
                retVal[parSeq[1][k][0][0],parSeq[1][k][0][1]] -= 1
                retVal[parSeq[1][k][0][0]-1,parSeq[1][k][0][1]] += 1
            if rc==1:
                retVal[parSeq[1][k][0][0],parSeq[1][k][0][1]] -= 1
                retVal[parSeq[1][k][0][0],parSeq[1][k][0][1]-1] += 1
            return retVal
    return None

# Takes as input a numpy matrix, integer i, and rc (0 if row, 1 if column), outputs matrix lowering op applied to that M
# Can also input rc='r' or rc='c'
def f(M,i,rc):
    """Lowering matrix crystal operator.

    :param M: Matrix to apply the operator to
    :type M: numpy matrix
    :param i: row or column index
    :type i: int
    :param rc: 'r' or 0 if row operator, 'c' or 1 if column operator
    :type rc: str or int
    :return: Result of applying lowering crystal operator to M if possible. 
        If the result of applying the operator to M is the empty symbol, return None.
    :rtype: numpy matrix or None
    """

    if rc=='r':
        rc = 0
    if rc=='c':
        rc = 1
    parSeq = par_word(M,i,rc)
    retVal = copy.deepcopy(M)
    # Find the matched parenthesis sequence
    matchSeq = matched(parSeq[0])
    # Flip the rightmost unmatched ) (i.e. 0) to a ( (i.e. 1)
    n = len(parSeq[0])
    for k in range(n):
        if parSeq[0][n-k-1]==0 and not matchSeq[n-k-1]:
            if rc==0:
                retVal[parSeq[1][n-k-1][0][0],parSeq[1][n-k-1][0][1]] -= 1
                retVal[parSeq[1][n-k-1][0][0]+1,parSeq[1][n-k-1][0][1]] += 1
            if rc==1:
                retVal[parSeq[1][n-k-1][0][0],parSeq[1][n-k-1][0][1]] -= 1
                retVal[parSeq[1][n-k-1][0][0],parSeq[1][n-k-1][0][1]+1] += 1
            return retVal
    return None

# input: numpy matrix M, rc (0 if row, 1 if column)
# output: row or column word of M
def word(M,rc):
    """Reading word of a matrix M. This function outputs either the row or 
    column reading word of M, depending on the input rc.

    :param M: Non-negative integer matrix
    :type M: numpy matrix
    :param rc: 'r' or 0 if row operator, 'c' or 1 if column operator
    :type rc: str or int
    :return: Either the row or column reading word of M
    :rtype: list
    """

    if rc=='r':
        rc==0
    if rc=='c':
        rc==1
    if rc==1:
        M = M.transpose()
    word = []
    for j in range(M.shape[1]):
        for i in range(M.shape[0]):
            word += [i]*M[i,j]
    return word

# input: numpy matrix M, rc (0 if row, 1 if column), I (Levi datum)
# output: row or column word of M
def filtered_word(M,rc,I):
    """Computes the filtered (row/column) reading word of M with respect
    to some Levi datum.

    :param M: Non-negative integer matrix
    :type M: numpy matrix
    :param rc: 'r' or 0 if row operator, 'c' or 1 if column operator
    :type rc: str or int
    :param I: Row/column Levi datum
    :type I: list
    :return: list of words, one for each GL-component of the Levi group
    :rtype: list
    """

    if rc=='r':
        rc = 0
    if rc=='c':
        rc = 1

    a = datum_to_alphabet(I)
    a = [a[0]]+[a[i]+sum(a[:i]) for i in range(1,len(a))]

    if rc==1:
        M = M.transpose()

    word = [[] for elt in a]
    a = [0] + a
    alphabets = [range(a[i-1],a[i]) for i in range(1,len(a))]

    for b in range(len(alphabets)):
        for j in range(M.shape[1]):
            for i in alphabets[b]:
                word[b] += [i+1]*M[i,j]
    return word

# Input: np matrix, I, J (Levi data)
# Output: filteredRSK(M) as a tuple of tableaux
def filtered_RSK(M,I,J):
    """Returns the result of applying filteredRSK to a matrix for a given Levi datum.

    :param M: The matrix to be filterRSK'd
    :type M: numpy matrix
    :param I: The row Levi datum
    :type I: list
    :param J: The column Levi datum
    :type J: list
    :return: A list of tableau [[row tableaux],[column tableaux]]
    :rtype: list
    """

    row_words = filtered_word(M,0,I)
    col_words = filtered_word(M,1,J)

    rowRSK = [RSK(row_word)[0] for row_word in row_words] 
    colRSK = [RSK(col_word)[0] for col_word in col_words] 
    
    return [rowRSK,colRSK]

# input: Levi datum
# output: list of alphabet sizes
def datum_to_alphabet(I):
    ret_val = []
    for i in range(1,len(I)):
        ret_val.append(I[i]-I[i-1])
    return ret_val

'''
VARIABLE HANDLING
'''
# Generate the necessary variables
class VariableGenerator(object): 
     def __init__(self, prefix, undScore=False): 
         self.__prefix = prefix 
         self.__undscore = undScore

     def __getitem__(self, key): 
        if not self.__undscore:
            return SR.var("%s%s"%(self.__prefix,key))
        if self.__undscore:
            return SR.var("%s_%s"%(self.__prefix,key))
        
# Return list of m*n variables
def var_gen(m,n,name='z'):
    gens = []
    for i in range(m):
        for j in range(n):
            cur = name+str(i+1)+str(j+1)
            gens.append(cur)
    return gens

'''
M2 RING CONSTRUCTORS
'''
def m2_ungraded_ring_str(varsC,to):
    mStr = 'QQ['
    for i in range(len(varsC)-1):
        mStr += varsC[i]+','
    mStr += varsC[-1] + ', MonomialOrder=>'+to+']'
    return mStr

def m2_graded_ring_str(m,n,varsC,to):
    weights = []
    for i in range(m):
        for j in range(n):
            cur_weight = [0]*(m+n)
            cur_weight[i] = 1
            cur_weight[m+j] = 1
            weights.append(cur_weight)
    weightStr = '{'
    for weight in weights:
        cur_str = '{'
        for i in range(len(weight)-1):
            cur_str += str(weight[i]) + ','
        cur_str += str(weight[-1])+'},'
        weightStr += cur_str
    weightStr = weightStr[:len(weightStr)-1] + '}'

    mStr = 'QQ['
    for i in range(len(varsC)-1):
        mStr += varsC[i]+','
    mStr += varsC[-1] + ', Degrees=>'+weightStr+',MonomialOrder=>'+to+']'
    return mStr

'''
M2 OUTPUT TO SAGE OBJECT CONVERSIONS
'''
# Input: string of a polynomial output from M2, lists of X and Y variables
# Assumes that m2 pol has variables T_0,...,T_k
# Ouput: string of a polynomial that can be used with eval() in Sage
def M2_to_Sage(pol,XY):
    pol=pol.replace('^','**')
    for i in reversed(range(len(XY))):
        pol=pol.replace('T_'+str(i),'XY['+str(i)+']')

    try: 
        return eval(pol)
    except RecursionError:
        pol_ls = pol.split('+')
        retVal = 0
        for elt in pol_ls:
            retVal += eval(elt)
        return retVal

# input: string 'zij*zkl*...*zmn'
# only works for monomials in zij, i,j <= 9
def M2_mon_to_Sage(mon,Z):
    # check for coefficients that are not 1
    coeff = 1
    if mon[0] != 'z':
        coeff = eval(mon[:mon.find('*')])
        mon = mon[mon.find('*')+1:]
    z_split = mon.split('z')
    z_split = [elt.replace('*','') for elt in z_split if not elt=='']
    z_split = [elt.split('^') if '^' in elt else [elt,'1'] for elt in z_split]
    ret_mon = 1
    for elt in z_split:
        ret_mon *= Z[int(elt[0][0])-1,int(elt[0][1])-1]**int(elt[1])
    return coeff*ret_mon

# input: monomial
# output: monomial as a matrix (ignoring coefficients!)
def sage_mon_to_mat(mon,m,n):
    d = mon.dict()
    elt_mat = np.array([0]*m*n).reshape(m,n)
    for k in d.keys():
        add_elt = np.array(k).reshape(m,n)
        elt_mat += add_elt
    return elt_mat

# Input: string = variable name for ideal defined via M2, R = PolRing object
# Output: BIdeal object
# IMPORTANT: R had to be defined without specifying a grading
def M2_ideal_to_Sage(name,R):
    g = m2.macaulay2("gens "+name).sage()
    gens = []
    for i in range(g.ncols()):
        gens.append(g[0,i])
    return BIdeal(gens,R)

'''
POLYNOMIALS, POLYNOMIAL RINGS, AND IDEALS
'''
# xR, yR are Sage rings containing x,y variables respectively
# X,Y are lists of x and y variables (usually created using VariableGenerator)
# x,y are lists of strings of x and y variables
class SplitPoly():
    """A class for polynomials in two sets of variables ('x' variables and 'y'
    variables). The rings in which the 'x' and 'y' variables live must be 
    specified.

    :param poly: the polynomial as an element of a Sage MPolynomialRing
    :type poly: class 'sage.rings.polynomial.multi_polynomial_libsingular.MPolynomial_libsingular'
    :param xR: the ring of 'x' variables
    :type xR: class 'sage.rings.polynomial.multi_polynomial_libsingular.MPolynomialRing_libsingular'
    :param yR: the ring of 'y' variables
    :type yR: class 'sage.rings.polynomial.multi_polynomial_libsingular.MPolynomialRing_libsingular'

    :ivar X: the generators of xR (output of xR.gens())
    :ivar Y: the generators of yR (output of yR.gens())
    :ivar x: list of strings ['xi'] of 'x' variables
    :ivar y: list of strings ['yi'] of 'y' variables
    :ivar deg: degree of the polynomial
    :ivar d: dictionary for the polynomial of the form {degree : homogeneous component of the polynomial with that degree}
    """

    def __init__(self,poly,xR,yR):
        self.poly = poly
        self.R = self.poly.parent()
        self.xR = xR
        self.yR = yR
        self.X = self.xR.gens()
        self.Y = self.yR.gens()
        self.x = ['x'+str(i) for i in range(len(self.X))]
        self.y = ['y'+str(i) for i in range(len(self.Y))]

        self.deg = self.poly.total_degree()
        self.d = defaultdict(self.poly.parent())

        for coeff,monom in self.poly:
            self.d[monom.degree()] += coeff * monom
    
    # Arguments for x,y: 's' (Schur), 'ss' (Schubert), 'm' (Monomial)
    # assumes input is a polynomial in x and y variables
    # specify var_groups as [[3,2,4],[1,4,2]] (first 3 x variables, next 2 x variables,...)
    # if not specified, var groups is assumed to be [[len(X variables)],[len(Y variables)]]
    # can instead input a permutation - will take the maximal Levi group
    def expand(self,x=None,y=None,I=[],J=[],returnDict=False,maxIter=10000):
        """Expands the polynomial into a sum of products of Schur polynomials
        based on a given Levi datum. If no inputs are given, returns the polynomial. 
        If the user specifies x='m' or y='m', the corresponding variables will
        be left as monomials. The default output is a string representing
        the expansion. Optionally, can output a dictionary of the form {tuple of 
        partitions, permutations, or exponents : coefficient in the expansion}.

        :param x: What type of polynomial to expand the x variables in ('s' for Schur,'m' for Monomial), defaults to None
        :type x: str, optional
        :param y: What type of polynomial to expand the x variables in ('s' for Schur,'m' for Monomial), defaults to None,
        :type y: str, optional
        :param I: Row Levi datum, defaults to []
        :type I: list, optional
        :param J: Column Levi datum, defaults to []
        :type J: list, optional
        :param returnDict: True to return a dictionary, False to return a string, defaults to False
        :type returnDict: bool, optional
        :param maxIter: Maximum number of subtractions allowed per degree component, defaults to 10000
        :type maxIter: int, optional
        :raises MemoryError: if the number of subtractions exceeds maxIter
        :return: A string representing the desired expansion (or, optionally, a dictionary)
        :rtype: str (optionally, dict)
        """

        if (x is None and y is None):
            return self.poly       
        if x is None:
            x = 'm'       
        if y is None:
            y = 'm'

        # process Levi datum
        var_groups = [datum_to_alphabet(I),datum_to_alphabet(J)]

        # initialize return dictionary
        retDict = defaultdict()

        # right now, take support for schur, schubert, and monomial
        # need to generate schur/schubert based on filtered tuples

        # filters tuples into correct input format for tType
        def filter_tuple(tType,tple,gps=None):
            if gps is not None:
                counter = 0
                partList = [[] for size in gps]
                for i in range(len(gps)):
                    partList[i] = [tple[j] for j in range(counter,gps[i]+counter)]
                    counter += gps[i]

            if gps is None:
                partList = [[elt for elt in tple]]

            if tType == 's':
                return partList

            if tType == 'm':
                return [[elt for elt in tple]]

        def tuple_to_poly(tType,ls,ringDict,subVars,rehome,numVars=None,i=None):
            R = ringDict[tType]

            if tType == 's':
                schur = rehome(R(ls).expand(numVars))
                schur = self.R(schur.subs(**subVars))
                return schur

            elif tType == 'm':
                m = 1
                for i in range(len(ls)):
                    m *= subVars[i]**ls[i]
                m = self.R(m)
                return m

        # s sort: lex, ss sort: revLex
        # sortDict: 'expansion': requires revLex?
        # if any require revLex, then sort by revLex
        sortDict = {'s':False,'ss':True,'m':True}
        ringDict = {'s':SymmetricFunctions(QQ).schur(),
                    'm':self.R}
        rehomeRingDictX = {'s':PolynomialRing(QQ,names=self.x), 
                           'm':self.xR}
        rehomeRingDictY = {'s':PolynomialRing(QQ,names=self.y), 
                           'm':self.yR}

        xIt = iter(self.X)
        yIt = iter(self.Y)
        yAlphabet = [[next(yIt) for _ in range(size)] for size in var_groups[1]]
        yAlphabetSubs = [{'y'+str(i):yAlphabet[j][i] for i in range(len(yAlphabet[j]))} for j in range(len(yAlphabet))]
        xAlphabet = [[next(xIt) for _ in range(size)] for size in var_groups[0]]
        xAlphabetSubs = [{'x'+str(i):xAlphabet[j][i] for i in range(len(xAlphabet[j]))} for j in range(len(xAlphabet))]

        varDictX = {'s':xAlphabetSubs,
                    'm':[self.X],
                    }

        varDictY = {'s':yAlphabetSubs,
                    'm':[self.Y],
                    }

        [xO,yO] = [sortDict[x],sortDict[y]]
        isRev = all([xO,yO])

        deg = self.poly.total_degree()

        # create dictionary 
        d = defaultdict(self.poly.parent())
        for coeff,monom in self.poly:
            d[monom.degree()] += coeff*monom

        # iterate through degree components
        for i in reversed(range(deg+1)):
            iters = 0
            degDict = d[i].dict()
            pol = d[i]
            # check if polynomial is constant
            if str(self.d[i]).isdigit():
                if not int(str(self.d[i])) == 0:
                    tple = tuple([0 for i in range(len(self.X) + len(self.Y) + 2)]) 
                    tpleX = filter_tuple(x,[elt for elt in tple[:len(self.X)]],gps=var_groups[0])
                    tpleY = filter_tuple(y,[elt for elt in tple[len(self.X):]],gps=var_groups[1])
                    unit = str([tpleX,tpleY])
                    if unit not in retDict:
                        retDict[unit] = int(str(self.d[i]))
                    else:
                        retDict[unit] += int(str(self.d[i]))
            
            while iters <= maxIter and not str(pol).isdigit():
                iters += 1
                degCmpntKeys = degDict.keys()

                if isRev: 
                    degCmpntKeys = list(reversed([elt for elt in degCmpntKeys]))
                if not isRev: 
                    degCmpntKeys = [elt for elt in degCmpntKeys]

                tple = degCmpntKeys[0]

                tpleX = filter_tuple(x,[elt for elt in tple[:len(self.X)]],gps=var_groups[0])

                # Find tupleY by looking at all possible y tuples associated with given x tuple
                xPartTuple = tple[:len(self.X)]
                startsTpleX = []

                for elt in degCmpntKeys:
                    if all([elt[i]==xPartTuple[i] for i in range(len(xPartTuple))]):
                        startsTpleX.append(elt)
                if isRev:
                    startsTpleX.sort(reverse=True)
                if not isRev:
                    startsTpleX.sort()

                tple1 = startsTpleX[-1]
                tpleY = filter_tuple(y,[elt for elt in tple1[len(self.X):]],gps=var_groups[1])

                xPol = 1
                for i in range(len(tpleX)):
                    xPol *= tuple_to_poly(x,tpleX[i],ringDict,varDictX[x][i],rehomeRingDictX[x],numVars=len(tpleX[i]))

                yPol = 1
                for j in range(len(tpleY)):
                    yPol *= tuple_to_poly(y,tpleY[j],ringDict,varDictY[y][j],rehomeRingDictY[y],numVars=len(tpleY[j]))

                retKey = str([tpleX,tpleY])
                tple = tple1
                coeff = degDict[tple]

                if retKey in retDict:
                    retDict[retKey] += degDict[tple]
                if retKey not in retDict:
                    retDict[retKey] = degDict[tple]
                if retDict[retKey]==0:
                    del retDict[retKey]

                subtractPol = xPol*yPol*coeff
                pol = pol - subtractPol
                degDict = pol.dict() 

                if iters > maxIter:
                    raise MemoryError("Exceeded maximum number of iterations (default: 10000). Please raise the maximum number of iterations and try again.")   

        if returnDict:
            return retDict

        return self.print(retDict=retDict,x=x,y=y)
    
    # TODO: support for tex expansion
    def print(self,retDict=None,x=None,y=None):
        if retDict is None:
            return self.poly
        if retDict is not None:
            retStr = ''
            keyLs = [elt for elt in list(retDict.keys())]
            itnum = 0
            for key in keyLs:
                coeff = int(retDict[key])
                if coeff < 0:
                    if itnum==0:
                        retStr += '-' + str(abs(retDict[key])) + '*'
                    if itnum > 0:
                        retStr += ' - ' + str(abs(retDict[key])) + '*'
                if coeff > 0:
                    if itnum > 0:
                        retStr += ' + ' + str(retDict[key]) + '*'
                    if itnum==0:
                        retStr += str(retDict[key]) + '*'
                keyEval = eval(key)
                for elt in keyEval[0]:
                    retStr += x + str(elt)
                for elt in keyEval[1]:
                    retStr += y + str(elt)

                itnum += 1
            return retStr

class PolRing():
    """Class for polynomial rings in an m by n matrix of variables.

    :param m: number of rows in the matrix of variables
    :type m: int
    :param n: number of columns in the matrix of variables
    :type n: int
    :param name: variable names, optional, default 'z'
    :type name: str
    :param to: Macaulay2 ring term order, optional, default 'GRevLex'
    :type to: str

    :ivar R: Sage PolynomialRing in an m by n matrix of variables
    :ivar Z: matrix of variables
    :ivar xR: Sage PolynomialRing of m 'x' variables x1,...,xm
    :ivar yR: Sage PolynomialRing of n 'y' variables y1,...,yn
    :ivar X: generators of xR, output of xR.gens()
    :ivar Y: generators of yR, output of yR.gens()
    :ivar graded_m2_str: str containing Macaulay2 command for generating R (with multigrading)
    :ivar ungraded_m2_str: str containing Macaulay2 command for generating R (no multigrading)  
    """

    # returns a polynomial ring in mxn variables
    def __init__(self,m,n,name='z',to='GRevLex'):
        self.m = m
        self.n = n
        self.vars = var_gen(self.m,self.n,name)
        self.varsM2 = var_gen(self.m,self.n,'m')
        self.R = PolynomialRing(QQ,names=self.vars)

        self.Z = matrix(self.R,np.array(self.vars).reshape(m,n)) 
        
        self.xR = PolynomialRing(QQ,names=['x'+str(i) for i in range(1,self.m+1)]) 
        self.yR = PolynomialRing(QQ,names=['y'+str(i) for i in range(1,self.n+1)]) 
        self.xyR = PolynomialRing(QQ,names=['x'+str(i) for i in range(1,self.m+1)]+['y'+str(i) for i in range(1,self.n+1)])

        self.X = self.xR.gens()
        self.Y = self.yR.gens()
        self.XY = self.xyR.gens()

        self.graded_m2_str = m2_graded_ring_str(m,n,self.vars,to)
        self.ungraded_m2_str = m2_ungraded_ring_str(self.vars,to)

    def hilb_exp(self,deg):
        """Returns Hilbert series for R up to specified degree as a SplitPoly object.

        :param deg: degree of the expansion
        :type deg: int
        :return: Hilbert series of R up to degree deg
        :rtype: SplitPoly
        """

        m2.macaulay2.set('R',self.graded_m2_str) 
        h = m2.macaulay2("toString hilbertSeries(R,Order=>"+str(deg)+")").sage()
        p = M2_to_Sage(h,self.XY)
        return SplitPoly(p,self.xR,self.yR)

# Named BIdeal to avoid conflict with Sage objects
# PR: instance of PolRing
class BIdeal():
    """Class for ideals of PolRing objects.

    :param gens: generators of the ideal
    :type gens: polynomials in PR.R
    :param PR: ring in which the ideal lives
    :type PR: PolRing

    :ivar I: ideal of PR.R generated by gens
    :ivar R: alias of PR.R
    :ivar X: alias of PR.X
    :ivar Y: alias of PR.Y
    :ivar m2_ideal_str: str containing command for defining I in Macaulay2 
    """

    def __init__(self,gens,PR):
        self.gens = gens
        self.PR = PR
        self.R = self.PR.R
        self.I = self.R.ideal(self.gens)
        self.gens = self.I.gens()
        self.X = self.PR.X
        self.Y = self.PR.Y
        self.XY = self.PR.XY

        gens = ''
        for elt in self.gens:
            gens += str(elt)+','
        gens = gens[:len(gens)-1]
        self.m2_ideal_str = "ideal("+gens+")"
    
    def bicrystalline(self,I,J,use_to=None,detailed_output=False):
        """Checks whether the ideal is bicrystalline with respect to a given
        Levi action. Optionally, instead of checking all term orders, one
        can check a specific term order. This function does *not* check whether the ideal 
        is stable under the action of the given Leiv group, or whether it is homogeneous.

        :param I: row Levi datum
        :type I: list
        :param J: column Levi datum
        :type J: list
        :param use_to: Macaulay2 term order to use, defaults to None
        :type use_to: list, optional
        :param detailed_output: when true, outputs details about the checks it makes to the terminal, defaults to False
        :type detailed_output: bool, optional
        :return: True if the ideal is bicrystalline (assuming it is homogeneous and stable under the input Levi group), else False
        :rtype: bool
        """

        m2.macaulay2.set("R",self.PR.ungraded_m2_str)
        m2.macaulay2.set("I",self.m2_ideal_str)
        
        # Find permissible crystal operators
        permRow = [i for i in range(I[-1]) if i not in I]
        permCol = [j for j in range(J[-1]) if j not in J]

        # if term order specified, find GB for the specified term order
        if use_to is not None:
            in_ideals_gen_ls = [self.gb_lts(to=use_to)]

        # if term order is not specified, find the Grobner fan
        if use_to is None:
            if detailed_output:
                print("Computing gfan")

            m2.macaulay2.set("g","gfan I")

            l = m2.macaulay2("#g").sage()
            in_ideals_gen_ls = [[] for i in range(l)]
            for i in range(l):
                in_ideals_gen_ls[i] = m2.macaulay2("gfanLeadingTerms g#"+str(i)).sage()

        # compute list of LTs of GB elts
        # gen_ls = [[lts of GB elts for TO 1], ...] as np matrices
        gen_ls = []
        for in_ideal in in_ideals_gen_ls:
            gb_lts_mats = []
            for elt in in_ideal:
                gb_lts_mats.append(sage_mon_to_mat(elt,self.PR.m,self.PR.n))
            gen_ls.append(gb_lts_mats)

        def is_bicrystalline(self,gens):
            if detailed_output:
                print('Checking initial ideal ',str(gens))

            # Create dictionary {str(gb elt): [{i:1 + sum of elts row i,i+1},{j:1 + sum of elts cols j,j+1}]}
            sdict = {str(g):[{i:1+int(g[i:i+2,:].sum()) for i in permRow},{j:1+int(g[:,j:j+2].sum()) for j in permCol}] for g in gens}

            # Find maximum over all gb elts of any sum
            rowtop = 0 if permRow==[] else max([max([sdict[str(g)][0][i] for i in permRow]) for g in gens])
            coltop = 0 if permCol==[] else max([max([sdict[str(g)][1][j] for j in permCol]) for g in gens])

            if detailed_output:
                print('largest degree for rows:',rowtop)
                print('largest degree for cols:',coltop)
            # Create a dictionary that associates each size in range top to the list of gb elts, i, j to check for 
            # that size
            crowdict = {size:[(g,[i for i in permRow if sdict[str(g)][0][i] >= size]) for g in gens] for size in range(rowtop+1)}
            ccoldict = {size:[(g,[j for j in permCol if sdict[str(g)][1][j] >= size]) for g in gens] for size in range(coltop+1)}

            # check rows
            for size in range(max(rowtop+1,coltop+1)):
                if detailed_output:
                    print('Checking degree:',size)

                if permRow!=[] and size <= rowtop:
                    comps = compositions(size,2*self.PR.n)

                    for comp in comps:
                        comp = np.matrix(comp).reshape(2,self.PR.n)
                        for (g,row_check) in crowdict[size]:
                            for i in row_check:
                                check_mat = np.matrix(g)
                                check_mat[i-1:i+1,:] += comp
                                e_check_mat = e(check_mat,i,0)
                                if not is_nonstd(gens,e_check_mat):
                                    if detailed_output:
                                        print('Not bicrystalline (row raising operator '+str(i)+'):')
                                        print(check_mat)
                                        print(e_check_mat)
                                    return False

                                f_check_mat = f(check_mat,i,0)
                                if not is_nonstd(gens,f_check_mat):
                                    if detailed_output:
                                        print('Not bicrystalline (row raising operator '+str(i)+'):')
                                        print(check_mat)
                                        print(f_check_mat)
                                    return False

                if permCol!=[] and size <= coltop:
                    comps = compositions(size,2*self.PR.m)

                    for comp in comps:
                        comp = np.matrix(comp).reshape(self.PR.m,2)
                        for (g,col_check) in ccoldict[size]:
                            for j in col_check:
                                check_mat = np.matrix(g)
                                check_mat[:,j-1:j+1] += comp
                                e_check_mat = e(check_mat,j,1)
                                if not is_nonstd(gens,e_check_mat):
                                    if detailed_output:
                                        print('Not bicrystalline (col raising operator '+str(j)+'):')
                                        print(check_mat)
                                        print(e_check_mat)
                                    return False

                                f_check_mat = f(check_mat,j,1)
                                if not is_nonstd(gens,f_check_mat):
                                    if detailed_output:
                                        print('Not bicrystalline (col raising operator '+str(j)+'):')
                                        print(check_mat)
                                        print(f_check_mat)
                                    return False
            if detailed_output:
                print('Ideal is bicrystalline')
            return True

        for k in range(len(gen_ls)):
            if detailed_output and not use_to:
                print(m2.macaulay2("g#"+str(k)))

            if is_bicrystalline(self,gen_ls[k]):
                if detailed_output:
                    print("True")
                return True

        if use_to is None and detailed_output:
            print("Ideal is not bicrystalline for any term order")

        if use_to is not None and detailed_output:
            print("Ideal is not bicrystalline for this term order:",use_to)

        return False

    # calculates a test set given (lead terms of a) grobner basis
    # Input: op = ['f' or 'e',i,'r' or 'c'], grobner bases (optional), term order (optional)
    def test_set(self,op,gb=None,to=None):
        """Outputs a test set for a given bicrystal operator, and optionally
        a given Grobner basis or term order.

        :param op: bicrystal operator as a list ['f' or 'e',i,'r' or 'c'], e.g. ['f',1,'r'] for the row lowering operator f1
        :type op: list
        :param gb: lead terms of a Grobner basis for I as a list of numpy matrices, defaults to None
        :type gb: list, optional
        :param to: a Macaulay2 term order, defaults to None
        :type to: str, optional
        :return: a test set for I as a list of numpy matrices
        :rtype: list
        """

        dim = self.PR.n if op[2]=='r' else self.PR.m

        if gb is None:
            gb = self.gb_lts_mats(to=to)

        # Compute the largest sum of adjacent rows/columns
        sums_ls = []
        for g in gb:
            if op[2]=='r':
                sums_ls.append(int(g[op[1]-1:op[1]+1,:].sum()))

            if op[2]=='c':
                sums_ls.append(int(g[:,op[1]-1:op[1]+1].sum()))

        sigma = max(sums_ls) + 1

        ts = []
        for i in range(sigma+1):
            C = compositions(i,2*dim)

            for c in C:
                c = np.matrix(c).reshape(2,dim) if op[2]=='r' else np.matrix(c).reshape(dim,2)
                for k in range(len(gb)):
                    g = gb[k]
                    if sums_ls[k] + 1 >= i:
                        new_mat = np.matrix(g)
                        if op[2]=='r':
                            new_mat[op[1]-1:op[1]+1,:] += c
                        if op[2]=='c':
                            new_mat[:,op[1]-1:op[1]+1] += c
                        ts.append(new_mat)

        TS = {ar.tostring():ar for ar in ts}

        return TS.values()

    def min_test_set(self,op,gb=None,to=None):
        """Outputs the unique *minimal* test set for a given bicrystal operator,
        and optionally a given Grobner basis or term order.

        :param op: bicrystal operator as a list ['f' or 'e',i,'r' or 'c'], e.g. ['f',1,'r'] for the row lowering operator f1
        :type op: list
        :param gb: lead terms of a Grobner basis for I as a list of numpy matrices, defaults to None
        :type gb: list, optional
        :param to: a Macaulay2 term order, defaults to None
        :type to: str, optional
        :return: the minimal test set for I as a list of numpy matrices
        :rtype: list
        """

        ts = self.test_set(op,gb,to)

        mts = []
        for elt in ts:
            if op[0]=='f':
                if f(elt,op[1],op[2]) is not None:
                    bad = False
                    for d in mts:
                        if np.min(elt-d) >= 0 and np.min(f(elt,op[1],op[2])-f(d,op[1],op[2])) >= 0:
                            bad = True
                            break
                    if not bad:
                        mts.append(elt)

            if op[0]=='e':
                if e(elt,op[1],op[2]) is not None:
                    bad = False
                    for d in mts:
                        if np.min(elt-d) >= 0 and np.min(e(elt,op[1],op[2])-e(d,op[1],op[2])) >= 0:
                            bad = True
                            break
                    if not bad:
                        mts.append(elt)
        return mts

    # NB: This function is only called from bicrystalline or nstd_mons, won't work independently
    def initial_ideal_from_gens(self,gens):
        m2_str = "monomialIdeal ideal("
        for gen in gens:
            cur_str = str(gen).replace('m','z')
            m2_str += cur_str + ','
        m2_str = m2_str[:len(m2_str)-1]+")"
        m2.macaulay2.set("M",m2_str)

    # returns all non-standard monomials for a given degree
    # if gens is specified, will create an initial ideal from the given generators
    # if leq=True, will find all non-standard monomials less than or equal to a given degree
    def nstd_mons(self,deg,gens=None,leq=False):
        """Returns all non-standard monomials for I up to a given degree as ring elements.

        :param deg: degree
        :type deg: int
        :param gens: optional list of lead terms of generators of the initial ideal as ring elements, defaults to None
        :type gens: list, optional
        :param leq: optionally return all nonstandard monomials of at most input degree, defaults to False
        :type leq: bool, optional
        :return: list of all nonstandard monomials of a given degree as ring elements
        :rtype: list
        """

        # Make sure that ring and ideal are defined in M2, use ungraded version
        m2.macaulay2.set("R",self.PR.ungraded_m2_str)
        m2.macaulay2.set("I",self.m2_ideal_str)

        if gens is None:
            gens = self.gb_lts()

        self.initial_ideal_from_gens(gens)
        ret_val = []

        if not leq:
            m2.macaulay2.set("nonStdMons","entries super basis("+str(deg)+",M)")
            m2.macaulay2.set("nonStdMons","nonStdMons#0")
            l = m2.macaulay2("#nonStdMons").sage()

            for i in range(l):
                cur_str = m2.macaulay2("toString nonStdMons#"+str(i)).sage().replace('m','z')
                ret_val.append(M2_mon_to_Sage(cur_str,self.PR.Z))

            return ret_val

        if leq:
            for k in range(1,deg+1):
                m2.macaulay2.set("nonStdMons","entries super basis("+str(k)+",M)")
                m2.macaulay2.set("nonStdMons","nonStdMons#0")
                l = m2.macaulay2("#nonStdMons").sage()

                for i in range(l):
                    cur_str = m2.macaulay2("toString nonStdMons#"+str(i)).sage().replace('m','z')
                    ret_val.append(M2_mon_to_Sage(cur_str,self.PR.Z))

            return ret_val


    def nstd_mons_mats(self,deg,gens=None,leq=False):
        """Returns all non-standard monomials for I up to a given degree as numpy matrices.

        :param deg: degree
        :type deg: int
        :param gens: optional list of lead terms of generators of the initial ideal as ring elements, defaults to None
        :type gens: list, optional
        :param leq: optionally return all nonstandard monomials of at most input degree, defaults to False
        :type leq: bool, optional
        :return: list of all nonstandard monomials of a given degree as numpy matrices
        :rtype: list
        """

        non_std_mons = self.nstd_mons(deg,gens=gens,leq=leq)
        ret_val = []
        for elt in non_std_mons:
            ret_val.append(sage_mon_to_mat(elt,self.PR.m,self.PR.n))
        return ret_val

    # Uses M2 to compute the Hilbert series
    # Input: degree of the expansion
    def hilb_exp(self,deg):
        """Computes the Hilbert series expansion of I up to a given degree.
        The Hilbert series is output as a SplitPol.

        :param deg: degree
        :type deg: int
        :return: Hilbert series up to a given degree
        :rtype: SplitPol
        """

        # Define the ideal in M2
        m2.macaulay2.set("R",self.PR.graded_m2_str)
        m2.macaulay2.set("I",self.m2_ideal_str)

        m2_command = 'toString hilbertSeries(I, Order=>'+str(deg)+')'
        pol = m2.macaulay2(m2_command)
        pol = M2_to_Sage(str(pol),self.XY)
        return SplitPoly(pol,self.PR.xR,self.PR.yR)

    def gb(self,to=None):
        """Computes a Grobner basis for the ideal. Optionally, one may specify
        the term order. The default is the term order of the parent PolRing.

        :param to: Macaulay2 term order, defaults to None
        :type to: str, optional
        :return: list of Grobner basis generators as ring elements
        :rtype: list
        """

        if to is None:
            m2.macaulay2.set("R",self.PR.ungraded_m2_str)
        if to is not None:
            m2.macaulay2.set("R",m2_ungraded_ring_str(self.PR.vars,to))

        m2.macaulay2.set("I",self.m2_ideal_str)

        LTs = []
        m2.macaulay2.set("gbGens","entries gens gb I")
        m2.macaulay2.set("gbGens","gbGens#0")
        l = m2.macaulay2("#gbGens").sage()
        for i in range(l):
            s = m2.macaulay2("gbGens#"+str(i)).sage()
            LTs.append(s)
        return LTs

    # Outputs gb for self 
    # Default: antidiagonal term order
    def gb_lts(self,to=None):
        """Computes the lead terms of a Grobner basis for the ideal. Optionally, 
        one may specify the term order. The default is the term order of the 
        parent PolRing.

        :param to: Macaulay2 term order, defaults to None
        :type to: str, optional
        :return: list of lead terms of Grobner basis generators as ring elements
        :rtype: list
        """

        if to is None:
            m2.macaulay2.set("R",self.PR.ungraded_m2_str)
        if to is not None:
            m2.macaulay2.set("R",m2_ungraded_ring_str(self.PR.vars,to))

        m2.macaulay2.set("I",self.m2_ideal_str)

        LTs = []
        m2.macaulay2.set("gbGens","entries leadTerm gens gb I")
        m2.macaulay2.set("gbGens","gbGens#0") 
        l = m2.macaulay2("#gbGens").sage()
        for i in range(l):
            s = m2.macaulay2("toString gbGens#"+str(i)).sage()
            m = M2_mon_to_Sage(s,self.PR.Z)
            LTs.append(m)
        return LTs

    def gb_lts_mats(self,to=None):
        """Computes the lead terms of a Grobner basis for the ideal. Optionally, 
        one may specify the term order. The default is the term order of the 
        parent PolRing. The lead terms are output as numpy matrices.

        :param to: Macaulay2 term order, defaults to None
        :type to: str, optional
        :return: list of lead terms of Grobner basis generators as numpy matrices
        :rtype: list
        """

        lts = self.gb_lts(to=to)
        ret_val = []
        for elt in lts:
            ret_val.append(sage_mon_to_mat(elt,self.PR.m,self.PR.n))
        return ret_val

    def def_m2_vars(self,graded=False,ideal_name="I",ring_name="R"):
        """Define the ideal in Macaulay2. After running this command, one can 
        run commands referencing the ideal "I" in Macaulay2.

        :param graded: whether the Macaulay2 ideal should be graded, defaults to False
        :type graded: bool, optional
        :param ideal_name: what the ideal should be called in Macaulay2, defaults to "I"
        :type ideal_name: str, optional
        :param ring_name: what the ring should be called in Macaulay2, defaults to "R"
        :type ring_name: str, optional
        """

        if graded:
            m2.macaulay2.set(ring_name,self.PR.graded_m2_str)
            m2.macaulay2.set(ideal_name,self.m2_ideal_str)
        if not graded:
            m2.macaulay2.set(ring_name,self.PR.ungraded_m2_str)
            m2.macaulay2.set(ideal_name,self.m2_ideal_str)

'''
GROUP ACTIONS
'''
# Check if a given Levi group L acts on an ideal I
def check_action(I,L,detailed_output=False):
    """Checks whether a given Levi group acts on a given ideal.

    :param I: The ideal to be checked
    :type I: BIdeal
    :param L: A Levi datum [I,J]
    :type L: list
    :param detailed_output: If True, prints a pair (Gröbner basis element,Gröbner basis element after group action) which fails the check (if such a pair exists), defaults to False
    :type detailed_output: bool, optional
    :return: True if the Levi group defined by L acts on I, else False
    :rtype: bool
    """

    permRows = [i for i in range(I.PR.m) if i not in L[0]]
    permCols = [j for j in range(I.PR.n) if j not in L[1]]

    sub_dicts_I = {i:{I.PR.Z[i-1,j]:I.PR.Z[i-1,j]+I.PR.Z[i,j] for j in range(I.PR.n)} for i in permRows}
    sub_dicts_I_lower = {i:{I.PR.Z[i,j]:I.PR.Z[i-1,j]+I.PR.Z[i,j] for j in range(I.PR.n)} for i in permRows}
    sub_dicts_J = {j:{I.PR.Z[i,j-1]:I.PR.Z[i,j-1]+I.PR.Z[i,j] for i in range(I.PR.m)} for j in permCols}
    sub_dicts_J_lower = {j:{I.PR.Z[i,j]:I.PR.Z[i,j-1]+I.PR.Z[i,j] for i in range(I.PR.m)} for j in permCols}

    for g in I.gens:
        for i in permRows:
            f1 = g.subs(sub_dicts_I[i])
            if not f1 in I.I:
                if detailed_output:
                    print(g,f1)
                return False

            f2 = g.subs(sub_dicts_I_lower[i])
            if not f2 in I.I:
                if detailed_output:
                    print(g,f2)
                return False

        for j in permCols:
            f1 = g.subs(sub_dicts_J[j])
            if not f1 in I.I:
                if detailed_output:
                    print(g,f1)
                return False

            f2 = g.subs(sub_dicts_J_lower[j])
            if not f2 in I.I:
                if detailed_output:
                    print(g,f2)
                return False
    
    return True


'''
CLASSES OF IDEALS
'''
# Input: matrix of variables in some ring, submatrix [[list of rows],[list of columns]], integer k
# Output: k x k minors of submatrix
def minors(M,k,B=None):
    """Outputs the k by k minors of the matrix M of size k. Optionally, outputs
    the k by k minors of a submatrix B of M, input as [[list of rows of B],[list of columns of B]].

    :param M: matrix
    :type M: Sage matrix
    :param k: minor size
    :type k: int
    :param B: submatrix of M, input as [[list of rows of B],[list of columns of B]] (row and column numbers are 0-indexed), defaults to None
    :type B: list, optional
    :return: list of minors
    :rtype: list
    """

    if B is None:
        B = [[i for i in range(M.nrows())],[j for j in range(M.ncols())]]
    if k > len(B[0]) or k > len(B[1]):
        print('Cannot take k x k minors of this matrix (k is too large)')
        return False
    
    row_combs = list(it.combinations(B[0],k))
    col_combs = list(it.combinations(B[1],k))

    retVal = []
    for row in row_combs:
        for col in col_combs:
            retVal.append(M[row,col].determinant([row,col]))
        
    return retVal

def shape_ideal(l,m,n,R=None):
    """Outputs the BIdeal I generated by all bitableaux of shape l in
    the polynomial ring in a matrix of m by n variables.

    :param l: a partition, as a decreasing list of integers
    :type l: list
    :param m: number of rows of the matrix of variables
    :type m: int
    :param n: number of columns of the matrix of variables
    :type n: int
    :param R: PolRing in which to define the ideal, defaults to None
    :type R: PolRing, optional
    :return: shape ideal I
    :rtype: BIdeal
    """

    if R is None:
        R = PolRing(m,n)
    gens = all_nonstd_pol_bitabs(l,R)
    I = BIdeal(gens,R)
    return I

# Classical determinantal ideals
# Input: number of rows, number of columns, size of minor
# Output: instance of BIdeal
def classical_det_ideal(m,n,k):
    """Creates the BIdeal I of k by k minors of an m by n matrix.

    :param m: number of rows in the matrix of variables
    :type m: int
    :param n: number of columns in the matrix of variables
    :type n: int
    :param k: size of minors
    :type k: int
    :return: classical determinantal ideal
    :rtype: BIdeal
    """

    R = PolRing(m,n)
    gens = minors(R.Z,k)
    I = BIdeal(gens,R)
    return I

# matrix Schubert ideals
# Default: effective matrix Schubert ideal
# Input: permutation w
# Optional input: region = region of variables to use
# Output: instance of BIdeal
def msv(w,R=None):
    """Creates the BIdeal I defining the matrix Schubert variety corresponding
    to a permutation w.

    :param w: permutation in one-line notation as a list of integers
    :type w: list
    :param region: list of tuples (i,j) defining a region in which to define the ideal, defaults to None
    :type region: list, optional
    :param R: the ring in which I is to be defined, defaults to None
    :type R: PolRing, optional
    :return: ideal defining the matrix Schubert variety for w
    :rtype: BIdeal
    """

    if type(w) is list:
        w = Perm(w)

    if R==None:
        R = PolRing(w.l,w.l)

    def fulton_generator_mats():
        essSet = w.filled_ess_set()
        minors = []
        for box in essSet:
            boxMat = R.Z[[i for i in range(box[0][0]+1)],[j for j in range(box[0][1]+1)]]
            minors += [boxMat[rows,cols] for cols in Combinations(boxMat.ncols(),box[1]+1) for rows in Combinations(boxMat.nrows(),box[1]+1)]
        return minors

    def fulton_generators():
        fultonMats = fulton_generator_mats()
        retVal = []
        for elt in fultonMats:
            retVal.append(elt.det())
        return retVal
    
    I = BIdeal(fulton_generators(),R)
    return I

def eff_msv(w):
    """Creates the effective matrix Schubert ideal corresponding to w. 
    The effective matrix Schubert ideal lives in the ring of r by c matrices,
    where r is the largest row in which the Rothe diagram for w has a box and c
    is the largest column in which the Rothe diagram for w has a box. The ideal is
    generated by the Fulton generators, together with all variables outside the effective
    region (i.e. all variables zij for which (i,j) is strictly southeast of any box in
    the Rothe diagram for w).

    :param w: permutation in one-line notation as a list of integers
    :type w: list
    :return: ideal defining the effective matrix Schubert variety for w
    :rtype: BIdeal
    """
    if type(w) is list:
        w = Perm(w)

    R = PolRing(w.max_row+1,w.max_col+1)

    def fulton_generator_mats():
        essSet = w.filled_ess_set()
        minors = []
        for box in essSet:
            boxMat = R.Z[[i for i in range(box[0][0]+1)],[j for j in range(box[0][1]+1)]]
            minors += [boxMat[rows,cols] for cols in Combinations(boxMat.ncols(),box[1]+1) for rows in Combinations(boxMat.nrows(),box[1]+1)]
        return minors

    def fulton_generators():
        fultonMats = fulton_generator_mats()
        retVal = []
        for elt in fultonMats:
            retVal.append(elt.det())
        return retVal
    
    gens = fulton_generators()
    ess_set = w.ess_set()
    for i in range(w.max_row+1):
        for j in range(w.max_col+1):
            in_reg = False
            for box in ess_set:
                if i <= box[0] and j <= box[1]:
                    in_reg = True
                    break
            if not in_reg:
                gens.append(R.Z[i,j])

    I = BIdeal(gens,R)
    return I

# matrix Richardson ideal
def mrv(u,v):
    """Constructs the matrix Richardson ideal corresponding to input
    permutations u and v.

    :param u: a permutation in one-line notation as a list of integers
    :type u: list
    :param v: a permutation in one-line notation as a list of integers
    :type v: list
    :return: the matrix Richardson ideal corresponding to u and v
    :rtype: BIdeal
    """

    d = max(len(u),len(v))
    R = PolRing(d,d)
    Iu = msv(u,R=R)
    Iv = msv(v,R=R)

    vg = Iv.gens
    subs_dict = {R.Z[i,j]:R.Z[d-i-1,j] for i in range(d) for j in range(d)}
    new_vg = [g.subs(subs_dict) for g in vg]

    gens = Iu.gens + new_vg

    I = BIdeal(gens,R)
    return I

'''
BITABLEAUX
'''
# Given a pair of SSYT, return the bitableau as a list [[[row indices],[column indices]],...]
def bitableau(P,Q):
    if not len(P[0])==len(Q[0]):
        print('Error: P,Q tableaux are not the same shape')
        return
    bitab = [[[P[i][j] for i in range(len(P)) if j<len(P[i])],[Q[i][j] for i in range(len(Q)) if j<len(Q[i])]] for j in range(len(P[0]))]
    return bitab

# Given a pair of SSYT and a ring R (instance of PolRing), return the polynomial corresponding to that bitableau in R
def poly_bitableau(P,Q,R):
    bitab = bitableau(P,Q)
    retVal = 1
    for [r,c] in bitab:
        retVal *= R.Z[sorted([r[i]-1 for i in range(len(r))]),sorted([c[i]-1 for i in range(len(c))])].determinant()
    return retVal

# Given a shape, max entry of P, max entry of Q, generate a list of all standard bitableaux of that shape and those max entries
def all_bitabs(shape,m,n,left_just=False):
    P_tab = SemistandardTableaux(shape, max_entry=m) 

    if not left_just:
        Q_tab = SemistandardTableaux(shape, max_entry=n) 
    if left_just:
        Q_tab = [SemistandardTableau([[i+1]*shape[i] for i in range(len(shape))])] 

    tabs = it.product(P_tab,Q_tab)
    return tabs

def pick_one_from_each_ls(l):
    if len(l)==1:
        return l
    retVal = it.product(*l)
    return retVal

# Given a shape, max entry of P, max entry of Q, generate a list of all (not necessarily standard) bitableaux of that shape
# and those max entries
def all_nonstd_bitabs(shape,m,n):
    # find conjugate of shape
    conj = Partition(shape).conjugate() 

    # iterate over each column and get lists of all the SSYT for that column
    colLsP = [[] for elt in conj]
    colLsQ = [[] for elt in conj]
    for i in range(len(conj)):
        colLsP[i] = SemistandardTableaux([1]*conj[i], max_entry=m).list() 
        colLsQ[i] = SemistandardTableaux([1]*conj[i], max_entry=n).list() 

    PIt = pick_one_from_each_ls(colLsP)
    QIt = pick_one_from_each_ls(colLsQ)

    P_tab = [Tableau([[ob[0] for ob in col] for col in elt]).conjugate() for elt in PIt] 
    Q_tab = [Tableau([[ob[0] for ob in col] for col in elt]).conjugate() for elt in QIt] 
    tabs = it.product(P_tab,Q_tab)
    return tabs

# Given a shape and an instance of PolRing, return all standard bitableaux of that shape in that ring
def all_pol_bitabs(shape,R,left_just=False):
    bitabs = all_bitabs(shape,R.m,R.n,left_just=left_just)
    tabs = [poly_bitableau(elt[0],elt[1],R) for elt in bitabs]
    return tabs

# Given a shape and an instance of PolRing, return all bitableaux (not necessarily standard) of that 
# shape in that ring
def all_nonstd_pol_bitabs(shape,R):
    bitabs = all_nonstd_bitabs(shape,R.m,R.n)
    tabs = [poly_bitableau(elt[0],elt[1],R) for elt in bitabs]
    return tabs

'''
HELPER FUNCTIONS
'''
# input: n (sum of elements), k (number of elements)
# output: iterator over weak compositions of n of size k
def compositions(n,k):
  if n < 0 or k < 0:
    return

  if k == 0:
    if n == 0:
      yield ()
    return

  if k == 1:
    yield (n,)
    return

  for i in range(0,n+1):
    for comp in compositions(n-i,k-1):
        yield (i,) + comp

# input: gens = list of np matrices, check_mat
# output: True if there is an element of gens so that check_mat-gen is totally non-negative, false else
def is_nonstd(gens,check_mat):
    if check_mat is None:
        return True
    for gen in gens:
        if np.min(check_mat-gen) >= 0:
            return True
    return False