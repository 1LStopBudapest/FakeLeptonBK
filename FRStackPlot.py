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
    default=['QCD', 'JetHT_Data'],      #last sample should be data as to be consistent with StackHists funtion.
    #default=['VV', 'DYJetsToLL', 'ZJetsToNuNu', 'ST','TTSingleLep_pow', 'WJetsToLNu', 'QCD', 'JetHT_Data'],      #last sample should be data as to be consistent with StackHists funtion.
    )
    argParser.add_argument(
        '-c', '--channel',           action='store',                    type=str,            default='Electron',
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
    StackHists(files, samplelists, 'LepPt_loose', plotDir, 'FRMeasurementRegion')
    StackHists(files, samplelists, 'LepPt_tight', plotDir, 'FRMeasurementRegion')

