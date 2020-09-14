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
    argParser.add_argument('--sample',           action='store',                     type=str,            default='JetHT_Run2016C',                                help="Which sample?" )
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


DataLumi=1.0

if year==2016:
    samplelist = samples_2016 
elif year==2017:
    samplelist = samples_2017 
else:
    samplelist = samples_2018 



sample = samples
print 'running over: ', sample
hfile = ROOT.TFile( 'Check_'+lepOpt+'_'+sample+'_%i_%i'%(options.startfile+1, options.startfile + options.nfiles)+'.root', 'RECREATE')
histos = {}
ext = sample[0:sample.find('_')] if options.pJobs else sample 
histos['TLRatioPt_den'] = HistInfo(hname = 'TLRatioPt_den', sample = ext, binning=[100,0,500], histclass = ROOT.TH1F).make_hist()
histos['TLRatioPt_num'] = HistInfo(hname = 'TLRatioPt_num', sample = ext, binning=[100,0,500], histclass = ROOT.TH1F).make_hist()
histos['NEle_loose'] = HistInfo(hname = 'NEle_loose', sample = ext, binning=[4,0,4], histclass = ROOT.TH1F).make_hist()
histos['NEle_tight'] = HistInfo(hname = 'NEle_tight', sample = ext, binning=[4,0,4], histclass = ROOT.TH1F).make_hist()
histos['NMu_loose'] = HistInfo(hname = 'NMu_loose', sample = ext, binning=[4,0,4], histclass = ROOT.TH1F).make_hist()
histos['NMu_tight'] = HistInfo(hname = 'NMu_tight', sample = ext, binning=[4,0,4], histclass = ROOT.TH1F).make_hist()
histos['IfEle_loose'] = HistInfo(hname = 'IfEle_loose', sample = ext, binning=[2,0,2], histclass = ROOT.TH1F).make_hist()
histos['IfEle_tight'] = HistInfo(hname = 'IfEle_tight', sample = ext, binning=[2,0,2], histclass = ROOT.TH1F).make_hist()
histos['IfMu_loose'] = HistInfo(hname = 'IfMu_loose', sample = ext, binning=[2,0,2], histclass = ROOT.TH1F).make_hist()
histos['IfMu_tight'] = HistInfo(hname = 'IfMu_tight', sample = ext, binning=[2,0,2], histclass = ROOT.TH1F).make_hist()

ch = SampleChain(sample, options.startfile, options.nfiles, year, 'fake').getchain()
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
    #print ientry
    if getSel.MsrMETcut() and getSel.MsrHTcut(): 
        Fill1D(histos['NMu_tight'], len(getSel.selectMuIdx()))
        Fill1D(histos['NMu_loose'], len(getSel.selectLooseMuIdx()))
        if len(getSel.selectMuIdx()): Fill1D(histos['IfMu_tight'], 1.0)
        if len(getSel.selectLooseMuIdx()): Fill1D(histos['IfMu_loose'], 1.0)
        Fill1D(histos['NEle_tight'], len(getSel.selectEleIdx()))
        Fill1D(histos['NEle_loose'], len(getSel.selectLooseEleIdx()))
        if len(getSel.selectEleIdx()): Fill1D(histos['IfEle_tight'], 1.0)
        if len(getSel.selectLooseEleIdx()): Fill1D(histos['IfEle_loose'], 1.0)

    #if getSel.Msrlepcut(lepOpt): print getSel.Msrlepcut(lepOpt)  
    #if getSel.MsrMTcut(lepOpt): print getSel.MsrMTcut(lepOpt)
    
    #for i in range(len(ch.Muon_pt)):
        #if abs(ch.Muon_dxy[i])>0.1: print abs(ch.Muon_dxy[i])
        #if getSel.muonSelector(ch.Muon_pt[i], ch.Muon_eta[i], ch.Muon_pfRelIso03_all[i], ch.Muon_dxy[i], ch.Muon_dz[i], lepton_selection='other'):
        #print i, getSel.muonSelector(ch.Muon_pt[i], ch.Muon_eta[i], ch.Muon_pfRelIso03_all[i], ch.Muon_dxy[i], ch.Muon_dz[i], lepton_selection='other')
        #print ientry, i, 'pt', ch.Muon_pt[i], 'eta', abs(ch.Muon_eta[i])
    if msrReg and passTrig:
        #if len(getSel.selectMuIdx()) > len(getSel.selectLooseMuIdx()):
            #for i in range(len(ch.Muon_pt)):
               # print i, 'pt', ch.Muon_pt[i], 'eta', abs(ch.Muon_eta[i]), 'iso', ch.Muon_pfRelIso03_all[i], 'iso*pt', ch.Muon_pfRelIso03_all[i]*ch.Muon_pt[i], 'dxy', ch.Muon_dxy[i], 'dz', ch.Muon_dz[i]
                #print 'loose', getSel.muonSelector(pt=ch.Muon_pt[i], eta=ch.Muon_eta[i], iso=ch.Muon_pfRelIso03_all[i], dxy=ch.Muon_dxy[i], dz=ch.Muon_dz[i], lepton_selection='looseHybridIso')
                #print 'tight', getSel.muonSelector(pt=ch.Muon_pt[i], eta=ch.Muon_eta[i], iso=ch.Muon_pfRelIso03_all[i], dxy=ch.Muon_dxy[i], dz=ch.Muon_dz[i], lepton_selection='HybridIso')
        lepPt = getSel.getLooseLep(lepOpt)['pt']
        lepid = getSel.getLooseLep(lepOpt)['idx']
        Fill1D(histos['TLRatioPt_den'], lepPt)
        if getSel.loosepasstight(lepid, lepOpt):
            Fill1D(histos['TLRatioPt_num'], lepPt)
hfile.Write()
