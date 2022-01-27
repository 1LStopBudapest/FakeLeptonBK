import os, sys
import ROOT



sys.path.append('../')
from Sample.SampleChain import SampleChain
from Sample.Dir import *
from Helper.PlotHelper import *

def get_parser():
    ''' Argument parser.                                                                                                                                                 
    '''
    import argparse
    argParser = argparse.ArgumentParser(description = "Argument parser")
    argParser.add_argument(
    '-l', '--samplelist',  # either of this switches
    nargs='+',       # one or more parameters to this switch
    type=str,        # /parameters/ are ints
    dest='alist',     # store in 'list'.
    default=['TTSingleLep_pow', 'TTLep_pow', 'WJetsToLNu_comb', 'QCD', 'DoubleMuon_Data'],      #last sample should be data.
    )
    argParser.add_argument(
        '-c', '--channel',           action='store',                    type=str,            default='Muon',
    )
    return argParser

options = get_parser().parse_args()

samplelists = options.alist
channel = options.channel

lepOpt = 'Ele' if 'Electron' in channel else 'Mu'

files = []
dofit = True

for sl in samplelists:
    if os.path.exists('mTHist_'+lepOpt+'_'+sl+'.root'):
        files.append(ROOT.TFile.Open('mTHist_'+lepOpt+'_'+sl+'.root'))
    elif os.path.exists(plotDir+'FRmTHistFiles/mTHist_'+lepOpt+'_'+sl+'.root'):
        files.append(ROOT.TFile.Open(plotDir+'FRmTHistFiles/mTHist_'+lepOpt+'_'+sl+'.root'))
    else:
        dofit = False        
        print 'Root files for',lepOpt,'channel and for',sl,'sample does not exist. Please run python mTHistMaker.py --sample',sl,'--channel',lepOpt

if dofit:
    #StackHists(files, samplelists, 'MT', plotDir, 'FRmTHistFiles', scaleOption='AreaScaling')
    #StackHists(files, samplelists, 'MT', plotDir, 'FRmTHistFiles')

    hs=[]
    for i, f in enumerate(files,0):
        hs.append(f.Get('MT_'+samplelists[i]))
    hs_MC = hs[:-1]
    h_data = hs[-1].Clone("Data")
    h_QCD = hs_MC[-1].Clone("QCDMC")#first element is QCD and last one is data
    h_EWK = hs_MC[0].Clone("EWKMC")
    for i, h in enumerate(hs_MC, 0):
        if i==0: continue
        if i!=len(hs_MC)-1:
            h_EWK.Add(h)

    #caculate scale
    '''
    i_low = h_data.GetXaxis().FindBin(80)
    i_up  = h_data.GetXaxis().FindBin(100)
    I_data = h_data.Integral(i_low,i_up)
    I_QCD = h_QCD.Integral(i_low,i_up)
    I_EWK = h_EWK.Integral(i_low,i_up)
        
    I_data = h_data.Integral()
    I_QCD = h_QCD.Integral()
    I_EWK = h_EWK.Integral()
    I_scale = I_data / (I_QCD + I_EWK)
    h_QCD.Scale(I_scale)
    h_EWK.Scale(I_scale)
    '''
               
    #Template Fit
    mc = ROOT.TObjArray(2)
    mc.Add(h_QCD)
    mc.Add(h_EWK)
    templateFit = ROOT.TFractionFitter(h_data, mc)
    for i in xrange(2):
        templateFit.Constrain(i,0.0,1.0)
    templateFit.SetRangeX(60,100)
    ROOT.SetOwnership( templateFit, False )
    status = templateFit.Fit()
    
    if int(status) != 0:
        print 'TFraction fit failed!!  aborting'
        exit(0)
    h_fittedMC = templateFit.GetPlot()
    QCD_sf = templateFit.GetMCPrediction(0)
    EWK_sf = templateFit.GetMCPrediction(1)    

    #Making some plots
    outputDir = os.getcwd()
    #Plot1D(h_QCD, outputDir, islogy=True)
    #Plot1D(h_EWK, outputDir, islogy=True)
    #Plot1D(h_data, outputDir, islogy=True)
    #print 'qcd: ', h_QCD.Integral(),' ewk: ', h_EWK.Integral(),' totMC: ',h_QCD.Integral()+h_EWK.Integral(),' data: ',h_data.Integral()
    #Plot1D(EWK_sf, outputDir, islogy=True)
    #Plot1D(h_fittedMC, outputDir, islogy=True)
    #CompareHist(h_data, h_fittedMC, 'dataMC', outputDir, islogy=True, scaleOption='noscale')
    #CompareHist(h_EWK, EWK_sf, 'sf', outputDir, islogy=True, scaleOption='noscale')

    #Storing the EWK norm factor
    f_sf = open('%sEWKNormFactor.txt'%Xfiles, 'w')#storing this file in 1LStopBudapest/AuxFiles/ for future use
    sf = EWK_sf.Integral()/h_EWK.Integral()
    print sf
    f_sf.write("%0.2f" %sf)
    f_sf.close()
