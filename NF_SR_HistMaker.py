import os, sys
import ROOT
import types


from RegSel_2 import RegSel

sys.path.append('../')
from Helper.HistInfo import HistInfo
from Helper.MCWeight import MCWeight
from TriggerStudy.TrigVarSel import TrigVarSel
from Sample.SampleChain import SampleChain
from Helper.VarCalc import *
from Helper.Binning import *
from Sample.FileList_2016 import samples as samples_2016
#from Sample.FileList_Fake_2016_janik import samples as samples_2016


def get_parser():
    ''' Argument parser.
    '''
    import argparse
    argParser = argparse.ArgumentParser(description = "Argument parser")
    argParser.add_argument('--sample',           action='store',                     type=str,            default='UL16PreVFP_WJetsToLNu',                                help="Which sample?" )
    argParser.add_argument('--year',             action='store',                     type=int,            default=2016,                                             help="Which year?" )
    argParser.add_argument('--startfile',        action='store',                     type=int,            default=0,                                                help="start from which root file like 0th or 10th etc?" )
    argParser.add_argument('--nfiles',           action='store',                     type=int,            default=-1,                                               help="No of files to run. -1 means all files" )
    argParser.add_argument('--nevents',           action='store',                    type=int,            default=-1,                                               help="No of events to run. -1 means all events" )
    argParser.add_argument('--channel',           action='store',                    type=str,            default='Muon',                                           help="Which lepton?" ) 
    argParser.add_argument('--region',            action='store',                    type=str,            default='SR',                                             help="Which region?" )   

    return argParser

options = get_parser().parse_args()



samples  = options.sample
channel = options.channel
nEvents = options.nevents
year = options.year
region = options.region
count74 = 0.0

isData = True if ('Run' in samples or 'Data' in samples) else False

lepOpt = 'Ele' if 'Electron' in channel else 'Mu'


DataLumi=1.0

if year==2016:
    samplelist = samples_2016
    DataLumi = SampleChain.luminosity_2016_preVFP
     
elif year==2017:
    samplelist = samples_2017
    DataLumi = SampleChain.luminosity_2017
else:
    samplelist = samples_2018 
    DataLumi = SampleChain.luminosity_2018

if region == 'SR':
    bins = 44
    binLabel = SRBinLabelList
elif region == 'CR':
    bins = 12
    binLabel = CRBinLabelList
elif region == 'SR+CR':
    bins = 44 + 12
    binLabel = SRBinLabelList+CRBinLabelList
else:
    bins = 1
    binLabel = ['REG']
    
ptBinning = [5.0,8,10,15,20,30,50]
etaBinning = [0.0, 1.442, 1.566, 3]
NEventsBinning = [3,-1,2]
TLratio_brl = [ 0.3 , 0.2 , 0.34 , 0.1 , 0.5 , 0.6 , 0.3]
TLratio_end = [ 0.32 , 0.22 , 0.342 , 0.1 , 0.5 , 0.6 , 0.3]

histext = ''

