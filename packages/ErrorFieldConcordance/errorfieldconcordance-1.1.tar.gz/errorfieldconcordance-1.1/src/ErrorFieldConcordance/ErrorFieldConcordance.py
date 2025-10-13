# -*- coding: utf-8 -*-
"""
@author: Joe Rinehart
@contributors: Bernd Saugel
     Sean Coekelenbergh
     Ishita Srivastava
     Brandon Woo


"""
import numpy as np
import math
from matplotlib import pyplot as plt
import pandas as pd


def calc_distance_from_line_to_point(line_slope,line_y_intercept,
                                      point_x,point_y):

    if (line_slope==0):
        return abs(line_y_intercept - point_y)

    # Ready to go back to high-school algebra, kids?  (maybe grade school?)
    # Get the inverse slope for the perpendicular from the point to the line
    m2 = -1/line_slope

    # now find the y-intercept of line 2
    # y = mx + b --> b = y - mx
    b2 = point_y - m2*point_x

    # At the intersection of these lines, y1==y2, and x1==x2 so...
    # m*x + b == m2*x + b2
    # Rearrange
    # x = (b2-b)/(_m-_m2)
    xi = (b2-line_y_intercept) / (line_slope - m2)
    # And the y-value of the intersection is
    yi = m2*xi + b2
    # now calculate the len of the line from (i,beat[i]) to xi,yi
    D = np.sqrt((xi - point_x)*(xi - point_x) + \
                 (yi - point_y)*(yi - point_y))
    return D


