import os, sys
import ROOT
import types


from RegSel import RegSel

sys.path.append('../')
from Helper.HistInfo import HistInfo
from TriggerStudy.TrigVarSel import TrigVarSel
from Sample.SampleChain import SampleChain
from Helper.VarCalc import *
from Sample.FileList_Fake_2016 import samples as samples_2016

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
    argParser.add_argument('--channel',           action='store',                    type=str,            default='Muon',                                       help="Which lepton?" )
    argParser.add_argument('--region',            action='store',                    type=str,            default='mesurement',                                     help="Which lepton?" )    
    argParser.add_argument('--pJobs',             action='store',                    type=bool,            default=False,                                           help="using GPU parallel program or not" )

    return argParser

options = get_parser().parse_args()



samples  = options.sample
channel = options.channel
nEvents = options.nevents
year = options.year

isData = True if ('Run' in samples or 'Data' in samples) else False

lepOpt = 'Ele' if 'Electron' in channel else 'Mu'

DataLumi = 1.0

if year==2016:
    samplelist = samples_2016
    DataLumi = SampleChain.luminosity_2016
elif year==2017:
    samplelist = samples_2017
    DataLumi = SampleChain.luminosity_2017
else:
    samplelist = samples_2018
    DataLumi = SampleChain.luminosity_2018


ptBinning = [3.5, 5, 12, 20, 30, 50, 80, 200]

histext = ''

if isinstance(samplelist[samples][0], types.ListType):
    histext = samples
    for s in samplelist[samples]:
        sample = list(samplelist.keys())[list(samplelist.values()).index(s)]
        print 'running over: ', sample
        hfile = ROOT.TFile( 'FRStackHist_'+lepOpt+'_'+sample+'_%i_%i'%(options.startfile+1, options.startfile + options.nfiles)+'.root', 'RECREATE')
        histos = {}
        histos['LepPt_loose'] = HistInfo(hname = 'LepPt_loose', sample = histext, binning = ptBinning, histclass = ROOT.TH1F, binopt = 'var').make_hist()
        histos['LepPt_tight'] = HistInfo(hname = 'LepPt_tight', sample = histext, binning = ptBinning, histclass = ROOT.TH1F, binopt = 'var').make_hist()
        
        ch = SampleChain(sample, options.startfile, options.nfiles, year, 'fake').getchain()
        print 'Total events of selected files of the', sample, 'sample: ', ch.GetEntries()
        n_entries = ch.GetEntries()
        nevtcut = n_entries -1 if nEvents == - 1 else nEvents - 1
        print 'Running over total events: ', nevtcut+1
        for ientry in range(n_entries):
            if ientry > nevtcut: break
            if ientry % (nevtcut/10)==0 : print 'processing ', ientry,'th event'
            ch.GetEntry(ientry)
            if isData:
                lumiscale = 1.0
            else:
                lumiscale = (DataLumi/1000.0) * ch.weight
            getSel = RegSel(ch, isData, year)
            msrReg = getSel.MsrmntReg(lepOpt)
            passTrig = TrigVarSel(ch, sample).passFakeRateJetTrig() if isData else True
            if msrReg and passTrig:
                lepPt = getSel.getLooseLep(lepOpt)['pt']
                lepid = getSel.getLooseLep(lepOpt)['idx']
                Fill1D(histos['LepPt_loose'], lepPt, lumiscale)
                if getSel.loosepasstight(lepid, lepOpt):
                    Fill1D(histos['LepPt_tight'], lepPt, lumiscale)
        hfile.Write()

else:
    histext = samples
    for l in list(samplelist.values()):
        if samplelist[samples] in l: histext = list(samplelist.keys())[list(samplelist.values()).index(l)]
    sample = samples
    print 'running over: ', sample
    hfile = ROOT.TFile( 'FRStackHist_'+lepOpt+'_'+sample+'_%i_%i'%(options.startfile+1, options.startfile + options.nfiles)+'.root', 'RECREATE')
    histos = {}
    histos['LepPt_loose'] = HistInfo(hname = 'LepPt_loose', sample = histext, binning = ptBinning, histclass = ROOT.TH1F, binopt = 'var').make_hist()
    histos['LepPt_tight'] = HistInfo(hname = 'LepPt_tight', sample = histext, binning = ptBinning, histclass = ROOT.TH1F, binopt = 'var').make_hist()
        
    ch = SampleChain(sample, options.startfile, options.nfiles, year, 'fake').getchain()
    print 'Total events of selected files of the', sample, 'sample: ', ch.GetEntries()
    n_entries = ch.GetEntries()
    nevtcut = n_entries -1 if nEvents == - 1 else nEvents - 1
    print 'Running over total events: ', nevtcut+1
    for ientry in range(n_entries):
        if ientry > nevtcut: break
        if nevtcut>10 and ientry % (nevtcut/10)==0 : print 'processing ', ientry,'th event'
        ch.GetEntry(ientry)
        if isData:
            lumiscale = 1.0
        else:
            lumiscale = (DataLumi/1000.0) * ch.weight
        getSel = RegSel(ch, isData, year)
        msrReg = getSel.MsrmntReg(lepOpt)
        passTrig = TrigVarSel(ch, sample).passFakeRateJetTrig() if isData else True
        if msrReg and passTrig:
            lepPt = getSel.getLooseLep(lepOpt)['pt']
            lepid = getSel.getLooseLep(lepOpt)['idx']
            Fill1D(histos['LepPt_loose'], lepPt, lumiscale)
            if getSel.loosepasstight(lepid, lepOpt):
                Fill1D(histos['LepPt_tight'], lepPt, lumiscale)

    hfile.Write()
