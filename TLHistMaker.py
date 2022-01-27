import os, sys
import ROOT
import types


from RegSel import RegSel

sys.path.append('../')
from Helper.HistInfo import HistInfo
from Helper.MCWeight import MCWeight
from TriggerStudy.TrigVarSel import TrigVarSel
from Sample.SampleChain import SampleChain
from Helper.VarCalc import *
#from Sample.FileList_Fake_2016 import samples as samples_2016
from Sample.FileList_Fake_2016_janik import samples as samples_2016

#this scipt will run over data and EWK processes (ttbar and wjets)

def get_parser():
    ''' Argument parser.
    '''
    import argparse
    argParser = argparse.ArgumentParser(description = "Argument parser")
    argParser.add_argument('--sample',           action='store',                     type=str,            default='DoubleMuon_Run2016B',                                help="Which sample?" )
    argParser.add_argument('--year',             action='store',                     type=int,            default=2016,                                             help="Which year?" )
    argParser.add_argument('--startfile',        action='store',                     type=int,            default=0,                                                help="start from which root file like 0th or 10th etc?" )
    argParser.add_argument('--nfiles',           action='store',                     type=int,            default=-1,                                               help="No of files to run. -1 means all files" )
    argParser.add_argument('--nevents',           action='store',                    type=int,            default=-1,                                               help="No of events to run. -1 means all events" )
    argParser.add_argument('--channel',           action='store',                    type=str,            default='Muon',                                       help="Which lepton?" )    

    return argParser

options = get_parser().parse_args()



samples  = options.sample
channel = options.channel
nEvents = options.nevents
year = options.year

isData = True if ('Run' in samples or 'Data' in samples) else False

lepOpt = 'Ele' if 'Electron' in channel else 'Mu'


DataLumi=1.0

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
etaBinning = [0.0, 1.442, 1.566, 2.5]

histext = ''

if isinstance(samplelist[samples][0], types.ListType):
    histext = samples
    for s in samplelist[samples]:
        sample = list(samplelist.keys())[list(samplelist.values()).index(s)]
        print 'running over: ', sample
        hfile = ROOT.TFile( 'TLHist_'+lepOpt+'_'+sample+'_%i_%i'%(options.startfile+1, options.startfile + options.nfiles)+'.root', 'RECREATE')
        histos = {}
        histos['TLLepPt_den_brl'] = HistInfo(hname = 'TLLepPt_den_brl', sample = histext, binning=ptBinning, histclass = ROOT.TH1F, binopt = 'var').make_hist()
        histos['TLLepPt_num_brl'] = HistInfo(hname = 'TLLepPt_num_brl', sample = histext, binning=ptBinning, histclass = ROOT.TH1F, binopt = 'var').make_hist()
        histos['TLLepPt_den_ecp'] = HistInfo(hname = 'TLLepPt_den_ecp', sample = histext, binning=ptBinning, histclass = ROOT.TH1F, binopt = 'var').make_hist()
        histos['TLLepPt_num_ecp'] = HistInfo(hname = 'TLLepPt_num_ecp', sample = histext, binning=ptBinning, histclass = ROOT.TH1F, binopt = 'var').make_hist()

        ch = SampleChain(sample, options.startfile, options.nfiles, year, 'fake').getchain()
        print 'Total events of selected files of the', sample, 'sample: ', ch.GetEntries()
        n_entries = ch.GetEntries()
        nevtcut = n_entries -1 if nEvents == - 1 else nEvents - 1
        print 'Running over total events: ', nevtcut+1
        for ientry in range(n_entries):
            if ientry > nevtcut: break
            if ientry % (nevtcut/10)==0 : print 'processing ', ientry,'th event'
            ch.GetEntry(ientry)

            '''                                                                                                                                                                      if isData and lepOpt == 'Mu' and 'DoubleMuon' in samples and muon_pt > 30 : continue                                                                                    if isData and lepOpt == 'Mu' and 'SingleMuon' in samples and muon_pt <= 30 : continue                                                                                   if isData and lepOpt == 'Ele' and 'JetHT' in samples and ele_pt > 12 : continue                                                                                         if isData and lepOpt == 'Ele' and 'DoubleEG' in samples and ele_pt <= 12 : continue                                                                                     '''
            getSel = RegSel(ch, isData, year)
            msrReg = getSel.MsrmntReg(lepOpt)
            passTrig = TrigVarSel(ch, sample).passFakeRateLepTrig(lepOpt)
            if msrReg and passTrig:
                if isData:
                    lumiscale = 1.0
                    MCcorr = 1.0
                    EWKNorm = 1.0
                else:
                    lumiscale = (DataLumi/1000.0) * ch.weight
                    MCcorr = MCWeight(ch, year,s).getPUWeight()
                    EWKNorm = float(MCWeight(ch, year,s).getEWKNorm())
                lepid = getSel.getLooseLep(lepOpt)['idx']
                lepPt = getSel.getLooseLep(lepOpt)['pt']
                lepPt = getSel.getLooseLep(lepOpt)['eta']
                if abs(lepPt)<=etaBinning[1]:
                    if getSel.looseNottight(lepid, lepOpt): Fill1D(histos['TLLepPt_den_brl'], lepPt, lumiscale * MCcorr * EWKNorm)
                    if getSel.loosepasstight(lepid, lepOpt): Fill1D(histos['TLLepPt_num_brl'], lepPt, lumiscale * MCcorr * EWKNorm)
                if abs(lepPt)>=etaBinning[2]:
                    if getSel.looseNottight(lepid, lepOpt): Fill1D(histos['TLLepPt_den_ecp'], lepPt, lumiscale * MCcorr * EWKNorm)
                    if getSel.loosepasstight(lepid, lepOpt): Fill1D(histos['TLLepPt_num_ecp'], lepPt, lumiscale * MCcorr * EWKNorm)
                     
        hfile.Write()

