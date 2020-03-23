#This script has functions needed to make a Cumulative Distribution Plot from
#Different variables output in  PhaseIITreeMaker root file.

import glob

import sys
import uproot
import lib.ROOTProcessor as rp
import lib.EventSelection as es
import lib.AmBePlots as abp
import pandas as pd
import matplotlib.pyplot as plt
import scipy.optimize as scp
import numpy as np

SIGNAL_DIR = "./Data/Pos3P1mData/"
BKG_DIR = "./Data/BkgCentralData/"

expoPFlat= lambda x,C1,tau,mu,B: C1*np.exp(-(x-mu)/tau) + B

def EventSelectionLosses(df):
    print("TOTAL NUMBER OF EVENT TIME TANKS SET: " + str(len(set(df['eventTimeTank']))))
    print("TOTAL NUMBER OF EVENT TIME TANKS, LIST: " + str(len(df['eventTimeTank'])))
    print("TOTAL NUMBER OF ENTRIES: " + str(len(df)))
    
    df_cleanSiPM = es.SingleSiPMPulses(df)
    print("TOTAL NUMBER OF EVENTS W/ ONE PULSE IN EACH SIPM: " + str(len(set(df_cleanSiPM['eventTimeTank']))))

    df_cleanSiPMDT = es.SingleSiPMPulsesDeltaT(df,200) 
    print("TOTAL NUMBER OF EVENTS W/ ONE PULSE IN EACH SIPM, PEAKS WITHIN 200 NS: " + str(len(set(df_cleanSiPMDT['eventTimeTank']))))

    #df_cleanPrompt = es.NoPromptClusters(df_cleanSiPM,2000)
    #print("TOTAL NUMBER OF EVENTS W/ ONE PULSE IN EACH SIPM AND NO PROMPT CLUSTER: " + str(len(set(df_cleanPrompt['eventTimeTank']))))

