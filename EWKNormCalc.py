import os, sys
import ROOT



sys.path.append('../')
from Sample.SampleChain import SampleChain
from Sample.Dir import plotDir
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
    StackHists(files, samplelists, 'MT', plotDir, 'FRmTHistFiles', scaleOption='AreaScaling')
    #StackHists(files, samplelists, 'MT', plotDir, 'FRmTHistFiles')
'''
    hs=[]
    for i, f in enumerate(files,0):
        hs.append(f.Get('MT_'+samplelists[i]))

    h_QCD = hs[0].Clone("QCDMC")#first element is QCD and last one is data
    h_EWK = hs[1].Clone("EWKMC")
    for i, h in enumerate(hs, 1):
        if i!=len(hs)-1:
            h_EWK.Add(h)
    #caculate scale
    i_low = hs[-1].GetXaxis().FindBin(80)
    i_up  = hs[-1].GetXaxis().FindBin(100)
    I_data = hs[-1].Integral(i_low,i_up)

    I_QCD = h_QCD.Integral(i_low,i_up)
    I_EWK = h_EWK.Integral(i_low,i_up)
    I_scale = I_data / (I_QCD + I_EWK)
    h_QCD.Scale(I_scale)
    h_EWK.Scale(I_scale)

    #Template Fit
    mc = ROOT.TObjArray(2)
    mc.Add(h_QCD)
    mc.Add(h_EWK)
    templateFit = ROOT.TFractionFitter(hs[-1], mc)
    for i in xrange(2):
        templateFit.Constrain(i,0.0,1.0)
    templateFit.SetRangeX(5,30)
    status = templateFit.Fit()
    if int(status) != 0:
        print 'TFraction fit failed!!  aborting'
        exit(0)
    h_fittedMC = templateFit.GetPlot()
    QCD_sf = templateFit.GetMCPrediction(0)
    EWK_sf = templateFit.GetMCPrediction(1)    
''' 