if isinstance(samplelist[samples][0], types.ListType):
    histext = samples
    for s in samplelist[samples]:
        sample = list(samplelist.keys())[list(samplelist.values()).index(s)]
        print 'running over: ', sample
        hfile = ROOT.TFile( 'NFHist_region_'+region+'_for_'+lepOpt+'_'+sample+'_%i_%i'%(options.startfile+1, options.startfile + options.nfiles)+'.root', 'RECREATE')
        histos = {}        
        histos['NF_AppReg_all'] = HistInfo(hname = 'NF_AppReg_all', sample = histext, binning=NEventsBinning, histclass = ROOT.TH1F, binopt = 'norm').make_hist() #  no *TL
        histos['NF_SearReg_all'] = HistInfo(hname = 'NF_SearReg_all', sample = histext, binning=NEventsBinning, histclass = ROOT.TH1F, binopt = 'norm').make_hist() #  using *TL
        histos['NF_AppReg_perBin'] = HistInfo(hname = 'NF_AppReg_perBin', sample = histext, binning = [bins, 0, bins], histclass = ROOT.TH1F).make_hist()
        histos['NF_SearReg_perBin'] = HistInfo(hname = 'NF_SearReg_perBin', sample = histext, binning = [bins, 0, bins], histclass = ROOT.TH1F).make_hist()
        for b in range(bins): 
            histos['NF_AppReg_perBin'].GetXaxis().SetBinLabel(b+1, binLabel[b])
            histos['NF_SearReg_perBin'].GetXaxis().SetBinLabel(b+1, binLabel[b])

        ch = SampleChain(sample, options.startfile, options.nfiles, year).getchain()
        print 'Total events of selected files of the', sample, 'sample: ', ch.GetEntries()
        n_entries = ch.GetEntries()
        #n_entries = 1000
        nevtcut = n_entries -1 if nEvents == - 1 else nEvents - 1
        print 'Running over total events: ', nevtcut+1
        for ientry in range(n_entries):
            if ientry > nevtcut: break
            if ientry % (nevtcut/10)==0 : print 'processing ', ientry,'th event'
            ch.GetEntry(ientry)
            getSel = RegSel(ch, isData, year)
            getMC = MCWeight(ch, year,s)
            if not getSel.PreSelection(lepOpt): continue
            lepid = getSel.getLooseLep(lepOpt)['idx']
            if isData:
                lumiscale = 1.0
                MCcorr = 1.0          
            else:
                lumiscale = (DataLumi) * ch.weight
                MCcorr = getMC.getTotalWeight()
                if lepOpt == 'Mu':
                    lep_promptflag = ord(ch.Muon_genPartFlav[lepid])
                    if lep_promptflag not in [ 1 , 15 ] : continue
                else:
                    lep_promptflag = ord(ch.Electron_genPartFlav[lepid])
                    if lep_promptflag not in [ 1 , 15 ] : continue
            passTrig = TrigVarSel(ch, sample).passFakeRateLepTrig_APPregion(lepOpt)
            if not passTrig: continue
            if region == 'SR':
                if not getSel.SearchRegion(lepOpt): continue
                if not getSel.looseNottight(lepid, lepOpt) : continue
                lepPt = getSel.getLooseLep(lepOpt)['pt']
                lepeta = getSel.getLooseLep(lepOpt)['eta']
                print lepPt , lepeta , getMC.getTLvalue(lepOpt , lepPt, lepeta) , MCcorr
                Fill1D(histos['NF_AppReg_all'], 1, lumiscale * MCcorr )
                Fill1D(histos['NF_SearReg_all'], 1, lumiscale * MCcorr * getMC.getTLvalue(lepOpt , lepPt, lepeta) )
 
                if getSel.SR1(lepOpt):
                    idx = findSR1BinIndex(getSel.calCT(1), getSel.getLepMT(lepOpt), getSel.getSortedLepVar()[0]['pt'],getSel.getSortedLepVar()[0]['charg'])
                    print 'SR1_idx' ,idx , getSel.calCT(1) , getSel.getLepMT(lepOpt) , getSel.getSortedLepVar()[0]['pt'] , getSel.getSortedLepVar()[0]['charg']
                    if not idx == -1:
                        Fill1D(histos['NF_AppReg_perBin'],idx, lumiscale * MCcorr)
                        Fill1D(histos['NF_SearReg_perBin'],idx, lumiscale * MCcorr * getMC.getTLvalue(lepOpt , lepPt, lepeta))
                if getSel.SR2(lepOpt):
                    idx = findSR2BinIndex(getSel.calCT(2), getSel.getLepMT(lepOpt) , getSel.getSortedLepVar()[0]['pt']) + 22
                    print 'SR2_idx' ,idx , getSel.calCT(2), getSel.getLepMT(lepOpt) , getSel.getSortedLepVar()[0]['pt']
                    if not idx == -1:
                        Fill1D(histos['NF_AppReg_perBin'],idx, lumiscale * MCcorr)
                        Fill1D(histos['NF_SearReg_perBin'],idx, lumiscale * MCcorr * getMC.getTLvalue(lepOpt , lepPt, lepeta))

            if region == 'CR':
                if not getSel.ControlRegion(lepOpt): continue
                if not getSel.looseNottight(lepid, lepOpt) : continue
                lepPt = getSel.getLooseLep(lepOpt)['pt']
                lepeta = getSel.getLooseLep(lepOpt)['eta']
                Fill1D(histos['NF_AppReg_all'], 1, lumiscale * MCcorr )
                Fill1D(histos['NF_SearReg_all'], 1, lumiscale * MCcorr * getMC.getTLvalue(lepOpt , lepPt, lepeta) )
                
                                                  
                if getSel.CR1(lepOpt):
                    print 'hiiii CR1 pass'
                    idx = findCR1BinIndex(getSel.calCT(1), getSel.getLepMT(lepOpt) , getSel.getSortedLepVar()[0]['charg'])
                    print 'CR1_idx' ,idx , getSel.calCT(1), getSel.getLepMT(lepOpt) , getSel.getSortedLepVar()[0]['charg']
                    if not idx == -1:
                        Fill1D(histos['NF_AppReg_perBin'],idx, lumiscale * MCcorr)
                        Fill1D(histos['NF_SearReg_perBin'],idx, lumiscale * MCcorr * getMC.getTLvalue(lepOpt , lepPt, lepeta))
                if getSel.CR2(lepOpt):
                    print 'hiiii CR2 pass'
                    idx = findCR2BinIndex(getSel.calCT(2), getSel.getLepMT(lepOpt)) + 6
                    print 'CR2_idx' ,idx , getSel.calCT(2), getSel.getLepMT(lepOpt)
                    if not idx == -1:
                        Fill1D(histos['NF_AppReg_perBin'],idx, lumiscale * MCcorr)
                        Fill1D(histos['NF_SearReg_perBin'],idx, lumiscale * MCcorr * getMC.getTLvalue(lepOpt , lepPt, lepeta))

            if region == 'SR+CR':
              if getSel.SearchRegion(lepOpt):
                if not getSel.looseNottight(lepid, lepOpt) : continue
                lepPt = getSel.getLooseLep(lepOpt)['pt']
                lepeta = getSel.getLooseLep(lepOpt)['eta']
                print lepPt , lepeta , getMC.getTLvalue(lepOpt , lepPt, lepeta)
                print lepPt , lepeta , getMC.getTLvalue(lepOpt , lepPt, lepeta)
                Fill1D(histos['NF_AppReg_all'], 1, lumiscale * MCcorr )
                Fill1D(histos['NF_SearReg_all'], 1, lumiscale * MCcorr * getMC.getTLvalue(lepOpt , lepPt, lepeta) )

                if getSel.SR1(lepOpt):
                    idx = findSR1BinIndex(getSel.calCT(1), getSel.getLepMT(lepOpt), getSel.getSortedLepVar()[0]['pt'],getSel.getSortedLepVar()[0]['charg'])
                    print 'SR1_idx' ,idx ,getSel.calCT(1), getSel.getLepMT(lepOpt), getSel.getSortedLepVar()[0]['pt'],getSel.getSortedLepVar()[0]['charg'] 
                    if not idx == -1:
                        Fill1D(histos['NF_AppReg_perBin'],idx, lumiscale * MCcorr)
                        Fill1D(histos['NF_SearReg_perBin'],idx, lumiscale * MCcorr * getMC.getTLvalue(lepOpt , lepPt, lepeta))

                if getSel.SR2(lepOpt):
                    idx = findSR2BinIndex(getSel.calCT(2), getSel.getLepMT(lepOpt), getSel.getSortedLepVar()[0]['pt']) + 22
                    print 'SR2_idx' ,idx , getSel.calCT(2), getSel.getLepMT(lepOpt), getSel.getSortedLepVar()[0]['pt']
                    if not idx == -1:
                        Fill1D(histos['NF_AppReg_perBin'],idx, lumiscale * MCcorr)
                        Fill1D(histos['NF_SearReg_perBin'],idx, lumiscale * MCcorr * getMC.getTLvalue(lepOpt , lepPt, lepeta))

              if  getSel.ControlRegion(lepOpt):
                if not getSel.looseNottight(lepid, lepOpt) : continue
                lepPt = getSel.getLooseLep(lepOpt)['pt']
                lepeta = getSel.getLooseLep(lepOpt)['eta']
                Fill1D(histos['NF_AppReg_all'], 1, lumiscale * MCcorr )
                Fill1D(histos['NF_SearReg_all'], 1, lumiscale * MCcorr * getMC.getTLvalue(lepOpt , lepPt, lepeta) ) 

                if getSel.CR1(lepOpt):
                    print 'hiiii CR1 pass' , getSel.getLooseLep(lepOpt)['pt']
                    idx = findCR1BinIndex(getSel.calCT(1), getSel.getLepMT(lepOpt), getSel.getSortedLepVar()[0]['charg'])
                    print 'CR1_idx' ,idx , getSel.calCT(1), getSel.getLepMT(lepOpt), getSel.getSortedLepVar()[0]['charg']
                    if not idx == -1:
                        Fill1D(histos['NF_AppReg_perBin'],idx, lumiscale * MCcorr)
                        Fill1D(histos['NF_SearReg_perBin'],idx, lumiscale * MCcorr * getMC.getTLvalue(lepOpt , lepPt, lepeta))

                if getSel.CR2(lepOpt):
                    print 'hiiii CR2 pass', getSel.getLooseLep(lepOpt)['pt']
                    idx = findCR2BinIndex(getSel.calCT(2), getSel.getLepMT(lepOpt)) + 6
                    print 'CR2_idx' ,idx, getSel.calCT(2), getSel.getLepMT(lepOpt)
                    if not idx == -1:
                        Fill1D(histos['NF_AppReg_perBin'],idx, lumiscale * MCcorr)
                        Fill1D(histos['NF_SearReg_perBin'],idx, lumiscale * MCcorr * getMC.getTLvalue(lepOpt , lepPt, lepeta))

        hfile.Write()