def PlotDemo(Sdf,Bdf,Sdf_trig,Bdf_trig):
    print("EVENT SELECTION LOSSES FOR CENTRAL SOURCE RUN")
    EventSelectionLosses(Sdf_trig)

    print("EVENT SELECTION LOSSES FOR BKG CENTRAL SOURCE RUN")
    EventSelectionLosses(Bdf)

    Sdf_SinglePulses = es.SingleSiPMPulses(Sdf)
    Bdf_SinglePulses = es.SingleSiPMPulses(Bdf)
    
    labels = {'title': "Amplitude of SiPM1 hits", 'xlabel':'Pulse amplitude [V]','llabel':'SiPM1'}
    ranges = {'bins': 70, 'range':(0,0.05)}
    abp.MakeSiPMVariableDistribution(Sdf_SinglePulses, "SiPMhitAmplitude",1,labels,ranges,True)
    labels = {'title': "Amplitude of SiPM hits (Source)", 'xlabel':'Pulse amplitude [V]','llabel':'SiPM2'}
    abp.MakeSiPMVariableDistribution(Sdf_SinglePulses, "SiPMhitAmplitude",2,labels,ranges,True)
    leg = plt.legend(loc=1,fontsize=24)
    leg.set_frame_on(True)
    leg.draw_frame(True)
    plt.show()

    labels = {'title': "Amplitude of SiPM1 hits (No Source)", 'xlabel':'Pulse amplitude [V]','llabel':'SiPM1'}
    ranges = {'bins': 70, 'range':(0,0.05)}
    abp.MakeSiPMVariableDistribution(Bdf_SinglePulses, "SiPMhitAmplitude",1,labels,ranges,True)
    labels = {'title': "Amplitude of SiPM hits", 'xlabel':'Pulse amplitude [V]','llabel':'SiPM2'}
    abp.MakeSiPMVariableDistribution(Bdf_SinglePulses, "SiPMhitAmplitude",2,labels,ranges,True)
    leg = plt.legend(loc=1,fontsize=24)
    leg.set_frame_on(True)
    leg.draw_frame(True)
    plt.show()


    plt.hist(np.hstack(Sdf_SinglePulses['hitPE']),100,range=(0,10))
    plt.title("PE distribution for hits in source data")
    plt.xlabel("Photoelectrons")
    plt.show()

    plt.hist(Sdf_SinglePulses['clusterTime'],70,label='Source',alpha=0.8)
    plt.hist(Bdf_SinglePulses['clusterTime'],70,label='No source',alpha=0.8)
    plt.xlabel("Cluster time (ns)")
    plt.title("Time distribution of all hit clusters")
    leg = plt.legend(loc=1,fontsize=24)
    leg.set_frame_on(True)
    leg.draw_frame(True)
    plt.show()

    Sdf_CleanPrompt = es.NoPromptClusters(Sdf_SinglePulses,2000)
    Bdf_CleanPrompt = es.NoPromptClusters(Bdf_SinglePulses,2000)
    plt.hist(Sdf_CleanPrompt['clusterTime'],70,label='Source',alpha=0.8)
    plt.hist(Bdf_CleanPrompt['clusterTime'],70,label='No source',alpha=0.8)
    plt.xlabel("Cluster time (ns)")
    plt.title("Time distribution of all hit clusters \n (One pulse in each SiPM, no prompt cluster)")
    leg = plt.legend(loc=1,fontsize=24)
    leg.set_frame_on(True)
    leg.draw_frame(True)
    plt.show()

    plt.hist(Sdf_CleanPrompt['clusterTime'],35,range=(15000,65000),alpha=0.8)
    hist,bin_edges = np.histogram(Sdf_CleanPrompt['clusterTime'],35,range=(15000,65000))
    bin_lefts = bin_edges[0:len(bin_edges)-1]
    print(len(hist))
    print(len(bin_lefts))
    bin_width = bin_lefts[1] - bin_lefts[0]
    bin_centers = bin_lefts + bin_width/2.
    #try making some nice bins
    init_params = [200, 30000,10000,10]
    popt, pcov = scp.curve_fit(expoPFlat, bin_centers,hist,p0=init_params, maxfev=6000)
    print("WE HERE")
    print(popt)
    print(pcov)
    myy = expoPFlat(bin_centers,popt[0],popt[1],popt[2],popt[3])
    myy_line = np.ones(len(bin_centers))*popt[3]
    tau_mean = int(popt[1]/1000)
    tau_unc = int(np.sqrt(pcov[1][1])/1000)
    plt.plot(bin_centers,myy,marker='None',linewidth=6,label=r'Best total fit $\tau = %i\pm%i \mu s$'%(tau_mean,tau_unc),color='black')
    plt.plot(bin_centers,myy_line,marker='None',linewidth=6,label=r'Flat bkg. fit',color='gray')
    plt.xlabel("Cluster time (ns)")
    plt.title("Time distribution of delayed hit clusters \n (One pulse in each SiPM, no prompt cluster)")
    leg = plt.legend(loc=1,fontsize=24)
    leg.set_frame_on(True)
    leg.draw_frame(True)
    plt.show()

    #CleanEventNumbers = Sdf_CleanPrompt["eventNumber"]
    #Return DF with triggers that have no prompt and one of each SiPM pulse
    Sdf_trig_goodSiPM = Sdf_trig.loc[(Sdf_trig['SiPM1NPulses']==1) & (Sdf_trig['SiPM2NPulses']==1)].reset_index(drop=True)
    Sdf_trig_CleanPrompt = es.NoPromptClusters_WholeFile(Sdf_SinglePulses,Sdf_trig_goodSiPM,2000)
    MSData = abp.MakeClusterMultiplicityPlot(Sdf_CleanPrompt,Sdf_trig_CleanPrompt)
    print("NUMBER OF TRIGS: " + str(len(MSData)))
    print("NUMBER OF ZERO MULTIPLICITY TRIGS: " + str(len(np.where(MSData==0)[0])))
    plt.hist(MSData,bins=20, range=(0,20), label="Source",alpha=0.7)
    plt.xlabel("Delayed cluster multiplicity")
    plt.title("Cluster multiplicity for delayed window of central source run \n (One pulse each SiPM, no prompt cluster)")
    leg = plt.legend(loc=1,fontsize=24)
    leg.set_frame_on(True)
    leg.draw_frame(True)
    plt.show()

    plt.hist(Bdf_SinglePulses['clusterTime'],100,label='No source', color='purple',alpha=0.7)
    plt.xlabel("Cluster time (ns)")
    plt.axvline(x=20000,color='black',linewidth=6)
    plt.axvline(x=65000,color='black',linewidth=6)
    plt.title("Region to characterize flat background distribution \n (No source data, one pulse in each SiPM)")
    leg = plt.legend(loc=1,fontsize=24)
    leg.set_frame_on(True)
    leg.draw_frame(True)
    plt.show()

    plt.hist(MSData,bins=20, range=(0,20), label="Source",alpha=0.7)
    Bdf_latewindow = Bdf_SinglePulses.loc[(Bdf_SinglePulses['clusterTime']>20000)].reset_index(drop=True)
    Bdf_trig_goodSiPM = Bdf_trig.loc[(Bdf_trig['SiPM1NPulses']==1) & (Bdf_trig['SiPM2NPulses']==1)].reset_index(drop=True)
    #Bdf_trig_bkgclean = es.FilterByEventNumber(Bdf_trig,CleanBkgNumbers)
    #Get cluster multiplicity of late window in events passing prompt criteria
    MBData = abp.MakeClusterMultiplicityPlot(Bdf_latewindow,Bdf_trig_goodSiPM)
    print("NUMBER OF TRIGS: " + str(len(MBData)))
    print("NUMBER OF ZERO MULTIPLICITY TRIGS (LATE WINDOW): " + str(len(np.where(MBData==0)[0])))
    plt.hist(MBData,bins=20, range=(0,20), label="No source",alpha=0.7)
    plt.xlabel("Delayed cluster multiplicity")
    plt.title("Cluster multiplicity for delayed window of central source run \n (One pulse each SiPM, no prompt cluster)")
    leg = plt.legend(loc=1,fontsize=24)
    leg.set_frame_on(True)
    leg.draw_frame(True)
    plt.show()

    #Plotting the PE distribution
    plt.hist(Sdf_CleanPrompt['clusterPE'],bins=70,range=(0,150),label='Source, >2 $\mu$s',alpha=0.8)

    plt.hist(Bdf_latewindow["clusterPE"],bins=70,range=(0,150),label='No source, >20 $\mu$s',alpha=0.8)
    plt.xlabel("PE")
    plt.title("PE distribution for delayed clusters")
    leg = plt.legend(loc=1,fontsize=24)
    leg.set_frame_on(True)
    leg.draw_frame(True)
    plt.show()

    #Plotting the PE distribution
    Bdf_latewindow_CBClean = Bdf_latewindow.loc[Bdf_latewindow['clusterChargeBalance']<0.4]
    Sdf_CleanPrompt_CBClean = Sdf_CleanPrompt.loc[Sdf_CleanPrompt['clusterChargeBalance']<0.4]
    plt.hist(Sdf_CleanPrompt_CBClean['clusterPE'],bins=70,range=(0,150),label='Source, >2 $\mu$s',alpha=0.8)

    plt.hist(Bdf_latewindow_CBClean["clusterPE"],bins=70,range=(0,150),label='No source, >20 $\mu$s',alpha=0.8)
    plt.xlabel("PE")
    plt.title("PE distribution for delayed clusters (Charge balance < 0.4)")
    leg = plt.legend(loc=1,fontsize=24)
    leg.set_frame_on(True)
    leg.draw_frame(True)
    plt.show()


    labels = {'title': 'Comparison of total PE to charge balance parameter (Source)', 
            'xlabel': 'Total PE', 'ylabel': 'Charge balance parameter'}
    ranges = {'xbins': 100, 'ybins':100, 'xrange':[0,150],'yrange':[0,1]}
    #abp.MakeHexJointPlot(Sdf,'clusterPE','clusterChargeBalance',labels,ranges)
    abp.Make2DHist(Sdf_CleanPrompt,'clusterPE','clusterChargeBalance',labels,ranges)
    abp.ShowPlot()

    labels = {'title': 'Comparison of total PE to charge balance parameter (No source, >20 $\mu$s)', 
            'xlabel': 'Total PE', 'ylabel': 'Charge balance parameter'}
    ranges = {'xbins': 50, 'ybins':50, 'xrange':[0,150],'yrange':[0,1]}
    #abp.MakeHexJointPlot(Sdf,'clusterPE','clusterChargeBalance',labels,ranges)
    Bdf_latewindow = Bdf.loc[Bdf['clusterTime']>20000]
    abp.Make2DHist(Bdf_latewindow,'clusterPE','clusterChargeBalance',labels,ranges)
    abp.ShowPlot()

    labels = {'title': 'Comparison of total PE to charge balance parameter', 
            'xlabel': 'Total PE', 'ylabel': 'Charge balance parameter','llabel':'No source',
            'color':'Reds'}
    ranges = {'xbins': 50, 'ybins':50, 'xrange':[0,150],'yrange':[0,1]}
    #abp.MakeHexJointPlot(Sdf,'clusterPE','clusterChargeBalance',labels,ranges)

    Bdf_window = Bdf_latewindow.loc[(Bdf_latewindow['clusterPE']<150) & \
            (Bdf_latewindow['clusterChargeBalance']>0) & (Bdf_latewindow['clusterChargeBalance']<1)]
    Sdf_window = Sdf_CleanPrompt.loc[(Sdf_CleanPrompt['clusterPE']<150) & \
            (Sdf_CleanPrompt['clusterChargeBalance']>0) & (Sdf_CleanPrompt['clusterChargeBalance']<1)]
    abp.MakeKDEPlot(Bdf_window,'clusterPE','clusterChargeBalance',labels,ranges)
    labels = {'title': 'Comparison of total PE to charge balance parameter', 
            'xlabel': 'Total PE', 'ylabel': 'Charge balance parameter','llabel':'No source',
            'color':'Blues'}
    abp.MakeKDEPlot(Sdf_window,'clusterPE','clusterChargeBalance',labels,ranges)
    abp.ShowPlot()

    labels = {'title': 'Comparison of total PE to max PE (Source)', 
            'xlabel': 'Total PE', 'ylabel': 'Max PE'}
    ranges = {'xbins': 40, 'ybins':40, 'xrange':[0,60],'yrange':[0,15]}
    #abp.MakeHexJointPlot(Sdf,'clusterPE','clusterChargeBalance',labels,ranges)
    abp.Make2DHist(Sdf_CleanPrompt,'clusterPE','clusterMaxPE',labels,ranges)
    abp.ShowPlot()

    labels = {'title': 'Comparison of total PE to max PE (No source, >20 $\mu$s)', 
            'xlabel': 'Total PE', 'ylabel': 'Max PE'}
    ranges = {'xbins': 40, 'ybins':40, 'xrange':[0,60],'yrange':[0,15]}
    #abp.MakeHexJointPlot(Sdf,'clusterPE','clusterChargeBalance',labels,ranges)
    Bdf_latewindow = Bdf.loc[Bdf['clusterTime']>20000]
    abp.Make2DHist(Bdf_latewindow,'clusterPE','clusterMaxPE',labels,ranges)
    abp.ShowPlot()

    labels = {'title': 'Comparison of total PE to Charge Point Y-component (Sourcej)', 
            'xlabel': 'Total PE', 'ylabel': 'Charge Point Y'}
    ranges = {'xbins': 30, 'ybins':30, 'xrange':[0,60],'yrange':[-1,1]}
    #abp.MakeHexJointPlot(Sdf,'clusterPE','clusterChargeBalance',labels,ranges)
    abp.Make2DHist(Sdf_CleanPrompt,'clusterPE','clusterChargePointY',labels,ranges)
    abp.ShowPlot()

    labels = {'title': 'Comparison of total PE to Charge Point Y-component (No source, >20 $\mu$s)', 
            'xlabel': 'Total PE', 'ylabel': 'Charge Point Y'}
    ranges = {'xbins': 30, 'ybins':30, 'xrange':[0,60],'yrange':[-1,1]}
    #abp.MakeHexJointPlot(Sdf,'clusterPE','clusterChargeBalance',labels,ranges)
    abp.Make2DHist(Bdf_latewindow,'clusterPE','clusterChargePointY',labels,ranges)
    abp.ShowPlot()


    Bdf_latewindow_CBCut = Bdf_latewindow.loc[Bdf_latewindow['clusterChargeBalance']>0.4]
    labels = {'title': 'Comparison of total PE to Charge Point Y-component (No source, >20 $\mu$s, Charge Balance > 0.4)', 
            'xlabel': 'Total PE', 'ylabel': 'Charge Point Y'}
    ranges = {'xbins': 30, 'ybins':30, 'xrange':[0,60],'yrange':[-1,1]}
    #abp.MakeHexJointPlot(Sdf,'clusterPE','clusterChargeBalance',labels,ranges)
    abp.Make2DHist(Bdf_latewindow_CBCut,'clusterPE','clusterChargePointY',labels,ranges)
    abp.ShowPlot()



