import matplotlib.pyplot as plt
import numpy as np
import os
import Energy as energy

def readROEs(resultsfile,nQ):
    '''
    Return list of roe upper bounds from results file.

    :param resultsfile: Name of results file.
    :type resultsfile: str
    :param nQ: Number of qubits.
    :type nQ: int

    :return: List of roe upper bounds.
    :rtype: listof float
    '''

    # Open datafile and skip first 8 lines
    results = open(resultsfile)
    for i in range(8):
        line = results.readline()

    # Store roe upper bounds
    roes = []
    while line != "":
        if nQ == 10:
            roe = float(line.split(" ")[15])
        else:
            roe = float(line.split(" ")[11])
        roes.append(roe)
        line = results.readline()
    results.close()

    return roes

def plotScaling(listQ,models,study,tol,pat,reqs,labels,fit = False):
    '''
    Plot scaling of number of hidden units or number of samples
    versus system size for various thresholds on the ROE upper bound.

    :param listQ: List of system sizes to check.
    :type listQ: listof int
    :param study: Type of study.
    :type study: anyof "Nh" "M"
    :param tol: Tolerance.
    :type tol: float
    :param pat: Patience.
    :type pat: int
    :params reqs: List of thresholds to consider.
    :type req: listof float

    :returns: None
    '''

    for i in range(len(reqs)):
        for m in range(len(models)):

            vals = []
            counter = 0
            passed = False
            for nQ in listQ:
                vals.append([])
                Nfolder = "Data/{0}/{1}Study/Q{2}".format(models[m],study,nQ)
                seeds = [name for name in os.listdir(Nfolder)]
                for seed in seeds:
                    folder = Nfolder + "/{0}".format(seed)
                    trials = [name for name in os.listdir(folder)]
                    trialsAlphaNum = {}
                    for j in range(len(trials)):
                        if study == "Nh" and len(trials[j]) == 3:
                            trialsAlphaNum["Nh0" + trials[j][-1]] = j
                        elif study == "M" and len(trials[j]) == 5:
                            trialsAlphaNum["M0" + trials[j][1:]] = j
                        else:
                            trialsAlphaNum[trials[j]] = j

                    for trial in sorted(trialsAlphaNum):
                        tfile = trials[trialsAlphaNum[trial]]
                        rp = folder + "/" + tfile + "/" + "Results.txt"
                        roes = readROEs(rp,nQ)
                        result = energy.earlyStopping(roes,tol,pat,reqs[i])
                        if result != False:
                            if result[-2] == "!":
                                vals[counter].append(int(trial[len(study):]))
                                passed = True
                                break

                    if not passed:
                        vals[counter].append(100000)
                    passed = False
                counter += 1

            vals = np.array(vals)
            valsM = np.min(vals,axis = 1)
            colours = ["b","g","r","c","m"]
            if fit:
                slope,intercept = np.polyfit(listQ,valsM,1)
                lineValues = [slope * k + intercept for k in listQ]
                plt.plot(listQ,valsM,"o",label = labels[m],color = colours[m])
                plt.plot(listQ,lineValues,color = colours[m])
            else:
                plt.plot(listQ,valsM,"-o",label = req)

    plt.xlabel("$N$")
    if study == "Nh":
        plt.ylabel("$N_{h}$")
        title = r"Min $N_{h}$ for various ROE Bounds"
        title += " with 99% CI (Across {0} Trials)".format(len(seeds))
    elif study == "M":
        plt.ylabel("$M$")
        title = r"Min $M$ for various ROE Bounds"
        title += " with 99% CI (Across {0} Trials)".format(len(seeds))
    
    # plt.title(title)
    plt.legend()
    plt.savefig("Scaling",dpi = 200)

def illustrateScaling():

    nh = list(range(5,11))
    roes = [0.02965658,0.02172137,0.01319593,0.00765384,0.00602224,0.00195432]

    plt.plot(nh,roes,"bo")
    plt.axhline(0.002,linestyle = "--",color = "r")
    plt.xlabel(r"$N_{h}$")
    plt.ylabel(r"$\epsilon_{ub}$")
    plt.show()

plotScaling(listQ = list(range(10,101,10)),
            models = ["TFIM1D","TFIM1D5p0"],
            study = "Nh",
            tol = 0.0005,
            pat = 50,
            reqs = [0.002],
            labels = ["h/J = 1","h/J = 5"],
            fit = True)