else:
    histext = samples
    for l in list(samplelist.values()):
        if samplelist[samples] in l: histext = list(samplelist.keys())[list(samplelist.values()).index(l)]
    sample = samples
    print 'running over: ', sample
    hfile = ROOT.TFile( 'TLHist_'+lepOpt+'_'+sample+'_%i_%i'%(options.startfile+1, options.startfile + options.nfiles)+'.root', 'RECREATE')
    histos = {}
    histos['TLLepPt_den_brl'] = HistInfo(hname = 'TLLepPt_den_brl', sample = histext, binning=ptBinning, histclass = ROOT.TH1F, binopt = 'var').make_hist()
    histos['TLLepPt_num_brl'] = HistInfo(hname = 'TLLepPt_num_brl', sample = histext, binning=ptBinning, histclass = ROOT.TH1F, binopt = 'var').make_hist()
    histos['TLLepPt_den_ecp'] = HistInfo(hname = 'TLLepPt_den_ecp', sample = histext, binning=ptBinning, histclass = ROOT.TH1F, binopt = 'var').make_hist()
    histos['TLLepPt_num_ecp'] = HistInfo(hname = 'TLLepPt_num_ecp', sample = histext, binning=ptBinning, histclass = ROOT.TH1F, binopt = 'var').make_hist()
    ch = SampleChain(sample, options.startfile, options.nfiles, year, 'fake').getchain()
    print 'Total events of selected files of the', sample, 'sample: ', ch.GetEntries()
    n_entries = ch.GetEntries()
    nevtcut = n_entries -1 if nEvents == - 1 else nEvents - 1
    print 'Running over total events: ', nevtcut+1
    for ientry in range(n_entries):
        if ientry > nevtcut: break
        if nevtcut>10 and ientry % (nevtcut/10)==0 : print 'processing ', ientry,'th event'
        ch.GetEntry(ientry)

        '''                                                                                                                                                                      if isData and lepOpt == 'Mu' and 'DoubleMuon' in samples and muon_pt > 30 : continue                                                                                    if isData and lepOpt == 'Mu' and 'SingleMuon' in samples and muon_pt <= 30 : continue                                                                                   if isData and lepOpt == 'Ele' and 'JetHT' in samples and ele_pt > 12 : continue                                                                                         if isData and lepOpt == 'Ele' and 'DoubleEG' in samples and ele_pt <= 12 : continue                                                                                     '''
        getSel = RegSel(ch, isData, year)
        msrReg = getSel.MsrmntReg(lepOpt)
        passTrig = TrigVarSel(ch, sample).passFakeRateLepTrig(lepOpt)
        if msrReg and passTrig:
            if isData:
                lumiscale = 1.0
                MCcorr = 1.0
                EWKNorm = 1.0
            else:
                lumiscale = (DataLumi/1000.0) * ch.weight
                MCcorr = MCWeight(ch, year,sample).getPUWeight()
                EWKNorm = float(MCWeight(ch, year,sample).getEWKNorm())
            lepid = getSel.getLooseLep(lepOpt)['idx']
            lepPt = getSel.getLooseLep(lepOpt)['pt']
            lepPt = getSel.getLooseLep(lepOpt)['eta']
            if abs(lepPt)<=etaBinning[1]:
                if getSel.looseNottight(lepid, lepOpt): Fill1D(histos['TLLepPt_den_brl'], lepPt, lumiscale * MCcorr * EWKNorm)
                if getSel.loosepasstight(lepid, lepOpt): Fill1D(histos['TLLepPt_num_brl'], lepPt, lumiscale * MCcorr * EWKNorm)
            if abs(lepPt)>=etaBinning[2]:
                if getSel.looseNottight(lepid, lepOpt): Fill1D(histos['TLLepPt_den_ecp'], lepPt, lumiscale * MCcorr * EWKNorm)
                if getSel.loosepasstight(lepid, lepOpt): Fill1D(histos['TLLepPt_num_ecp'], lepPt, lumiscale * MCcorr * EWKNorm)
                
    hfile.Write()