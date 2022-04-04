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
    default=['UL16PreVFP_WJetsToLNu', 'UL16PreVFP_DYJetsToLL', 'UL16PreVFP_TTLep_pow', 'UL16PreVFP_TTSingleLep_pow' ,'UL16PreVFP_MET_Data'],#last sample should be data as to be consistent with StackHists funtion.
    )
    argParser.add_argument('-c', '--channel',        action='store',                type=str,            default='Muon',)
    argParser.add_argument('-s', '--sample',         action='store',                type=str,            default='DoubleMuon_Data',)
    argParser.add_argument('-b', '--isSingle',       action='store',                type=bool,           default=False,)
    argParser.add_argument('-r' ,'--region',         action='store',                type=str,            default='SR',       help="Which region?", )
    return argParser

options = get_parser().parse_args()

samplelists = options.alist
channel = options.channel
sample = options.sample
isSingleSample = options.isSingle
region = options.region

lepOpt = 'Ele' if 'Electron' in channel else 'Mu'

doplots = True

if isSingleSample:
    if os.path.exists('NFHist_region_'+region+'_for_'+lepOpt+'_'+sample+'.root'):
        f = ROOT.TFile.Open('NFHist_region_'+region+'_for_'+lepOpt+'_'+sample+'.root')
    elif os.path.exists(plotDir+'NFHistFiles/NFHist_region_'+region+'_for_'+lepOpt+'_'+sample+'.root'):
        f = ROOT.TFile.Open(plotDir+'NFHistFiles/NFHist_region_'+region+'_for_'+lepOpt+'_'+sample+'.root')
    else:
        doplots = False        
        print 'Root files for',lepOpt,'channel and for',sample,'sample and region ' , region , 'does not exist. Please run python NF_SR_HistMaker.py --sample',sample,'--channel',lepOpt ,'--region', region
        f = None
    if f is not None:
        hst=[]
        hst.append(f.Get('NF_AppReg_all_'+sample))
        hst.append(f.Get('NF_SearReg_all_'+sample))
        hst.append(f.Get('NF_AppReg_perBin_'+sample))
        hst.append(f.Get('NF_SearReg_perBin_'+sample))
        

else:    
    files = []
    print 'here1'
    for sl in samplelists:
        if os.path.exists('NFHist_region_'+region+'_for_'+lepOpt+'_'+sl+'.root'):
            files.append(ROOT.TFile.Open('NFHist_region_'+region+'_for_'+lepOpt+'_'+sl+'.root'))
            print ' one file   ' , 'NFHist_region_', region , 'for lep ',lepOpt,'_',sl
        elif os.path.exists(plotDir+'NFHistFiles/NFHist_region_'+region+'_for_'+lepOpt+'_'+sl+'.root'):
            files.append(ROOT.TFile.Open(plotDir+'NFHistFiles/NFHist_region_'+region+'_for_'+lepOpt+'_'+sl+'.root'))
            print ' two file   ' , plotDir,'NFHistFiles/NFHist_region_',region,'_for_',lepOpt,'_',sl
        else:
            doplots = False        
            print 'Root files for',lepOpt,'channel and for',sl,'sample does not exist. Please run python NF_SR_HistMaker.py --sample',sl,'--channel',lepOpt ,'--region', region

    if len(files)!=0:
        #print len(files) , samplelists[0] , samplelists[1] , samplelists[2]  , files[0] , files[1] , files[2] 
        hst=[]
        hsEWK=[]
        hsd=[]        
        hsEWK.append(files[0].Get('NF_AppReg_all_'+samplelists[0]))
        hsEWK.append(files[0].Get('NF_SearReg_all_'+samplelists[0]))
        hsEWK.append(files[0].Get('NF_AppReg_perBin_'+samplelists[0]))
        hsEWK.append(files[0].Get('NF_SearReg_perBin_'+samplelists[0]))
        
        for i, f in enumerate(files,0):
            if i==0:continue
            elif i==len(files)-1:
                hsd.append(f.Get('NF_AppReg_all_'+samplelists[i]))
                hsd.append(f.Get('NF_SearReg_all_'+samplelists[i]))
                hsd.append(f.Get('NF_AppReg_perBin_'+samplelists[i]))
                hsd.append(f.Get('NF_SearReg_perBin_'+samplelists[i]))
                
            else:
                
                hsEWK[0].Add(f.Get('NF_AppReg_all_'+samplelists[i]))
                hsEWK[1].Add(f.Get('NF_SearReg_all_'+samplelists[i]))
                hsEWK[2].Add(f.Get('NF_AppReg_perBin_'+samplelists[i]))
                hsEWK[3].Add(f.Get('NF_SearReg_perBin_'+samplelists[i]))

        if len(hsEWK)!=len(hsd): print 'Check above histogram access method again, something is wrong!!'            
        for i in range(len(hsd)):
            h = hsd[i].Clone(hsd[i].GetName())
            h.Add(hsEWK[i], -1)
            hst.append(h)

c1 = c1 = ROOT.TCanvas('c1', '' , 800,600)
c1.Divide(1,4)
c1.cd(1)
hst[0].Draw()
c1.cd(2)
hst[1].Draw()
c1.cd(3)
hst[2].Draw()
c1.cd(4)
hst[3].Draw()  
c1.SaveAs('Number_Fake_%s_%s.pdf'%(lepOpt ,region ))      



