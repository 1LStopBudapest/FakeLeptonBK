import ROOT
import math
import os, sys
import collections as coll

sys.path.append('../')
from Helper.VarCalc import *

class RegSel():
    
    def __init__(self, tr, isData, yr):
        self.tr = tr
        self.yr = yr
        self.isData = isData
        
    #selection
    def MsrmntReg(self, lep):
        reg = self.MsrMETcut() and self.Msrlepcut(lep) and self.MsrMTcut(lep) and self.MsrJetGoodCleancut()
        return reg
    
    def MsrMETcut(self):
        cut = False
        if self.tr.MET_pt < 50: # it was 40
            cut = True
        return cut

    def EWKTempMETcut(self):
        cut = False
        if self.tr.MET_pt > 50:
            cut = True
        return cut
    
    def MsrMTcut(self, lep):
        MT = self.getMuMT('Loose') if lep=='Mu' else self.getLooseEleMT('Loose')
        return MT<40   # return true if mt < 40 and false if mt>=40 it was 30
        #return MT<1000

    def MsrMT(self, lep, lp='Loose'):
        MT = self.getMuMT(lp) if lep=='Mu' else self.getEleMT(lp)
        return MT

    def Msrlepcut(self, lep):
        return len(self.selectLooseMuIdx())==1 if lep=='Mu' else len(self.selectLooseEleIdx()) == 1 #true if len is >=1 for Janik only =1

    def EWKlepcut(self, lep):
        return len(self.selectTightMuIdx())==1 if lep=='Mu' else len(self.selectTightEleIdx()) == 1 #true if len is >=1 for Janik only =1
    
    def MsrJetGoodCleancut(self):
        return len(self.selectLepCleanGoodJetIdx(lp='Loose'))>=1

    def EWKJetGoodCleancut(self):
        return len(self.selectLepCleanGoodJetIdx(lp='Tight'))>=1 
        
    def selectLepCleanGoodJetIdx(self, lp, thrsld=40):
        if 'Loose' in lp:
            lepvarL = sortedlist(self.getLepVar(self.selectLooseMuIdx(),self.selectLooseEleIdx()))
        else:
            lepvarL = sortedlist(self.getLepVar(self.selectTightMuIdx(),self.selectTightEleIdx()))
        idx = []
        d = {}
        for j in range(len(self.tr.JetGood_pt)):
            clean = False
            if self.tr.JetGood_pt[j] > thrsld and abs(self.tr.Jet_eta[j]) < 2.4 and self.tr.JetGood_jetId[j] > 0:
                clean = True
                for l in range(len(lepvarL)):  #the condition of cleaning jet?
                    dR = DeltaR(lepvarL[l]['eta'], lepvarL[l]['phi'], self.tr.JetGood_eta[j], self.tr.JetGood_phi[j])
                    ptRatio = float(self.tr.JetGood_pt[j])/float(lepvarL[l]['pt'])
                    if dR < 0.4 and ptRatio < 2:
                        clean = False
                        break
                if clean:
                    d[self.tr.JetGood_pt[j]] = j
        od = coll.OrderedDict(sorted(d.items(), reverse=True))
        for jetgoodpt in od:
            idx.append(od[jetgoodpt])
        return idx
    
    
    def getLooseMu(self):
        muvarL = sortedlist(self.getMuVar(self.selectLooseMuIdx())) # sort from high to small according to pt in varCalc.py
        return muvarL[0]
        
    def getLooseEle(self):
        elevarL = sortedlist(self.getEleVar(self.selectLooseEleIdx()))
        return elevarL[0]

    def getLooseLep(self, lep):
        return self.getLooseMu() if lep=='Mu' else self.getLooseEle()
    
    
    def getMuMT(self, lp):
        if 'Loose' in lp:        
            muvar = sortedlist(self.getMuVar(self.selectLooseMuIdx()))
        else:
            muvar = sortedlist(self.getMuVar(self.selectTightMuIdx()))
        return MT(muvar[0]['pt'], muvar[0]['phi'], self.tr.MET_pt, self.tr.MET_phi) if len(muvar) else 0

    def getEleMT(self, lp):
        if 'Loose' in lp:
            elevar = sortedlist(self.getEleVar(self.selectLooseEleIdx()))
        else:
            elevar = sortedlist(self.getEleVar(self.selectTightEleIdx()))
        return MT(elevar[0]['pt'], elevar[0]['phi'], self.tr.MET_pt, self.tr.MET_phi) if len(elevar) else 0
        
    def getMuVar(self, muId):
        Llist = []
        for id in muId:
            Llist.append({'pt':self.tr.Muon_pt[id], 'eta':self.tr.Muon_eta[id], 'phi':self.tr.Muon_phi[id], 'dxy':self.tr.Muon_dxy[id], 'dz': self.tr.Muon_dz[id], 'idx':id})
        return Llist

    def getEleVar(self, eId):
        Llist = []
        for id in eId:
            Llist.append({'pt':self.tr.Electron_pt[id], 'eta':self.tr.Electron_eta[id], 'phi':self.tr.Electron_phi[id], 'dxy':self.tr.Electron_dxy[id], 'dz': self.tr.Electron_dz[id], 'idx':id})
        return Llist
    
    def getLepVar(self, muId, eId):
        Llist = []
        for id in muId:
            Llist.append({'pt':self.tr.Muon_pt[id], 'eta':self.tr.Muon_eta[id], 'phi':self.tr.Muon_phi[id], 'dxy':self.tr.Muon_dxy[id], 'dz': self.tr.Muon_dz[id], 'idx':id})
        for id in eId:
            Llist.append({'pt':self.tr.Electron_pt[id], 'eta':self.tr.Electron_eta[id], 'phi':self.tr.Electron_phi[id], 'dxy':self.tr.Electron_dxy[id], 'dz': self.tr.Electron_dz[id], 'idx':id})
        return Llist
    
    def selectLooseMuIdx(self):
        idx = []
        for i in range(len(self.tr.Muon_pt)):
            if self.muonSelector(pt=self.tr.Muon_pt[i], eta=self.tr.Muon_eta[i],iso=self.tr.Muon_pfRelIso03_all[i], dxy=self.tr.Muon_dxy[i], dz=self.tr.Muon_dz[i], Id=self.tr.Muon_looseId[i], lepton_selection='looseHybridIso'):
                idx.append(i)
        return idx

    def selectTightMuIdx(self):
        idx = []
        for i in range(len(self.tr.Muon_pt)):
            if self.muonSelector(pt=self.tr.Muon_pt[i], eta=self.tr.Muon_eta[i],iso=self.tr.Muon_pfRelIso03_all[i], dxy=self.tr.Muon_dxy[i], dz=self.tr.Muon_dz[i], Id=self.tr.Muon_looseId[i], lepton_selection='HybridIso'):
                idx.append(i)
        return idx
    
    def selectLooseEleIdx(self):
        idx = []
        for i in range(len(self.tr.Electron_pt)):
            if self.eleSelector(pt=self.tr.Electron_pt[i], eta=self.tr.Electron_eta[i], iso=self.tr.Electron_pfRelIso03_all[i], dxy=self.tr.Electron_dxy[i], dz=self.tr.Electron_dz[i], Id=self.tr.Electron_vidNestedWPBitmap[i],lepton_selection='looseHybridIso'):
                idx.append(i)              
	return idx

    def selectTightEleIdx(self):
        idx = []
        for i in range(len(self.tr.Electron_pt)):
            if self.eleSelector(pt=self.tr.Electron_pt[i], eta=self.tr.Electron_eta[i], iso=self.tr.Electron_pfRelIso03_all[i], dxy=self.tr.Electron_dxy[i], dz=self.tr.Electron_dz[i], Id=self.tr.Electron_vidNestedWPBitmap[i],lepton_selection='HybridIso'):
                idx.append(i)              
	return idx
    
    def muonSelector( self, pt, eta, iso, dxy, dz, Id = True, lepton_selection='HybridIso', year=2016):
        if lepton_selection == 'HybridIso':
            def func():
                if pt <= 25 and pt >3.5:
                    return \
                        abs(eta)       < 2.4 \
                        and (iso* pt) <= 5.0 \
                        and abs(dxy)       < 0.02 \
                        and abs(dz)        < 0.1 \
                        and Id
                elif pt > 25:
                    return \
                        abs(eta)       < 2.4 \
                        and iso < 0.2 \
                        and abs(dxy)       < 0.02 \
                        and abs(dz)        < 0.1 \
                        and Id
            
        elif lepton_selection == 'looseHybridIso':
            def func():
                if pt <= 25 and pt >3.5:
                    return \
                        abs(eta)       < 2.4 \
                        and (iso*pt) <= 20.0 \
                        and abs(dxy)       < 0.1 \
                        and abs(dz)        < 0.5 \
                        and Id
                elif pt > 25:
                    return \
                        abs(eta)       < 2.4 \
                        and iso < 0.8 \
                        and abs(dxy)       < 0.1 \
                        and abs(dz)        < 0.5 \
                        and Id
        else:
            def func():
                return \
                    pt >3.5 \
                    and abs(eta)       < 2.4 \
                    and Id
       
        return func()


    def eleSelector(self, pt, eta, iso, dxy, dz, Id, lepton_selection='HybridIso', year=2016):
        if lepton_selection == 'HybridIso':  # tight selection for fake rate
            def func():
                if pt <= 25 and pt >5:
                    return \
                        abs(eta)       < 2.5 \
                        and (iso* pt) <= 5.0 \
                        and abs(dxy)       < 0.02 \
                        and abs(dz)        < 0.1 \
                        and eleVID(Id, 1, removedCuts=['pfRelIso03_all']) #cutbased id: 0:fail, 1:veto, 2:loose, 3:medium, 4:tight
                elif pt > 25:
                    return \
                        abs(eta)       < 2.5 \
                        and iso < 0.2 \
                        and abs(dxy)       < 0.02 \
                        and abs(dz)        < 0.1 \
                        and eleVID(Id,1, removedCuts=['pfRelIso03_all'])

        elif lepton_selection == 'looseHybridIso':
            def func():
                if pt <= 25 and pt >5:
                    return \
                        abs(eta)       < 2.5 \
                        and (iso*pt) <= 20.0 \
                        and abs(dxy)       < 0.1 \
                        and abs(dz)        < 0.5 \
                        and eleVID(Id, 1, removedCuts=['pfRelIso03_all']) #cutbased id: 0:fail, 1:veto, 2:loose, 3:medium, 4:tight
                elif pt > 25:
                    return \
                        abs(eta)       < 2.5 \
                        and iso < 0.8 \
                        and abs(dxy)       < 0.1 \
                        and abs(dz)        < 0.5 \
                        and eleVID(Id, 1, removedCuts=['pfRelIso03_all']) #cutbased id: 0:fail, 1:veto, 2:loose, 3:medium, 4:tight

        else:
            def func():
                return \
                    pt >5 \
                    and abs(eta)       < 2.5 \
                    and eleVID(Id,1, removedCuts=['pfRelIso03_all'])
        return func()  
  
    def loosepasstight(self, idx, lep):
        lt = False
        if lep=='Mu':
            if self.muonSelector(self.tr.Muon_pt[idx], self.tr.Muon_eta[idx], self.tr.Muon_pfRelIso03_all[idx], self.tr.Muon_dxy[idx], self.tr.Muon_dz[idx],self.tr.Muon_looseId[idx], 'HybridIso'):
                lt = True
        else:
            if self.eleSelector(self.tr.Electron_pt[idx], self.tr.Electron_eta[idx], self.tr.Electron_pfRelIso03_all[idx], self.tr.Electron_dxy[idx], self.tr.Electron_dz[idx], self.tr.Electron_vidNestedWPBitmap[idx],'HybridIso'):
                lt = True

        return lt    
  
    def looseNottight(self, idx, lep):
        lt = True
        if lep=='Mu':
            if self.muonSelector(self.tr.Muon_pt[idx], self.tr.Muon_eta[idx], self.tr.Muon_pfRelIso03_all[idx], self.tr.Muon_dxy[idx], self.tr.Muon_dz[idx],self.tr.Muon_looseId[idx], 'HybridIso'):
                lt = False
        else:
            if self.eleSelector(self.tr.Electron_pt[idx], self.tr.Electron_eta[idx], self.tr.Electron_pfRelIso03_all[idx], self.tr.Electron_dxy[idx], self.tr.Electron_dz[idx], self.tr.Electron_vidNestedWPBitmap[idx],'HybridIso'):
                lt = False

        return lt    
  
  
  
    
    '''
    def PreSelection(self):
        ps = self.METcut() and self.HTcut() and self.ISRcut() and self.lepcut() and self.dphicut() and self.XtralepVeto() and self.XtraJetVeto() and self.tauVeto()
        return ps

    def SearchRegion(self):
        if not self.PreSelection():
            return False
        else:
            lepvar = sortedlist(self.getLepVar(self.selectMuIdx(), self.selectEleIdx()))
            if len(lepvar) > 1 and lepvar[0]['pt']<=30:
                return True
            else:
                return False
    def SR1(self):
        if not self.SearchRegion():
            return False
        else:
            return True if self.cntBtagjet(30)==0 and self.cntBtagjet(60)==0 and self.calCT(1)>300 and abs(sortedlist(self.getLepVar(self.selectMuIdx(), self.selectEleIdx()))[0]['eta']) < 1.5 else False

    def SR2(self):
        if not self.SearchRegion():
            return False
        else:
            return True if self.cntBtagjet(30)>=1 and self.cntBtagjet(60)==0 and self.calCT(2)>300  else False

    
    def ControlRegion(self):
        if not self.PreSelection():
            return False
        else:
            lepvar = sortedlist(self.getLepVar(self.selectMuIdx(), self.selectEleIdx()))
            if len(lepvar) > 1 and lepvar[0]['pt']>30:
                return True
            else:
                return False

    def CR1(self):
        if not self.ControlRegion():
            return False
        else:
            return True if self.cntBtagjet(30)==0 and self.cntBtagjet(60)==0 and self.calCT(1)>300 and abs(sortedlist(self.getLepVar(self.selectMuIdx(), self.selectEleIdx()))[0]['eta']) < 1.5 else False

    def CR2(self):
        if not self.ControlRegion():
            return False
        else:
            return True if self.cntBtagjet(30)>=1 and self.cntBtagjet(60)==0 and self.calCT(2)>300  else False
                

    #cuts
    def ISRcut(self, thr=100):
        return len(self.selectISRjetIdx(thr))>0

    def METcut(self):
        cut = False
        if self.tr.MET_pt >200:
            cut = True
        return cut

    def MsrMETcut(self):
        cut = False
        if self.tr.MET_pt < 50: # it was 40 
            cut = True
        return cut
        
    def HTcut(self, thr=300, jetpt=30):
        cut = False
        HT = self.calHT(jetpt)
        if HT >thr:
            cut = True
        return cut
   
    def MsrHTcut(self, jetpt=40): # it was 30
        cut = False
        HT = self.calHT(jetpt)
        if HT > 900:
            cut = True
        return cut
    
    def dphicut(self):
        cut = False
        if len(self.selectjetIdx(30)) >=2 and self.tr.JetGood_pt[self.selectjetIdx(30)[1]]> 60:
            if DeltaPhi(self.tr.JetGood_phi[self.selectjetIdx(30)[0]], self.tr.JetGood_phi[self.selectjetIdx(30)[1]])<2.5:
                cut = True
        return cut

    def lepcut(self):
        return len(self.getLepVar(self.selectMuIdx(), self.selectEleIdx())) >= 1

    def Msrlepcut(self, lep):
        return len(self.selectLooseMuIdx())>=1 if lep=='Mu' else len(self.selectLooseEleIdx()) >= 1 #true if len is >=1 for Janik only =1
    
    def SingleElecut(self):
        return self.cntEle()>=1 and self.cntMuon()==0

    def SingleMuoncut(self):
        return self.cntMuon()>=1 and self.cntEle()==0
    
    def XtralepVeto(self):
        cut = True
        lepvar = sortedlist(self.getLepVar(self.selectMuIdx(), self.selectEleIdx()))
        if len(lepvar) > 1 and lepvar[1]['pt']>20:
            cut = False
        return cut

    def XtraJetVeto(self):
        cut = True
        if len(self.selectjetIdx(30)) >=3 and self.tr.JetGood_pt[self.selectjetIdx(30)[2]]> 60:
            cut = False
        return cut

    def tauVeto(self):
        cut = True
        if self.tr.nTau>=1:#only applicable to postprocessed sample where lepton(e,mu)-cleaned (dR<0.4) tau collection is stored
            cut = False
        return cut


    def MsrMTcut(self, lep):
        MT = self.getLooseMuMT() if lep=='Mu' else self.getLooseEleMT()
        return MT<40   # return true if mt < 40 and false if mt>=40 it was 30

    #var
    def getLooseMu(self):
        muvarL = sortedlist(self.getMuVar(self.selectLooseMuIdx())) # sort from high to small according to pt in varCalc.py
        return muvarL[0]
        
    def getLooseEle(self):
        elevarL = sortedlist(self.getEleVar(self.selectLooseEleIdx()))
        return elevarL[0]

    def getLooseLep(self, lep):
        return self.getLooseMu() if lep=='Mu' else self.getLooseEle()

    def loosepasstight(self, idx, lep):
        lt = False
        if lep=='Mu':
            if self.muonSelector(self.tr.Muon_pt[idx], self.tr.Muon_eta[idx], self.tr.Muon_pfRelIso03_all[idx], self.tr.Muon_dxy[idx], self.tr.Muon_dz[idx], 'HybridIso'):
                lt = True
        else:
            if self.eleSelector(self.tr.Electron_pt[idx], self.tr.Electron_eta[idx], self.tr.Electron_pfRelIso03_all[idx], self.tr.Electron_dxy[idx], self.tr.Electron_dz[idx], self.tr.Electron_cutBased_Fall17_V1[idx],'HybridIso'):
                lt = True

        return lt

            
    def getLepMT(self):
        lepvar = sortedlist(self.getLepVar(self.selectMuIdx(), self.selectEleIdx()))
        return MT(lepvar[0]['pt'], lepvar[0]['phi'], self.tr.MET_pt, self.tr.MET_phi) if len(lepvar) else 0

    def getLooseMuMT(self):
        muvar = sortedlist(self.getMuVar(self.selectLooseMuIdx()))
        return MT(muvar[0]['pt'], muvar[0]['phi'], self.tr.MET_pt, self.tr.MET_phi) if len(muvar) else 0

    def getLooseEleMT(self):
        elevar = sortedlist(self.getEleVar(self.selectLooseEleIdx()))
        return MT(elevar[0]['pt'], elevar[0]['phi'], self.tr.MET_pt, self.tr.MET_phi) if len(elevar) else 0
    

    def calCT(self, i):
        return CT1(self.tr.MET_pt, self.calHT()) if i==1 else CT2(self.tr.MET_pt, self.getISRPt())
        
    def calHT(self, thr):
        HT = 0
        for i in self.selectjetIdx(thr):
            HT = HT + self.tr.JetGood_pt[i]
        return HT

    def calNj(self, thrsld):
        return len(self.selectjetIdx(thrsld))
        
    def getISRPt(self):
        return self.tr.JetGood_pt[self.selectISRjetIdx()[0]] if len(self.selectISRjetIdx()) else 0
    
    def cntBtagjet(self, discOpt='CSVV2', ptthrsld=30):
        return len(self.selectBjetIdx(discOpt, ptthrsld))

    def cntMuon(self):
        return len(self.selectMuIdx())

    def	cntEle(self):
    	return len(self.selectEleIdx())
    
    def selectjetIdx(self, thrsld=40): # it was 30
        idx = []
        for i in range(len(self.tr.JetGood_pt)):
            if self.tr.JetGood_pt[i]>thrsld and abs(self.tr.JetGood_eta[i])<2.4:
                idx.append(i)
        return idx

    def selectISRjetIdx(self, thrsld=100):
        idx = []
        for i in range(len(self.tr.JetGood_pt)):
            if self.tr.JetGood_pt[i]>thrsld and abs(self.tr.JetGood_eta[i])<2.4:
                idx.append(i)
        return idx

    def selectBjetIdx(self, discOpt='DeepCSV', ptthrsld=30):
        idx = []
        for i in range(len(self.tr.JetGood_pt)):
            if self.tr.JetGood_pt[i]>ptthrsld and abs(self.tr.JetGood_eta[i])<2.4:
                if (self.isBtagCSVv2(self.tr.JetGood_btagCSVV2[i], self.yr) if discOpt == 'CSVV2' else self.isBtagDeepCSV(self.tr.JetGood_btagDeepB[i], self.yr)):
                    idx.append(i)
        return idx

    def	selectEleIdx(self):
        idx = []
        for i in range(len(self.tr.Electron_pt)):
            if self.eleSelector(pt=self.tr.Electron_pt[i], eta=self.tr.Electron_eta[i], iso=self.tr.Electron_pfRelIso03_all[i], dxy=self.tr.Electron_dxy[i], dz=self.tr.Electron_dz[i], Id=self.tr.Electron_vidNestedWPBitmap[i][i],lepton_selection='HybridIso'):
                idx.append(i)              
	return idx

    def	selectLooseEleIdx(self):
        idx = []
        for i in range(len(self.tr.Electron_pt)):
            if self.eleSelector(pt=self.tr.Electron_pt[i], eta=self.tr.Electron_eta[i], iso=self.tr.Electron_pfRelIso03_all[i], dxy=self.tr.Electron_dxy[i], dz=self.tr.Electron_dz[i], Id=self.tr.Electron_vidNestedWPBitmap[i],lepton_selection='looseHybridIso'):
                idx.append(i)              
	return idx
    

    def selectMuIdx(self):
        idx = []
        for i in range(len(self.tr.Muon_pt)):
            if self.muonSelector(pt=self.tr.Muon_pt[i], eta=self.tr.Muon_eta[i], iso=self.tr.Muon_pfRelIso03_all[i], dxy=self.tr.Muon_dxy[i], dz=self.tr.Muon_dz[i], Id=self.tr.Muon_looseId[i], lepton_selection='HybridIso'):
                idx.append(i)
        return idx

    def selectLooseMuIdx(self):
        idx = []
        for i in range(len(self.tr.Muon_pt)):
            if self.muonSelector(pt=self.tr.Muon_pt[i], eta=self.tr.Muon_eta[i],iso=self.tr.Muon_pfRelIso03_all[i], dxy=self.tr.Muon_dxy[i], dz=self.tr.Muon_dz[i], Id=self.tr.Muon_looseId[i], lepton_selection='looseHybridIso'):
                idx.append(i)
        return idx
    
    def getMuVar(self, muId):
        Llist = []
        for id in muId:
            Llist.append({'pt':self.tr.Muon_pt[id], 'eta':self.tr.Muon_eta[id], 'phi':self.tr.Muon_phi[id], 'dxy':self.tr.Muon_dxy[id], 'dz': self.tr.Muon_dz[id], 'idx':id})
        return Llist

    def getEleVar(self, eId):
        Llist = []
        for id in eId:
            Llist.append({'pt':self.tr.Electron_pt[id], 'eta':self.tr.Electron_eta[id], 'phi':self.tr.Electron_phi[id], 'dxy':self.tr.Electron_dxy[id], 'dz': self.tr.Electron_dz[id], 'idx':id})
        return Llist
    
    def getLepVar(self, muId, eId):
        Llist = []
        for id in muId:
            Llist.append({'pt':self.tr.Muon_pt[id], 'eta':self.tr.Muon_eta[id], 'phi':self.tr.Muon_phi[id], 'dxy':self.tr.Muon_dxy[id], 'dz': self.tr.Muon_dz[id], 'idx':id})
        for id in eId:
            Llist.append({'pt':self.tr.Electron_pt[id], 'eta':self.tr.Electron_eta[id], 'phi':self.tr.Electron_phi[id], 'dxy':self.tr.Electron_dxy[id], 'dz': self.tr.Electron_dz[id], 'idx':id})
        return Llist

    def isBtagDeepCSV(self, jetb, year):
        if year == 2016:
            return jetb > 0.6321
        elif year == 2017:
            return jetb > 0.4941
        elif year == 2018:
            return jetb > 0.4184
        else:
            return True

    def isBtagCSVv2(self, jetb, year):
        if year == 2016:
            return jetb > 0.8484
        elif year == 2017 or year == 2018:
            return jetb > 0.8838
        else:
            return True
        

    def muonSelector( self, pt, eta, iso, dxy, dz, Id = True, lepton_selection='HybridIso', year=2016):
        if lepton_selection == 'HybridIso':
            def func():
                if pt <= 25 and pt >3.5:
                    return \
                        abs(eta)       < 2.4 \
                        and (iso* pt) <= 5.0 \   # absolute iso = relative iso * pt
                        and abs(dxy)       < 0.02 \
                        and abs(dz)        < 0.1 \
                        and Id
                elif pt > 25:
                    return \
                        abs(eta)       < 2.4 \
                        and iso < 0.2 \
                        and abs(dxy)       < 0.02 \
                        and abs(dz)        < 0.1 \
                        and Id
            
        elif lepton_selection == 'looseHybridIso':
            def func():
                if pt <= 25 and pt >3.5:
                    return \
                        abs(eta)       < 2.4 \
                        and (iso*pt) <= 20.0 \
                        and abs(dxy)       < 0.1 \
                        and abs(dz)        < 0.5 \
                        and Id
                elif pt > 25:
                    return \
                        abs(eta)       < 2.4 \
                        and iso < 0.8 \
                        and abs(dxy)       < 0.1 \
                        and abs(dz)        < 0.5 \
                        and Id
        else:
            def func():
                return \
                    pt >3.5 \
                    and abs(eta)       < 2.4 \
                    and Id
       
        return func()


    def eleSelector(self, pt, eta, iso, dxy, dz, Id, lepton_selection='HybridIso', year=2016):
        if lepton_selection == 'HybridIso':  # tight selection for fake rate
            def func():
                if pt <= 25 and pt >5:
                    return \
                        abs(eta)       < 2.5 \
                        and (iso* pt) <= 5.0 \
                        and abs(dxy)       < 0.02 \
                        and abs(dz)        < 0.1 \
                        and eleVID(Id, 1, removedCuts=['pfRelIso03_all']) #cutbased id: 0:fail, 1:veto, 2:loose, 3:medium, 4:tight
                elif pt > 25:
                    return \
                        abs(eta)       < 2.5 \
                        and iso < 0.2 \
                        and abs(dxy)       < 0.02 \
                        and abs(dz)        < 0.1 \
                        and self.eleID(Id,1)

        elif lepton_selection == 'looseHybridIso':
            def func():
                if pt <= 25 and pt >5:
                    return \
                        abs(eta)       < 2.5 \
                        and (iso*pt) <= 20.0 \
                        and abs(dxy)       < 0.1 \
                        and abs(dz)        < 0.5 \
                        and eleVID(Id, 1, removedCuts=['pfRelIso03_all']) #cutbased id: 0:fail, 1:veto, 2:loose, 3:medium, 4:tight
                elif pt > 25:
                    return \
                        abs(eta)       < 2.5 \
                        and iso < 0.8 \
                        and abs(dxy)       < 0.1 \
                        and abs(dz)        < 0.5 \
                        and eleVID(Id, 1, removedCuts=['pfRelIso03_all']) #cutbased id: 0:fail, 1:veto, 2:loose, 3:medium, 4:tight

        else:
            def func():
                return \
                    pt >5 \
                    and abs(eta)       < 2.5 \
                    and self.eleID(Id,1)
        return func()



    def eleID(self, idval, idtype):
        return idval==idtype

    
    def genEle(self):
        L = []
        for i in range(self.tr.nGenPart):
            if abs(self.tr.GenPart_pdgId[i]) ==11 and GenFlagString(self.tr.GenPart_statusFlags[i])[-1]=='1' and GenFlagString(self.tr.GenPart_statusFlags[i])[6]=='1' and self.tr.GenPart_status[i]==1 and self.tr.GenPart_genPartIdxMother[i] != -1:
                if abs(self.tr.GenPart_pdgId[self.tr.GenPart_genPartIdxMother[i]])!=21:
                    L.append({'pt':self.tr.GenPart_pt[i], 'eta':self.tr.GenPart_eta[i], 'phi':self.tr.GenPart_phi[i]})
        return L

    def genMuon(self):
        L = []
        for i in range(self.tr.nGenPart):
            if abs(self.tr.GenPart_pdgId[i]) ==13 and GenFlagString(self.tr.GenPart_statusFlags[i])[-1]=='1' and GenFlagString(self.tr.GenPart_statusFlags[i])[6]=='1' and self.tr.GenPart_status[i]==1 and self.tr.GenPart_genPartIdxMother[i] != -1:
                if abs(self.tr.GenPart_pdgId[self.tr.GenPart_genPartIdxMother[i]])!=22:
                    L.append({'pt':self.tr.GenPart_pt[i], 'eta':self.tr.GenPart_eta[i], 'phi':self.tr.GenPart_phi[i]})
        return L
    '''
