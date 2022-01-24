import os, sys
import ROOT
import types
#import numpy

from RegSel import RegSel

sys.path.append('../')
from Helper.HistInfo import HistInfo
from Helper.MCWeight import MCWeight
from TriggerStudy.TrigVarSel import TrigVarSel
from Sample.SampleChain import SampleChain
from Helper.VarCalc import *
from Sample.FileList_Fake_2016_janik import samples as samples_2016

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
    argParser.add_argument('--channel',           action='store',                    type=str,            default='Electron',                                       help="Which lepton?" )
    argParser.add_argument('--region',            action='store',                    type=str,            default='mesurement',                                     help="Which region?" )    
    #argParser.add_argument('--pJobs',             action='store',                    type=bool,            default=False,                                           help="using GPU parallel program or not" )

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


ptBinning = [3.5, 5, 12, 20, 30, 50,200]
#metBinning= [10, 0, 1000]
metBinning= [0.0, 100 , 200 , 300 , 400 , 500 , 600,700,800,900,1000]
#mtBinning=  [10, 0, 1000]
mtBinning=  [0.0, 100 , 200 , 300 , 400 , 500 , 600,700,800,900,1000]
muon_etaBinning= [-2.4,-2,-1.6,-1.2,-0.8,-0.4,0,0.4,0.8,1.2,1.6,2,2.4]
ele_etaBinning= [-2.5,-2,-1.5,-1.0,0,0.5,1,1.5,2,2.5]
#vtxBinning= [10, 0, 50]
vtxBinning= [0.0 , 10 , 20 , 30, 40 , 50]


histext = ''

if 'T2tt' in samples:
    sample = samples
    print 'running over: ', sample
    hfile = ROOT.TFile( 'FRStackHist_'+lepOpt+'_'+sample+'_%i_%i'%(options.startfile+1, options.startfile + options.nfiles)+'.root', 'RECREATE')
    histos = {}
    histos['LepPt_loose'] = HistInfo(hname = 'LepPt_loose', sample = histext, binning = ptBinning, histclass = ROOT.TH1F, binopt = 'var').make_hist()
    histos['LepPt_tight'] = HistInfo(hname = 'LepPt_tight', sample = histext, binning = ptBinning, histclass = ROOT.TH1F, binopt = 'var').make_hist()
    histos['MET'] = HistInfo(hname = 'MET', sample = histext, binning = metBinning, histclass = ROOT.TH1F, binopt = 'var').make_hist()
    histos['MT'] = HistInfo(hname = 'MT', sample = histext, binning = mtBinning, histclass = ROOT.TH1F, binopt = 'var').make_hist()
    histos['Mu_Eta'] = HistInfo(hname = 'Mu_Eta', sample = histext, binning = muon_etaBinning, histclass = ROOT.TH1F, binopt = 'var').make_hist()
    histos['Ele_Eta'] = HistInfo(hname = 'Ele_Eta', sample = histext, binning = ele_etaBinning, histclass = ROOT.TH1F, binopt = 'var').make_hist()
    histos['Pgoodvtx_number'] = HistInfo(hname = 'Pgoodvtx_number', sample = histext, binning = vtxBinning, histclass = ROOT.TH1F, binopt = 'var').make_hist()
    
    ch = SampleChain(sample, options.startfile, options.nfiles, year, 'fake').getchain()
    print 'Total events of selected files of the', sample, 'sample: ', ch.GetEntries()
    n_entries = ch.GetEntries()
    #n_entries = 10
    nevtcut = n_entries -1 if nEvents == - 1 else nEvents - 1
    print 'Running over total events: ', nevtcut+1
    for ientry in range(n_entries):
        if ientry > nevtcut: break
        if ientry % (nevtcut/10)==0 : print 'processing ', ientry,'th event'
        ch.GetEntry(ientry)
        '''
        if isData and lepOpt == 'Mu' and 'DoubleMuon' in samples and ch.Muon_pt > 30 : continue 
        if isData and lepOpt == 'Mu' and 'SingleMuon' in samples and ch.Muon_pt <= 30 : continue
        if isData and lepOpt == 'Ele' and 'JetHT' in samples and ch.Electron_pt > 12 : continue 
        if isData and lepOpt == 'Ele' and 'DoubleEG' in samples and ch.Electron_pt <= 12 : continue
        '''
        if isData:
            lumiscale = 1.0
            MCcorr = 1.0
        else:
            #lumiscale = (DataLumi/1000.0) * ch.weight
            lumiscale =  ch.weight
            MCcorr = MCWeight(ch, year,s).getTotalWeight()
        getSel = RegSel(ch, isData, year)
        msrReg = getSel.MsrmntReg(lepOpt)
        passTrig = TrigVarSel(ch, sample).passFakeRateLepTrig(lepOpt)  # before .passFakeRateJetTrig() if isData else True
        if msrReg and passTrig:
            lepPt = getSel.getLooseLep(lepOpt)['pt']
            lepid = getSel.getLooseLep(lepOpt)['idx']
            met   = ch.MET_pt
            mt    = getSel.MsrMT(lepOpt)
            muon_eta = ch.Muon_eta
            ele_eta = ch.Electron_eta
            npgood_vtx = ch.PV_npvsGood
            print(lepPt , '  ', met , '  ',mt, '  ',muon_eta, '  ',ele_eta, '  ',npgood_vtx)
            Fill1D(histos['LepPt_loose'], lepPt, lumiscale * MCcorr)
            Fill1D(histos['MET'], met, lumiscale * MCcorr)
            Fill1D(histos['MT'], mt, lumiscale * MCcorr)
            Fill1D(histos['Mu_Eta'], muon_eta, lumiscale * MCcorr)
            Fill1D(histos['Ele_Eta'], ele_eta, lumiscale * MCcorr)
            Fill1D(histos['Pgoodvtx_number'], npgood_vtx, lumiscale * MCcorr)
            if getSel.loosepasstight(lepid, lepOpt):
                Fill1D(histos['LepPt_tight'], lepPt, lumiscale * MCcorr)
    hfile.Write()

