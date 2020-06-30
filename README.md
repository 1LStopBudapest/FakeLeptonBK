This repository contains the codes for fake lepton BK estimation

Basic idea is to measure the probablity of passing tight lepton selection of the loose (selcted) lepton. This is tight to loose ratio or fakerate

This loose an tight selection critaria are defined in RegSel.py

Signal region is constructed by selcting tight lepton. So by fakerate reweighting the events in application region which has same selction as signal region except the lepton selection is loose, we can estimate the fake lepton events in our signal region.

Tight-to-loose ration or fake rate is measured in separate region called measurement region which is defined in RegSel.py, and is obtained from data (JetHT)

Fake rate is calculated separetely for electron and muon channel and as a function of lepton pT in a few lepton eta bins. The denominator and numaretor histograms for the ratio are calculated by the script

FakeRatioHistMaker.py

But, we first check the loose and tight lepton pT distribution in measurement region using BK MC samples and data. This is done by following scipts

create histogram: FRStackHistMaker.py

plot eff: FRStackPlot.py

This section is evolving, so more scripts will be added soon