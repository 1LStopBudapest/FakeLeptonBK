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
    default=['DYJetsToLL', 'WJetsToLNu_comb', 'TTLep_pow' , 'TTSingleLep_pow' , 'QCD', 'DoubleMuon_Data'],      #last sample should be data as to be consistent with StackHists funtion.
    #default=['VV', 'DYJetsToLL', 'ZJetsToNuNu', 'ST','TTSingleLep_pow', 'WJetsToLNu', 'QCD', 'JetHT_Data'],      #last sample should be data as to be consistent with StackHists funtion.
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
doplots = True

for sl in samplelists:
    if os.path.exists('FRStackHist_'+lepOpt+'_'+sl+'.root'):
        files.append(ROOT.TFile.Open('FRStackHist_'+lepOpt+'_'+sl+'.root'))
    elif os.path.exists(plotDir+'FRStackFiles/FRStackHist_'+lepOpt+'_'+sl+'.root'):
        files.append(ROOT.TFile.Open(plotDir+'FRStackFiles/FRStackHist_'+lepOpt+'_'+sl+'.root'))
    else:
        doplots = False        
        print 'Root files for',lepOpt,'channel and for',sl,'sample soes not exist. Please run python FRStackHistMaker.py --sample',sl,'--channel',lepOpt

if doplots :
    StackHists(files, samplelists, 'MET', plotDir, 'FRMeasurementRegion', islogy=True)
    StackHists(files, samplelists, 'MT', plotDir, 'FRMeasurementRegion', islogy=True)
    StackHists(files, samplelists, 'Pgoodvtx_number', plotDir, 'FRMeasurementRegion', islogy=True)
    StackHists(files, samplelists, 'LepEta', plotDir, 'FRMeasurementRegion', islogy=True)
    StackHists(files, samplelists, 'LepPt', plotDir, 'FRMeasurementRegion', islogy=True)
    #StackHists(files, samplelists, 'LepPt_tight', plotDir, 'FRMeasurementRegion')
    StackHists(files, samplelists, 'jet1metdphi', plotDir, 'FRMeasurementRegion', islogy=True)
    StackHists(files, samplelists, 'jet2metdphi', plotDir, 'FRMeasurementRegion', islogy=True)
    StackHists(files, samplelists, 'jet3metdphi', plotDir, 'FRMeasurementRegion', islogy=True)
    StackHists(files, samplelists, 'Njets', plotDir, 'FRMeasurementRegion', islogy=True)
    StackHists(files, samplelists, 'jet1Pt', plotDir, 'FRMeasurementRegion', islogy=True)
    StackHists(files, samplelists, 'jet2Pt', plotDir, 'FRMeasurementRegion', islogy=True)
    StackHists(files, samplelists, 'jet3Pt', plotDir, 'FRMeasurementRegion', islogy=True)
