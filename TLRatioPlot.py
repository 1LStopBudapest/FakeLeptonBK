import os, sys
import ROOT



sys.path.append('../')
from Sample.SampleChain import SampleChain
from Sample.Dir import plotDir
from Helper.PlotHelper import *
from Helper.Style import *

import numpy as np

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
    default=['WJetsToLNu_comb', 'TTSingleLep_pow', 'TTLep_pow', 'DoubleMuon_Data'],      #last sample should be data as to be consistent with StackHists funtion.
    )
    argParser.add_argument(
        '-c', '--channel',           action='store',                    type=str,            default='Muon',
    )
    argParser.add_argument(
        '-s', '--sample',           action='store',                    type=str,            default='DoubleMuon_Data',
    )
    argParser.add_argument(
        '-b', '--isSingle',           action='store',                   type=bool,            default=False,
    )

    return argParser

options = get_parser().parse_args()

samplelists = options.alist
channel = options.channel
sample = options.sample
isSingleSample = options.isSingle

lepOpt = 'Ele' if 'Electron' in channel else 'Mu'

doplots = True

if isSingleSample:
    if os.path.exists('TLHist_'+lepOpt+'_'+sample+'.root'):
        f = ROOT.TFile.Open('TLHist_'+lepOpt+'_'+sample+'.root')
    elif os.path.exists(plotDir+'TLFiles/TLHist_'+lepOpt+'_'+sample+'.root'):
        f = ROOT.TFile.Open(plotDir+'TLFiles/TLRatioHist_'+lepOpt+'_'+sample+'.root')
    else:
        doplots = False        
        print 'Root files for',lepOpt,'channel and for',sample,'sample soes not exist. Please run python TLHistMaker.py --sample',sample,'--channel',lepOpt
        f = None
    if f is not None:
        hst=[]
        hst.append(f.Get('TLLepPt_num_brl_'+sample))
        hst.append(f.Get('TLLepPt_den_brl_'+sample))
        hst.append(f.Get('TLLepPt_num_ecp_'+sample))
        hst.append(f.Get('TLLepPt_den_ecp_'+sample))

else:    
    files = []
    print 'here1'
    for sl in samplelists:
        if os.path.exists('TLHist_'+lepOpt+'_'+sl+'.root'):
            files.append(ROOT.TFile.Open('TLHist_'+lepOpt+'_'+sl+'.root'))
        elif os.path.exists(plotDir+'TLHistFiles/TLHist_'+lepOpt+'_'+sl+'.root'):
            files.append(ROOT.TFile.Open(plotDir+'TLHistFiles/TLHist_'+lepOpt+'_'+sl+'.root'))
        else:
            doplots = False        
            print 'Root files for',lepOpt,'channel and for',sl,'sample soes not exist. Please run python TLHistMaker.py --sample',sl,'--channel',lepOpt

    if len(files)!=0:
        hst=[]
        hsEWK=[]
        hsd=[]
        hsEWK.append(files[0].Get('TLLepPt_num_brl_'+samplelists[0]))
        hsEWK.append(files[0].Get('TLLepPt_den_brl_'+samplelists[0]))
        hsEWK.append(files[0].Get('TLLepPt_num_ecp_'+samplelists[0]))
        hsEWK.append(files[0].Get('TLLepPt_den_ecp_'+samplelists[0]))
        for i, f in enumerate(files,0):
            if i==0:continue
            elif i==len(files)-1:
                hsd.append(f.Get('TLLepPt_num_brl_'+samplelists[i]))
                hsd.append(f.Get('TLLepPt_den_brl_'+samplelists[i]))
                hsd.append(f.Get('TLLepPt_num_ecp_'+samplelists[i]))
                hsd.append(f.Get('TLLepPt_den_ecp_'+samplelists[i]))
            else:
                hsEWK[0].Add(f.Get('TLLepPt_num_brl_'+samplelists[i]))
                hsEWK[1].Add(f.Get('TLLepPt_den_brl_'+samplelists[i]))
                hsEWK[2].Add(f.Get('TLLepPt_num_ecp_'+samplelists[i]))
                hsEWK[3].Add(f.Get('TLLepPt_den_ecp_'+samplelists[i]))

        if len(hsEWK)!=len(hsd): print 'Check above histogram access method again, something is wrong!!'            
        for i in range(len(hsd)):
            h = hsd[i].Clone(hsd[i].GetName())
            h.Add(hsEWK[i], -1)
            hst.append(h)
            
if doplots:
    outputDir = os.getcwd()
    
    hRatio_b = getRatioHist(hst[0], hst[1], "TLRatio_Barel_"+lepOpt, "FakeRate", lepOpt+'pt', 1.0)
    hRatio_e = getRatioHist(hst[2], hst[3], "TLRatio_Endcap_"+lepOpt, "FakeRate", lepOpt+'pt', 1.0)
    Plot1D(hRatio_b, outputDir, drawOption="text")
    Plot1D(hRatio_e, outputDir, drawOption="text")