def ErrorFieldConcordance(X,Y,IDS=[],
                          plot_TF=False,
                          graph_label="",
                          X_name="ΔCOa (Lpm)",
                          Y_name="ΔCOb (Lpm)",
                          min_plot_range=3,
                          decolor_threshold=2,
                          silent=False,
                          weight_histogram = True,
                          print_weight_table = True,
                          save_plot_as=""):

    if (len(X) != len(Y)):
        if (not silent):
            print ("ErrorFieldConcordance: Reference and Test values must have" +\
                   " the same number of observations.")
        return (np.nan,np.nan)
    if (len(X)<2):
        if (not silent):
            print ("ErrorFieldConcordance: Must have at least two observations" +\
                   " per group")
        return (np.nan,np.nan)

    if (len(IDS) == 0):
        IDS = [1] * len(X)
    elif (len(IDS) != len(Y)):
        if (not silent):
            print ("ErrorFieldConcordance: Length of subject IDs does not "+\
                   "match length of observations")
        return (np.nan,np.nan)

    tabrows = []

    # Calculate changes
    DX = []
    DY = []
    for i in range(1,len(X)):
        if (IDS[i-1] == IDS[i]):
            DX.append(X[i] - X[i-1])
            DY.append(Y[i] - Y[i-1])

    if (len(DX) == 0):
        if (not silent):
            print ("ErrorFieldConcordance: No matching subject IDs found;" +\
                   "not possible to calculate any changes.  Check to be sure " +\
                    "subject observations are grouped together and in temporal " +\
                    "order in the lists")
        return (np.nan,np.nan)

    plotcols = []
    TotalWeight = 0
    TotalScore = 0
    ScoreArray = []
    WeightArray = []

    for i in range(len(DX)):
        # Point weight is the distance from the plotted point
        # to the origin (0,0).  This is the hypotenuse of the triangle
        # formed by sides of the lengths DX and DY.
        Hypot = np.hypot(DX[i],DY[i])


        # Calculate the Angle (a) that a line from the origin makes to
        # this point.  Sin (theta) = opp/hypot
        Angle = np.arctan((DY[i])/DX[i])
        Angle = math.degrees(Angle)
        # 'Score' the Agreement: angle <15 full credit (1 pt)
        #                        angle >75 full negative credit (-1 pt)
        #                        graded between 15 & 75
        # First Correct the angle - perfect is 45 degree line
        Angle -= 45
        if (Angle < -90):
            Angle += 180

        # Now calculate the score based on the angle and prepare graphing
        Score = 0
        # Yellow color is (1.0, 0.84, 0)
        #Score = 1 - (2*(abs(Angle) - 15)/60)  # Total range is (75-15)=60
        Score = abs((90-abs(Angle))/45) - 1

        newcol = []
        # Graph Colors (complex shade gradient - this math leads to
        # appropriate boundary transitions by visual appearance)
        thresh = 0.2
        if(Score > thresh):
            s = (Score-thresh)
            newcol = [1-s,0.84-(0.84*s),s]
        elif(Score < -thresh):
            s = (abs(Score)-thresh)
            newcol = [1, 0.84-(0.84*s),0]
            #print (plotcols[-1])
        else:
            #yellow
            newcol = [1.0, 0.84, 0]

        # Now modify the colors by the weight
        if (decolor_threshold > 0):
            if (Hypot < decolor_threshold):
                desat = 1-pow(1-(decolor_threshold-Hypot)/decolor_threshold,2)
                for j in [0,1,2]:
                    k = newcol[j]
                    diff = 0.85 - k
                    mod = diff * desat
                    newcol[j] += mod

        plotcols.append((newcol[0],newcol[1],newcol[2]))

        # now do the tally
        TotalWeight += Hypot
        TotalScore += Hypot * Score
        ScoreArray.append((Hypot * Score)/Hypot)
        WeightArray.append(Hypot)

        tabrows.append([DX[i],DY[i],Hypot,Score])

    # concordance
    conc = np.round(100*TotalScore/TotalWeight,1)

    # weighted standard deviation
    SD = np.round(100*np.sqrt(np.cov(ScoreArray, aweights=WeightArray)),1)


    #  plot
    if (plot_TF) or (save_plot_as != ""):
        plt.rcParams.update({'font.size': 14})

        mX = max([abs(ele) for ele in DX])
        mY = max([abs(ele) for ele in DY])
        LIM = max(mX,mY) * 1.05
        LIM = max(LIM,min_plot_range)

        plt.figure(figsize=(6,6))

        plt.ylim(-LIM,LIM)
        plt.xlim(-LIM,LIM)

        gtitle = "Error Field Concordance = "+str(conc)+"±"+str(SD)+"%"
        if (graph_label != ""):
            gtitle = graph_label+"\n"+gtitle;

        plt.plot([-LIM,LIM],[-LIM,LIM],color="lightgray",zorder=10)
        plt.plot([0,0],[0.2,-0.2],color="lightgray",zorder=10)
        plt.plot([0.2,-0.2],[0,0],color="lightgray",zorder=10)
        plt.title(gtitle)
        if (X_name != ""):
            plt.xlabel(str(X_name))
        if (Y_name != ""):
            plt.ylabel(str(Y_name))

        for k in range(len(DX)):
            plt.scatter(DX[k],DY[k],alpha=min(1,600/len(DX)),
                        color=plotcols[k])

        #plt.text(-4,4,"Conc: "+str(conc))
        #plt.text(-4,3.5,"B/Y/R: ["+str(_b)+","+str(_y)+","+str(_r)+"]")
        #plt.text(-4,3,"Tot : "+str(len(DX)))

        if (save_plot_as != ""):
            if (save_plot_as[-4:].lower() != ".png"):
                save_plot_as += ".png"
            plt.savefig(save_plot_as,dpi=300)

        if (plot_TF):
            plt.show()

        if (weight_histogram):
            plt.figure()
            plt.hist(WeightArray,bins=30)
            plt.title("Histogram of Calculated Weights")
            plt.xlabel("Weight")
            plt.ylabel("Count")
            plt.show()

    if (not silent):
        WeightArray.sort(reverse=True)
        if (WeightArray[min(2,len(WeightArray)-1)] < 0.75):
            print ("ErrorFieldConcordance: Observed changes in data "\
                   +"are small and may be heavily affected by noise in measurement.")

        if (print_weight_table):
            tabrows = pd.DataFrame(tabrows,columns=["ΔX","ΔY","Weight","Score"])
            print ("-------------------------------------")
            print ("Error Field Concordance Weights Table")
            print ("-------------------------------------")
            print (tabrows.to_string())
            print ("-------------------------------------")

    return (conc,SD)

if __name__ == "__main__":

    print ("Creating Random Data Sample Plot")

    X = np.random.random_sample(100)*5+2
    Y = np.random.random_sample(100)*5+2

    IDS = [1] * len(X)

    C = ErrorFieldConcordance(X,Y,IDS,True,"",
                              decolor_threshold = 1,
                              min_plot_range=4)
    print ("Error Field Concordance (-100% to +100%): "+str(C[0])+" ± "+str(C[1])+"%")