elif isinstance(samplelist[samples][0], types.ListType):
    histext = samples
    for s in samplelist[samples]:
        sample = list(samplelist.keys())[list(samplelist.values()).index(s)]
        print 'running over: ', sample
        hfile = ROOT.TFile( 'FRStackHist_'+lepOpt+'_'+sample+'_%i_%i'%(options.startfile+1, options.startfile + options.nfiles)+'.root', 'RECREATE')
        histos = {}
        histos['LepPt_loose'] = HistInfo(hname = 'LepPt_loose', sample = histext, binning = ptBinning, histclass = ROOT.TH1F, binopt = 'var').make_hist()
        histos['LepPt_tight'] = HistInfo(hname = 'LepPt_tight', sample = histext, binning = ptBinning, histclass = ROOT.TH1F, binopt = 'var').make_hist()
        histos['MET'] = HistInfo(hname = 'MET', sample = histext, binning = metBinning, histclass = ROOT.TH1F, binopt = 'var').make_hist()
        histos['MT'] = HistInfo(hname = 'MT', sample = histext, binning = mtBinning, histclass = ROOT.TH1F, binopt = 'var').make_hist()
        histos['Mu_Eta'] = HistInfo(hname = 'Mu_Eta', sample = histext, binning = muon_etaBinning, histclass = ROOT.TH1F, binopt = 'var').make_hist()
        histos['Ele_Eta'] = HistInfo(hname = 'Ele_Eta', sample = histext, binning = ele_etaBinning, histclass = ROOT.TH1F, binopt = 'var').make_hist()
        histos['Pgoodvtx_number'] = HistInfo(hname = 'Pgoodvtx_number', sample = histext, binning = vtxBinning, histclass = ROOT.TH1F, binopt = 'var').make_hist()
        ch = SampleChain(sample, options.startfile, options.nfiles, year, 'fake').getchain()
        '''
        if isData:
            muon_pt = ROOT.std.vector('float')()
            ele_pt  = ROOT.std.vector('float')()
        '''
        print 'Total events of selected files of the', sample, 'sample: ', ch.GetEntries()
        n_entries = ch.GetEntries()
        #n_entries = 10
        nevtcut = n_entries -1 if nEvents == - 1 else nEvents - 1
        print 'Running over total events: ', nevtcut+1
        for ientry in range(n_entries):
            if ientry > nevtcut: break
            if ientry % (nevtcut/10)==0 : print 'processing ', ientry,'th event'
            ch.GetEntry(ientry)
            '''
            if isData:
                ch.SetBranchAddress("Muon_pt", muon_pt)
                ch.SetBranchAddress("Electron_pt", ele_pt)            
            if isData and lepOpt == 'Mu' and 'DoubleMuon' in samples and muon_pt > 30 : continue 
            if isData and lepOpt == 'Mu' and 'SingleMuon' in samples and muon_pt <= 30 : continue
            if isData and lepOpt == 'Ele' and 'JetHT' in samples and ele_pt > 12 : continue 
            if isData and lepOpt == 'Ele' and 'DoubleEG' in samples and ele_pt <= 12 : continue
            '''
            if isData:
                lumiscale = 1.0
                MCcorr = 1.0
            else:
                #lumiscale = (DataLumi/1000.0) * ch.weight
                lumiscale =  ch.weight
                MCcorr = MCWeight(ch, year,s).getTotalWeight()
            getSel = RegSel(ch, isData, year)
            msrReg = getSel.MsrmntReg(lepOpt)
            passTrig = TrigVarSel(ch, sample).passFakeRateLepTrig(lepOpt)  # before .passFakeRateJetTrig() if isData else True
            if msrReg and passTrig:
                lepPt = getSel.getLooseLep(lepOpt)['pt']
                lepid = getSel.getLooseLep(lepOpt)['idx']
                met   = ch.MET_pt
                mt    = getSel.MsrMT(lepOpt)
                muon_eta = ch.Muon_eta
                ele_eta = ch.Electron_eta
                npgood_vtx = ch.PV_npvsGood
                print(lepPt , '  ', met , '  ',mt, '  ',muon_eta, '  ',ele_eta, '  ',npgood_vtx)
                Fill1D(histos['LepPt_loose'], lepPt, lumiscale * MCcorr)
                Fill1D(histos['MET'], met, lumiscale * MCcorr)
                Fill1D(histos['MT'], mt, lumiscale * MCcorr)
                Fill1D(histos['Mu_Eta'], muon_eta, lumiscale * MCcorr)
                Fill1D(histos['Ele_Eta'], ele_eta, lumiscale * MCcorr)
                Fill1D(histos['Pgoodvtx_number'], npgood_vtx, lumiscale * MCcorr)
                if getSel.loosepasstight(lepid, lepOpt):
                    Fill1D(histos['LepPt_tight'], lepPt, lumiscale * MCcorr)
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
    histos['MET'] = HistInfo(hname = 'MET', sample = histext, binning = metBinning, histclass = ROOT.TH1F, binopt = 'var').make_hist()  
    histos['MT'] = HistInfo(hname = 'MT', sample = histext, binning = mtBinning, histclass = ROOT.TH1F, binopt = 'var').make_hist()
    histos['Mu_Eta'] = HistInfo(hname = 'Mu_Eta', sample = histext, binning = muon_etaBinning, histclass = ROOT.TH1F, binopt = 'var').make_hist()
    histos['Ele_Eta'] = HistInfo(hname = 'Ele_Eta', sample = histext, binning = ele_etaBinning, histclass = ROOT.TH1F, binopt = 'var').make_hist()
    histos['Pgoodvtx_number'] = HistInfo(hname = 'Pgoodvtx_number', sample = histext, binning = vtxBinning, histclass = ROOT.TH1F, binopt = 'var').make_hist()    
    ch = SampleChain(sample, options.startfile, options.nfiles, year, 'fake').getchain()
    
    '''
    if isData:
        muon_pt = ROOT.std.vector('float')()
        ele_pt  = ROOT.std.vector('float')()
    '''
    print 'Total events of selected files of the', sample, 'sample: ', ch.GetEntries()
    n_entries = ch.GetEntries()
    #n_entries = 10
    nevtcut = n_entries -1 if nEvents == - 1 else nEvents - 1
    print 'Running over total events: ', nevtcut+1
    for ientry in range(n_entries):
        if ientry > nevtcut: break
        if nevtcut>10 and ientry % (nevtcut/10)==0 : print 'processing ', ientry,'th event'
        ch.GetEntry(ientry)
        
        '''
        if isData:
            ch.SetBranchAddress("Muon_pt", muon_pt)
            ch.SetBranchAddress("Electron_pt", ele_pt)
        if isData and lepOpt == 'Mu' and 'DoubleMuon' in samples and muon_pt > 30 : continue 
        if isData and lepOpt == 'Mu' and 'SingleMuon' in samples and muon_pt <= 30 : continue
        if isData and lepOpt == 'Ele' and 'JetHT' in samples and ele_pt > 12 : continue 
        if isData and lepOpt == 'Ele' and 'DoubleEG' in samples and ele_pt <= 12 : continue
        '''
        if isData:
            lumiscale = 1.0
            MCcorr = 1.0
        else:
            #lumiscale = (DataLumi/1000.0) * ch.weight
            lumiscale =  ch.weight
            MCcorr = MCWeight(ch, year,sample).getTotalWeight()
        getSel = RegSel(ch, isData, year)
        msrReg = getSel.MsrmntReg(lepOpt)
        passTrig = TrigVarSel(ch, sample).passFakeRateLepTrig(lepOpt)  # before .passFakeRateJetTrig() if isData else True
        if msrReg and passTrig:
            lepPt = getSel.getLooseLep(lepOpt)['pt']
            lepid = getSel.getLooseLep(lepOpt)['idx']
            met   = ch.MET_pt
            mt    = getSel.MsrMT(lepOpt)
            if lepOpt== 'Mu' : 
                muon_eta = getSel.getLooseLep(lepOpt)['eta']
            else: 
                ele_eta = getSel.getLooseLep(lepOpt)['eta']
            npgood_vtx = ch.PV_npvsGood
            #print(lepPt , '  ', met , '  ',mt, '  ', muon_eta , '  ',ele_eta, '  ',npgood_vtx, ' ' , lumiscale , '  ' ,  MCcorr , '  ', lumiscale * MCcorr  )
            
            Fill1D(histos['LepPt_loose'], lepPt, lumiscale * MCcorr)
            Fill1D(histos['MET'], met, lumiscale * MCcorr)
           
            Fill1D(histos['MT'], mt, lumiscale * MCcorr)
            if lepOpt== 'Mu' :
                Fill1D(histos['Mu_Eta'], muon_eta, lumiscale * MCcorr)
            else:
                Fill1D(histos['Ele_Eta'], ele_eta, lumiscale * MCcorr)
            Fill1D(histos['Pgoodvtx_number'], npgood_vtx, lumiscale * MCcorr)
            

            if getSel.loosepasstight(lepid, lepOpt):
                Fill1D(histos['LepPt_tight'], lepPt, lumiscale * MCcorr)
                

    hfile.Write()