if __name__=='__main__':
    slist = glob.glob(SIGNAL_DIR+"*.ntuple.root")
    blist = glob.glob(BKG_DIR+"*.ntuple.root")

    livetime_estimate = abp.EstimateLivetime(slist)
    print("SIGNAL LIVETIME ESTIMATE IN SECONDS IS: " + str(livetime_estimate))
    livetime_estimate = abp.EstimateLivetime(blist)
    print("BKG LIVETIME ESTIMATE IN SECONDS IS: " + str(livetime_estimate))

    mybranches = ['eventNumber','eventTimeTank','clusterTime','SiPMhitQ','SiPMNum','SiPMhitT','hitT','hitQ','hitPE','SiPMhitAmplitude','clusterChargeBalance','clusterPE','clusterMaxPE','SiPM1NPulses','SiPM2NPulses','clusterChargePointY']
    SProcessor = rp.ROOTProcessor(treename="phaseIITankClusterTree")
    for f1 in slist:
        SProcessor.addROOTFile(f1,branches_to_get=mybranches)
    Sdata = SProcessor.getProcessedData()
    Sdf = pd.DataFrame(Sdata)

    BProcessor = rp.ROOTProcessor(treename="phaseIITankClusterTree")
    for f1 in blist:
        BProcessor.addROOTFile(f1,branches_to_get=mybranches)
    Bdata = BProcessor.getProcessedData()
    Bdf = pd.DataFrame(Bdata)

    SProcessor = rp.ROOTProcessor(treename="phaseIITriggerTree")
    for f1 in slist:
        SProcessor.addROOTFile(f1,branches_to_get=mybranches)
    Sdata = SProcessor.getProcessedData()
    Sdf_trig = pd.DataFrame(Sdata)

    BProcessor = rp.ROOTProcessor(treename="phaseIITriggerTree")
    for f1 in blist:
        BProcessor.addROOTFile(f1,branches_to_get=mybranches)
    Bdata = BProcessor.getProcessedData()
    Bdf_trig = pd.DataFrame(Bdata)
    PlotDemo(Sdf,Bdf,Sdf_trig,Bdf_trig)