else:
        histext = samples
        for l in list(samplelist.values()):
            if samplelist[samples] in l: histext = list(samplelist.keys())[list(samplelist.values()).index(l)]
        sample = samples
        print 'running over: ', sample
        hfile = ROOT.TFile( 'NFHist_region_'+region+'_for_'+lepOpt+'_'+sample+'_%i_%i'%(options.startfile+1, options.startfile + options.nfiles)+'.root', 'RECREATE')
        histos = {}
        histos['NF_AppReg_all'] = HistInfo(hname = 'NF_AppReg_all', sample = histext, binning=NEventsBinning, histclass = ROOT.TH1F, binopt = 'norm').make_hist() #  no *TL
        histos['NF_SearReg_all'] = HistInfo(hname = 'NF_SearReg_all', sample = histext, binning=NEventsBinning, histclass = ROOT.TH1F, binopt = 'norm').make_hist() #  using *TL
        histos['NF_AppReg_perBin'] = HistInfo(hname = 'NF_AppReg_perBin', sample = histext, binning = [bins, 0, bins], histclass = ROOT.TH1F).make_hist()
        histos['NF_SearReg_perBin'] = HistInfo(hname = 'NF_SearReg_perBin', sample = histext, binning = [bins, 0, bins], histclass = ROOT.TH1F).make_hist()
        for b in range(bins): 
            histos['NF_AppReg_perBin'].GetXaxis().SetBinLabel(b+1, binLabel[b])
            histos['NF_SearReg_perBin'].GetXaxis().SetBinLabel(b+1, binLabel[b])

        ch = SampleChain(sample, options.startfile, options.nfiles, year).getchain()
        print 'Total events of selected files of the', sample, 'sample: ', ch.GetEntries()
        n_entries = ch.GetEntries()
        #n_entries = 1000
        nevtcut = n_entries -1 if nEvents == - 1 else nEvents - 1
        print 'Running over total events: ', nevtcut+1
        for ientry in range(n_entries):
            if ientry > nevtcut: break
            if ientry % (nevtcut/10)==0 : print 'processing ', ientry,'th event'
            ch.GetEntry(ientry)
            getSel = RegSel(ch, isData, year)
            getMC = MCWeight(ch, year,sample)
            if not getSel.PreSelection(lepOpt): continue
            lepid = getSel.getLooseLep(lepOpt)['idx']
            if isData:
                lumiscale = 1.0
                MCcorr = 1.0          
            else:
                lumiscale = (DataLumi) * ch.weight
                if ch.Pileup_nTrueInt >= 74 : 
                    count74 = count74 + 1
                    continue
                #MCcorr = get_PU_weight_2(ch.Pileup_nTrueInt)
                MCcorr = getMC.getTotalWeight()
                if lepOpt == 'Mu':
                    lep_promptflag = ord(ch.Muon_genPartFlav[lepid])
                    if lep_promptflag not in [ 1 , 15 ] : continue
                else:
                    lep_promptflag = ord(ch.Electron_genPartFlav[lepid])
                    if lep_promptflag not in [ 1 , 15 ] : continue
            passTrig = TrigVarSel(ch, sample).passFakeRateLepTrig_APPregion(lepOpt)
            if not passTrig: continue
            if region == 'SR':
                if not getSel.SearchRegion(lepOpt): continue
                if not getSel.looseNottight(lepid, lepOpt) : continue
                lepPt = getSel.getLooseLep(lepOpt)['pt']
                lepeta = getSel.getLooseLep(lepOpt)['eta']
                Fill1D(histos['NF_AppReg_all'], 1, lumiscale * MCcorr )
                Fill1D(histos['NF_SearReg_all'], 1, lumiscale * MCcorr * getMC.getTLvalue(lepOpt , lepPt, lepeta))
 
                if getSel.SR1(lepOpt):
                    idx = findSR1BinIndex(getSel.calCT(1), getSel.getLepMT(lepOpt), getSel.getSortedLepVar()[0]['pt'],getSel.getSortedLepVar()[0]['charg'])
                    print 'SR1_idx' ,idx , getSel.calCT(1) , getSel.getLepMT(lepOpt) , getSel.getSortedLepVar()[0]['pt'] , getSel.getSortedLepVar()[0]['charg']
                    if not idx == -1:
                        Fill1D(histos['NF_AppReg_perBin'],idx, lumiscale * MCcorr)
                        Fill1D(histos['NF_SearReg_perBin'],idx, lumiscale * MCcorr * getMC.getTLvalue(lepOpt , lepPt, lepeta))

                if getSel.SR2(lepOpt):
                    idx = findSR2BinIndex(getSel.calCT(2), getSel.getLepMT(lepOpt) , getSel.getSortedLepVar()[0]['pt']) + 22
                    print 'SR2_idx' ,idx , getSel.calCT(2), getSel.getLepMT(lepOpt) , getSel.getSortedLepVar()[0]['pt']
                    if not idx == -1:
                        Fill1D(histos['NF_AppReg_perBin'],idx, lumiscale * MCcorr)
                        Fill1D(histos['NF_SearReg_perBin'],idx, lumiscale * MCcorr * getMC.getTLvalue(lepOpt , lepPt, lepeta))


            if region == 'CR':
                if not getSel.ControlRegion(lepOpt): continue
                if not getSel.looseNottight(lepid, lepOpt) : continue
                lepPt = getSel.getLooseLep(lepOpt)['pt']
                lepeta = getSel.getLooseLep(lepOpt)['eta']
                Fill1D(histos['NF_AppReg_all'], 1, lumiscale * MCcorr )
                Fill1D(histos['NF_SearReg_all'], 1, lumiscale * MCcorr * getMC.getTLvalue(lepOpt , lepPt, lepeta)) 
                if getSel.CR1(lepOpt):
                    print 'hiiii CR1 pass'
                    idx = findCR1BinIndex(getSel.calCT(1), getSel.getLepMT(lepOpt) , getSel.getSortedLepVar()[0]['charg'])
                    print 'CR1_idx' ,idx , getSel.calCT(1), getSel.getLepMT(lepOpt) , getSel.getSortedLepVar()[0]['charg']
                    if not idx == -1:
                        Fill1D(histos['NF_AppReg_perBin'],idx, lumiscale * MCcorr)
                        Fill1D(histos['NF_SearReg_perBin'],idx, lumiscale * MCcorr * getMC.getTLvalue(lepOpt , lepPt, lepeta))

                if getSel.CR2(lepOpt):
                    print 'hiiii CR2 pass'
                    idx = findCR2BinIndex(getSel.calCT(2), getSel.getLepMT(lepOpt)) + 6
                    print 'CR2_idx' ,idx , getSel.calCT(2), getSel.getLepMT(lepOpt)
                    if not idx == -1:
                        Fill1D(histos['NF_AppReg_perBin'],idx, lumiscale * MCcorr)
                        Fill1D(histos['NF_SearReg_perBin'],idx, lumiscale * MCcorr * getMC.getTLvalue(lepOpt , lepPt, lepeta))

            if region == 'SR+CR':
              if getSel.SearchRegion(lepOpt):
                if not getSel.looseNottight(lepid, lepOpt) : continue
                lepPt = getSel.getLooseLep(lepOpt)['pt']
                lepeta = getSel.getLooseLep(lepOpt)['eta']
                Fill1D(histos['NF_AppReg_all'], 1, lumiscale * MCcorr )
                Fill1D(histos['NF_SearReg_all'], 1, lumiscale * MCcorr * getMC.getTLvalue(lepOpt , lepPt, lepeta))

                if getSel.SR1(lepOpt):
                    idx = findSR1BinIndex(getSel.calCT(1), getSel.getLepMT(lepOpt), getSel.getSortedLepVar()[0]['pt'],getSel.getSortedLepVar()[0]['charg'])
                    print 'SR1_idx' ,idx ,getSel.calCT(1), getSel.getLepMT(lepOpt), getSel.getSortedLepVar()[0]['pt'],getSel.getSortedLepVar()[0]['charg'] 
                    if not idx == -1:
                        Fill1D(histos['NF_AppReg_perBin'],idx, lumiscale * MCcorr)
                        Fill1D(histos['NF_SearReg_perBin'],idx, lumiscale * MCcorr * getMC.getTLvalue(lepOpt , lepPt, lepeta))

                if getSel.SR2(lepOpt):
                    idx = findSR2BinIndex(getSel.calCT(2), getSel.getLepMT(lepOpt), getSel.getSortedLepVar()[0]['pt']) + 22
                    print 'SR2_idx' ,idx , getSel.calCT(2), getSel.getLepMT(lepOpt), getSel.getSortedLepVar()[0]['pt']
                    if not idx == -1:
                        Fill1D(histos['NF_AppReg_perBin'],idx, lumiscale * MCcorr)
                        Fill1D(histos['NF_SearReg_perBin'],idx, lumiscale * MCcorr * getMC.getTLvalue(lepOpt , lepPt, lepeta))


              if  getSel.ControlRegion(lepOpt):
                if not getSel.looseNottight(lepid, lepOpt) : continue
                lepPt = getSel.getLooseLep(lepOpt)['pt']
                lepeta = getSel.getLooseLep(lepOpt)['eta']
                Fill1D(histos['NF_AppReg_all'], 1, lumiscale * MCcorr )
                Fill1D(histos['NF_SearReg_all'], 1, lumiscale * MCcorr * getMC.getTLvalue(lepOpt , lepPt, lepeta))

                if getSel.CR1(lepOpt):
                    print 'hiiii CR1 pass' , getSel.getLooseLep(lepOpt)['pt']
                    idx = findCR1BinIndex(getSel.calCT(1), getSel.getLepMT(lepOpt), getSel.getSortedLepVar()[0]['charg'])
                    print 'CR1_idx' ,idx , getSel.calCT(1), getSel.getLepMT(lepOpt), getSel.getSortedLepVar()[0]['charg']
                    if not idx == -1:
                        Fill1D(histos['NF_AppReg_perBin'],idx, lumiscale * MCcorr)
                        Fill1D(histos['NF_SearReg_perBin'],idx, lumiscale * MCcorr * getMC.getTLvalue(lepOpt , lepPt, lepeta))

                if getSel.CR2(lepOpt):
                    print 'hiiii CR2 pass', getSel.getLooseLep(lepOpt)['pt']
                    idx = findCR2BinIndex(getSel.calCT(2), getSel.getLepMT(lepOpt)) + 6
                    print 'CR2_idx' ,idx, getSel.calCT(2), getSel.getLepMT(lepOpt)
                    if not idx == -1:
                        Fill1D(histos['NF_AppReg_perBin'],idx, lumiscale * MCcorr)
                        Fill1D(histos['NF_SearReg_perBin'],idx, lumiscale * MCcorr * getMC.getTLvalue(lepOpt , lepPt, lepeta))
        hfile.Write()

