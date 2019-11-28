import numpy as np
from numpy import genfromtxt
import pandas as pd
from random import randrange
from scipy import stats
import seaborn as sns
import matplotlib.pyplot as plt

def diagSU(su):
    '''

    :param su: sum of U_0 columns
    :return: diagonal matrix
    '''
    Uzero = []
    for j in range(0, len(su)):
        Uzero.append([0] * len(su))

    for j in range(0, len(su)):
        Uzero[j][j] = 1 / su[j]

    return Uzero

def diagonalize(su):
    '''

    :param su: diagonal of a matrix
    :return: diagonal matrix
    '''

    Uzero = []
    for j in range(0, len(su)):
        Uzero.append([0] * len(su))

    for j in range(0, len(su)):
        Uzero[j][j] = su[j]
    Uzero = pd.DataFrame(Uzero)
    return Uzero


def randPU_wrong2(n, K):
    # all 0 matrix
    Uzero = []
    for k in range(0, n):
        Uzero.append([1] * K)

    return Uzero


def mse(Xrow, Xmean0row1):
    min_dif = 0
    for r in range(0, len(Xrow)):
        min_dif += (Xrow[r] - Xmean0row1[r]) ** 2

    MSE = min_dif / len(Xrow)
    return MSE


def mse2(Xrow, Xmean0row1):
    min_dif = 0
    for r in range(0, len(Xrow)):
        min_dif += (Xrow[r] - Xmean0row1[r]) ** 2

    MSE = min_dif / len(Xrow)
    return MSE


def costf(X, Xmean_ott, U):
    cost = 0
    for i in range(0, len(X)):
        for j in range(0, len(U.iloc[0])):
            if U.iloc[i, j] == 1:
                cost += mse(X.iloc[i], Xmean_ott.iloc[j])
    return cost


