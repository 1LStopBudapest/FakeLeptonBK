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
    argParser.add_argument('--sample',           action='store',                     type=str,            default='WJetsToLNu_comb',                                help="Which sample?" )
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
    DataLumi = SampleChain.luminosity_2016_forTL
elif year==2017:
    samplelist = samples_2017
    DataLumi = SampleChain.luminosity_2017
else:
    samplelist = samples_2018 
    DataLumi = SampleChain.luminosity_2018
    
ptBinning = [3.5, 5.0, 8, 10, 15, 20, 30, 50]
etaBinning = [0.,1.442,1.566,3.142]

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
        #n_entries = ch.GetEntries()
        n_entries = 1000
        nevtcut = n_entries -1 if nEvents == - 1 else nEvents - 1
        print 'Running over total events: ', nevtcut+1
        for ientry in range(n_entries):
            if ientry > nevtcut: break
            if ientry % (nevtcut/10)==0 : print 'processing ', ientry,'th event'
            ch.GetEntry(ientry)
            getSel = RegSel(ch, isData, year)
            msrReg = getSel.MsrmntReg(lepOpt)
            passTrig = TrigVarSel(ch, sample).passFakeRateLepTrig_TL_oneTrig(lepOpt)
            if msrReg and passTrig:
                lepid = getSel.getLooseLep(lepOpt)['idx']
                if isData:
                    lumiscale = 1.0
                    MCcorr = 1.0
                    #EWKNorm = 1.0
                else:
                    '''
                    # for checking janik values
                    lumiscale = (1.0) * ch.weight
                    MCcorr = get_PU_weight_janik(ch.PV_npvsGood)
                    #print ch.PV_npvsGood , get_PU_weight(ch.PV_npvsGood)
                    EWKNorm = 0.000163
                    '''
                    lumiscale = (DataLumi) * ch.weight
                    MCcorr = get_PU_weight(ch.Pileup_nTrueInt)
                    if lepOpt == 'Mu':
                        lep_promptflag = ord(ch.Muon_genPartFlav[lepid])
                        if lep_promptflag not in [ 1 , 15 ] : continue
                    else:
                        lep_promptflag = ord(ch.Electron_genPartFlav[lepid])
                        if lep_promptflag not in [ 1 , 15 ] : continue
                        
                lepPt = getSel.getLooseLep(lepOpt)['pt']
                lepeta = getSel.getLooseLep(lepOpt)['eta']
                if abs(lepeta)>=etaBinning[0] and abs(lepeta)<=etaBinning[1]:
                    if getSel.looseNottight(lepid, lepOpt): Fill1D(histos['TLLepPt_den_brl'], lepPt, lumiscale * MCcorr )
                    if getSel.loosepasstight(lepid, lepOpt): Fill1D(histos['TLLepPt_num_brl'], lepPt, lumiscale * MCcorr )
                    
                if abs(lepeta)>=etaBinning[2] and abs(lepeta)<=etaBinning[3]:
                    if getSel.looseNottight(lepid, lepOpt): Fill1D(histos['TLLepPt_den_ecp'], lepPt, lumiscale * MCcorr)
                    if getSel.loosepasstight(lepid, lepOpt): Fill1D(histos['TLLepPt_num_ecp'], lepPt, lumiscale * MCcorr)
                    
                     
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
    #n_entries = ch.GetEntries()
    n_entries = 1000
    nevtcut = n_entries -1 if nEvents == - 1 else nEvents - 1
    print 'Running over total events: ', nevtcut+1
    for ientry in range(n_entries):
        if ientry > nevtcut: break
        if nevtcut>10 and ientry % (nevtcut/10)==0 : print 'processing ', ientry,'th event'
        ch.GetEntry(ientry)
        getSel = RegSel(ch, isData, year)
        msrReg = getSel.MsrmntReg(lepOpt)
        passTrig = TrigVarSel(ch, sample).passFakeRateLepTrig_TL_oneTrig(lepOpt)
        if msrReg and passTrig:
            lepid = getSel.getLooseLep(lepOpt)['idx']
            if isData:
                lumiscale = 1.0
                MCcorr = 1.0
                #EWKNorm = 1.0
            else:
                '''
                # for checking janik values
                lumiscale = (1.0) * ch.weight
                MCcorr = get_PU_weight_janik(ch.PV_npvsGood)
                #print ch.PV_npvsGood , get_PU_weight(ch.PV_npvsGood)
                EWKNorm = 0.000163
                '''
                lumiscale = (DataLumi) * ch.weight
                MCcorr = get_PU_weight(ch.Pileup_nTrueInt)
                if lepOpt == 'Mu':
                    lep_promptflag = ord(ch.Muon_genPartFlav[lepid])
                    if lep_promptflag not in [ 1 , 15 ] : continue
                else:
                    lep_promptflag = ord(ch.Electron_genPartFlav[lepid])
                    if lep_promptflag not in [ 1 , 15 ] : continue                    
            
            lepPt = getSel.getLooseLep(lepOpt)['pt']
            lepeta = getSel.getLooseLep(lepOpt)['eta']
            
            if abs(lepeta)>=etaBinning[0] and abs(lepeta)<=etaBinning[1]:
                if getSel.looseNottight(lepid, lepOpt): Fill1D(histos['TLLepPt_den_brl'], lepPt, lumiscale * MCcorr )
                if getSel.loosepasstight(lepid, lepOpt): Fill1D(histos['TLLepPt_num_brl'], lepPt, lumiscale * MCcorr)
                
            if abs(lepeta)>=etaBinning[2] and abs(lepeta)<=etaBinning[3]:
                if getSel.looseNottight(lepid, lepOpt): Fill1D(histos['TLLepPt_den_ecp'], lepPt, lumiscale * MCcorr )
                if getSel.loosepasstight(lepid, lepOpt): Fill1D(histos['TLLepPt_num_ecp'], lepPt, lumiscale * MCcorr)
                

                
    hfile.Write()
