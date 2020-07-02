import os, sys
import ROOT
import types


from RegSel import RegSel

sys.path.append('../')
from Helper.HistInfo import HistInfo
from TriggerStudy.TrigVarSel import TrigVarSel
from Sample.SampleChain import SampleChain
from Helper.VarCalc import *

def get_parser():
    ''' Argument parser.
    '''
    import argparse
    argParser = argparse.ArgumentParser(description = "Argument parser")
    argParser.add_argument('--sample',           action='store',                     type=str,            default='JetHT_Run2016B',                                help="Which sample?" )
    argParser.add_argument('--year',             action='store',                     type=int,            default=2016,                                             help="Which year?" )
    argParser.add_argument('--startfile',        action='store',                     type=int,            default=0,                                                help="start from which root file like 0th or 10th etc?" )
    argParser.add_argument('--nfiles',           action='store',                     type=int,            default=-1,                                               help="No of files to run. -1 means all files" )
    argParser.add_argument('--nevents',           action='store',                    type=int,            default=-1,                                               help="No of events to run. -1 means all events" )
    argParser.add_argument('--channel',           action='store',                    type=str,            default='Electron',                                       help="Which lepton?" )    
    argParser.add_argument('--pJobs',             action='store',                    type=bool,            default=False,                                           help="using GPU parallel program or not" )

    return argParser

options = get_parser().parse_args()



samples  = options.sample
channel = options.channel
nEvents = options.nevents
year = options.year

isData = True if ('Run' in samples or 'Data' in samples) else False

lepOpt = 'Ele' if 'Electron' in channel else 'Mu'

if isinstance(SampleChain.samplelist[samples][0], types.ListType):
    for s in SampleChain.samplelist[samples]:
        sample = list(SampleChain.samplelist.keys())[list(SampleChain.samplelist.values()).index(s)]
        print 'running over: ', sample
        hfile = ROOT.TFile( 'TLRatioHist_'+lepOpt+'_'+sample+'_%i_%i'%(options.startfile+1, options.startfile + options.nfiles)+'.root', 'RECREATE')
        histos = {}
        ext = samples[0:samples.find('_')] if options.pJobs else samples
        histos['TLRatioPt_den'] = HistInfo(hname = 'TLRatioPt_den', sample = ext, binning=[100,0,500], histclass = ROOT.TH1F).make_hist()
        histos['TLRatioPt_num'] = HistInfo(hname = 'TLRatioPt_num', sample = ext, binning=[100,0,500], histclass = ROOT.TH1F).make_hist()

        ch = SampleChain(sample, options.startfile, options.nfiles).getchain()
        print 'Total events of selected files of the', sample, 'sample: ', ch.GetEntries()
        n_entries = ch.GetEntries()
        nevtcut = n_entries -1 if nEvents == - 1 else nEvents - 1
        print 'Running over total events: ', nevtcut+1
        for ientry in range(n_entries):
            if ientry > nevtcut: break
            if ientry % (nevtcut/10)==0 : print 'processing ', ientry,'th event'
            ch.GetEntry(ientry)
            getSel = RegSel(ch, isData, year)
            msrReg = getSel.MsrmntReg(lepOpt)
            passTrig = TrigVarSel(ch, sample).passFakeRateJetTrig() if isData else True
            if msrReg and passTrig:
                lepPt = getSel.getLooseLep(lepOpt)['pt']
                lepid = getSel.getLooseLep(lepOpt)['idx']
                Fill1D(histos['TLRatioPt_den'], lepPt)
                if getSel.loosepasstight(idx, lepOpt):
                     Fill1D(histos['TLRatioPt_num'], lepPt)
        hfile.Write()

else:
    sample = samples
    print 'running over: ', sample
    hfile = ROOT.TFile( 'TLRatioHist_'+lepOpt+'_'+sample+'_%i_%i'%(options.startfile+1, options.startfile + options.nfiles)+'.root', 'RECREATE')
    histos = {}
    ext = sample[0:sample.find('_')] if options.pJobs else sample 
    histos['TLRatioPt_den'] = HistInfo(hname = 'TLRatioPt_den', sample = ext, binning=[100,0,500], histclass = ROOT.TH1F).make_hist()
    histos['TLRatioPt_num'] = HistInfo(hname = 'TLRatioPt_num', sample = ext, binning=[100,0,500], histclass = ROOT.TH1F).make_hist()
    
    ch = SampleChain(sample, options.startfile, options.nfiles).getchain()
    print 'Total events of selected files of the', sample, 'sample: ', ch.GetEntries()
    n_entries = ch.GetEntries()
    nevtcut = n_entries -1 if nEvents == - 1 else nEvents - 1
    print 'Running over total events: ', nevtcut+1
    for ientry in range(n_entries):
        if ientry > nevtcut: break
        if nevtcut>10 and ientry % (nevtcut/10)==0 : print 'processing ', ientry,'th event'
        ch.GetEntry(ientry)
        getSel = RegSel(ch, isData, year)
        msrReg = getSel.MsrmntReg(lepOpt)
        passTrig = TrigVarSel(ch, sample).passFakeRateJetTrig() if isData else True
        #if passTrig and getSel.MsrMETcut():print 'MsrMETcut(): ', getSel.MsrMETcut(), 'MsrHTcut(): ', getSel.MsrHTcut(), 'Msrlepcut(lep): ', getSel.Msrlepcut(lepOpt), 'MsrMTcut(lep): ', getSel.MsrMTcut(lepOpt)
        #if getSel.MsrMETcut():print 'MsrMETcut(): ', getSel.MsrMETcut()
        if msrReg and passTrig:
            lepPt = getSel.getLooseLep(lepOpt)['pt']
            lepid = getSel.getLooseLep(lepOpt)['idx']
            Fill1D(histos['TLRatioPt_den'], lepPt)
            if getSel.loosepasstight(idx, lepOpt):
                Fill1D(histos['TLRatioPt_num'], lepPt)
    hfile.Write()
