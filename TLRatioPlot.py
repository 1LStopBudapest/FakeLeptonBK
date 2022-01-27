import os, sys
import ROOT



sys.path.append('../')
from Sample.SampleChain import SampleChain
from Sample.Dir import plotDir
from Helper.PlotHelper import *
from Helper.Style import *

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
        '-s', '--sample',           action='store',                    type=str,            default='QCD',
    )
    argParser.add_argument(
        '-b', '--isSingle',           action='store',                   type=bool,            default=True,
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

    for sl in samplelists:
        if os.path.exists('TLHist_'+lepOpt+'_'+sl+'.root'):
            files.append(ROOT.TFile.Open('TLHist_'+lepOpt+'_'+sl+'.root'))
        elif os.path.exists(plotDir+'TLHistFiles/TLHist_'+lepOpt+'_'+sl+'.root'):
            files.append(ROOT.TFile.Open(plotDir+'TLHistFiles/TLHist_'+lepOpt+'_'+sl+'.root'))
        else:
            doplots = False        
            print 'Root files for',lepOpt,'channel and for',sl,'sample soes not exist. Please run python TLHistMaker.py --sample',sl,'--channel',lepOpt

    if len(f)!=0:
        hst=[]
        for i, f in enumerate(files,0):
            hs=[]
            hs.append(f.Get('TLLepPt_num_brl_'+samplelists[i]))
            hs.append(f.Get('TLLepPt_den_brl_'+samplelists[i]))
            hs.append(f.Get('TLLepPt_num_ecp_'+samplelists[i]))
            hs.append(f.Get('TLLepPt_den_ecp_'+samplelists[i]))
            hst.append(hs)
            
if doplots :
    hRatio = getRatioHist(hnum, hden, "FakeRate", lepOpt+'pt', 0.6)
    c = ROOT.TCanvas('c', '', 600, 800)
    hRatio.Draw("PE")
    c.SaveAs('FakeRate_'+lepOpt+'_'+sample+".png")
    c.Close()