def kmeans_wrong(X, K, Rndstart):
    '''

    :param X: data Matrix
    :param K: Number of cluster of the partition
    :param Rndstart: number of random start
    :return:
    '''

    maxiter = 100
    n = len(X)
    j = len(X.iloc[0])
    epsilon = 0.00001

    # find the best solution in a fixed number of random start partitions
    for loop in range(0, Rndstart):

        # initial WRONG partition U_0 is given

        U_0 = pd.DataFrame(randPU_wrong2(n, K))

        # column frequency = random cluster
        sum_col = []
        for r in range(0, K):
            sum_col.append(sum(U_0[r]))

        # 1/su on diagonal of a NxN matrix
        su_diag = diagSU(sum_col)

        # given U compute Xmean (centroids)
        Ut = U_0.transpose()
        dot1 = pd.DataFrame(np.dot(su_diag, Ut))

        Xmean0 = round(pd.DataFrame(np.dot(dot1, X)), 4)

        for iter in range(1, maxiter):
            # given Xmean = assign each units to the closest cluster
            U = []
            for r in range(0, n):
                U.append([0] * K)

            for r in range(0, n):

                min_dif = mse(X.iloc[r], Xmean0.iloc[0])

                posmin = 0
                for j in range(1, K):

                    dif = mse(X.iloc[r], Xmean0.iloc[j])
                    if dif < min_dif:
                        min_dif = dif
                        posmin = j
                U[r][posmin] = 1

            U = pd.DataFrame(U)

            # given a partition of units, so given U compute Xmean (centroids)

            # update sum_col
            sum_col = []
            for t in range(0, K):
                sum_col.append(sum(U[t]))

            ## RARE CASE (BUT POSSIBLE) #############################################################
            # if there is some empty cluster we must split the cluster with max sum_col
            while sum([sum_col[h] == 0 for h in range(0, len(sum_col))]) > 0:  # some cluster is empty

                p1 = min(sum_col)
                p2 = max(sum_col)

                # select min column (empty cluster)
                for j in range(0, len(sum_col)):
                    if p1 == sum_col[j]:
                        c1 = j

                # select max column (cluster) for split its points to empty cluster
                for k in range(0, len(sum_col)):
                    if p2 == sum_col[k]:
                        c2 = k

                # list of units in max column (cluster)
                ind = []
                for row in range(0, len(U)):
                    if int(U.iloc[row, c2]) == 1:
                        ind.append(row)

                # split max cluster
                ind2 = []
                for row in range(0, p2 // 2):
                    ind2.append(row)

                for row in range(0, len(ind2)):
                    U.iloc[row, c1] = 1
                    U.iloc[row, c2] = 0

                sum_col = []
                for q in range(0, K):
                    sum_col.append(sum(U[q]))
            #################################################################################################

            # give U compute centroids
            _U = U.transpose()
            _dot1 = pd.DataFrame(np.dot(diagSU(sum_col), _U))
            Xmean = round(pd.DataFrame(np.dot(dot1, X)), 4)

            # compute ojective function
            BB = (np.dot(U, Xmean)) - X
            f = round(np.trace(np.dot(BB.transpose(), BB)), 4)

            # stopping rule
            dif = 0

            for k in range(0, K):
                dif += mse2(Xmean.iloc[k], Xmean0.iloc[k])

            if dif > epsilon:
                Xmean0 = Xmean
            else:
                break

        if loop == 0:
            U_ott = U
            f_ott = f
            Xmean_ott = Xmean

        if f < f_ott:
            U_ott = U
            f_ott = f
            Xmean_ott = Xmean

    # calculate cost
    cost = costf(X, Xmean_ott, U_ott)
    print('Done')
    return round(pd.DataFrame(U_ott), 4), f_ott, cost


def dwdb(data, U, Xm, K):

    u = pd.DataFrame([1] * len(data))
    _u = u.transpose()
    _dot1 = pd.DataFrame(np.dot(u, _u))
    mat = round(pd.DataFrame(np.dot(1 / len(data), _dot1)), 4)
    # centrature matrix
    Jc = pd.DataFrame(np.identity(len(data)) - mat)

    data_c = round(pd.DataFrame(np.dot(Jc, data)), 4)
    _Xm = round(pd.DataFrame(np.dot(pd.DataFrame(np.linalg.pinv(U.values)), data)), 4)

    #WITHIN
    p = data_c - np.dot(U, _Xm)
    D_w = np.trace(np.dot(p.transpose(), p))

    #BETWEEN
    b = np.dot(U, _Xm)
    D_b = np.trace(np.dot(b.transpose(), b))

    return (D_b/(K-1))/(D_w/(len(data)-K))


def standardizeDataFrame(data):
    u = pd.DataFrame([1]*len(data))
    _u = u.transpose()
    _dot1 = pd.DataFrame(np.dot(u, _u))
    mat = round(pd.DataFrame(np.dot(1/len(data), _dot1)), 4)
    #centrature matrix
    Jc = np.identity(len(data)) - mat
    dot_data = pd.DataFrame(np.dot(Jc, data))
    dot_data2 = np.dot(dot_data.transpose(), dot_data)
    s_data = round(pd.DataFrame(np.dot(1/len(data), dot_data2)), 4)

    diagonal = np.array(np.diag(s_data))
    d2 = diagonalize(diagonal)**0.5
    d2_inv = pd.DataFrame(np.linalg.pinv(d2.values)) #pseudo inverse

    dot1 = pd.DataFrame(np.dot(data, d2_inv))
    stand = round(pd.DataFrame(np.dot(Jc, dot1)), 4)
    return stand


if __name__ == "__main__":
    data = pd.DataFrame(genfromtxt(r'C:\Users\aless\Desktop\data\wine.data', delimiter=','))
    data = data.drop(data.columns[[0]], axis='columns')

    # #### datacolumns
    data.columns = [

        'Alcohol',
        'Malic acid',
        'Ash',
        'Alcalinity_of_ash',
        'Magnesium',
        'Total_phenols',
        'Flavanoids',
        'Nonflavanoid_phenols',
        'Proanthocyanins',
        'Color_intensity',
        'Hue',
        'OD280/OD315_of_diluted_wines',
        'Proline']
    # standardize DataFrame
    dataS = standardizeDataFrame(data)

kluster = kmeans_wrong(dataS, 3, 1)
print('Our objective function has value: ', kluster[2])


