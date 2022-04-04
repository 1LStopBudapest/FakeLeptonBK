import os, sys
import types


sys.path.append('../')
from Sample.SampleChain import SampleChain
from Sample.Dir import plotDir
#from Sample.FileList_Fake_2016_janik  import samples as samples_2016
from Sample.FileList_2016 import samples as samples_2016

#samplesRun = ['WJetsToLNu_comb', 'TTSingleLep_pow', 'TTLep_pow', 'DoubleMuon_Data']
samplesRun = ['UL16PreVFP_WJetsToLNu', 'UL16PreVFP_DYJetsToLL', 'UL16PreVFP_TTLep_pow', 'UL16PreVFP_TTSingleLep_pow' ,'UL16PreVFP_MET_Data']
fileperjobMC = 1 
fileperjobData = 1
TotJobs = 4
year = 2016
channel = 'Muon'
region = 'SR'
txtline = []

if year==2016:
    samplelist = samples_2016
elif year==2017:
    samplelist = samples_2017
else:
    samplelist = samples_2018

for sL in samplesRun:
    if isinstance(samplelist[sL][0], types.ListType):
        for s in samplelist[sL]:
            sample = list(samplelist.keys())[list(samplelist.values()).index(s)]
            fileperjob = fileperjobData if ('Run' in sample or 'Data' in sample) else fileperjobMC
            tfiles = len(SampleChain.getfilelist(samplelist[sample][0]))
            for i in range(0, tfiles, fileperjobMC):
                txtline.append("python NF_SR_HistMaker.py --sample %s --channel %s --startfile %i --nfiles %i --region %s \n"%(sample, channel, i, fileperjobMC , region))
    else:
        tfiles = len(SampleChain.getfilelist(samplelist[sL][0]))
        fileperjob = fileperjobData if ('Run' in sL or 'Data' in sL) else fileperjobMC
        for i in range(0, tfiles, fileperjobMC):
            txtline.append("python NF_SR_HistMaker.py --sample %s  --channel %s --startfile %i --nfiles %i --region %s \n"%(sL, channel, i, fileperjobMC , region ))
                
fout = open("NFparallelJobsubmit.txt", "w")
fout.write(''.join(txtline))
fout.close()

Rootfilesdirpath = os.path.join(plotDir,"NFHistFiles")
if not os.path.exists(Rootfilesdirpath):
    os.makedirs(Rootfilesdirpath)

bashline = []    
bashline.append("echo 'Start Running NF_SR_HistMaker.py in parallel GPU'\n\n")
bashline.append('parallel --jobs %i < NFparallelJobsubmit.txt\n'%TotJobs)
bashline.append("echo \n'Adding root files from NF_SR_HistMaker.py and moving to %s for late use'\n\n"%Rootfilesdirpath)

lepOpt = 'Ele' if 'Electron' in channel else 'Mu'

for sL in samplesRun:
    if 'Data' in sL:
        sLi = sL.replace('Data','')+'Run'
        bashline.append('hadd NFHist_region_%s_for_%s_%s.root NFHist_region_%s_for_%s_%s*.root\n'%(region, lepOpt, sL, region , lepOpt, sLi))
    elif isinstance(samplelist[sL][0], types.ListType):
        sLi = 'hadd NFHist_region_'+region+'_for_'+lepOpt+'_'+sL+'.root'+str("".join(' NFHist_region_'+region+'_for_'+lepOpt+'_'+list(samplelist.keys())[list(samplelist.values()).index(s)]+'*.root' for s in samplelist[sL]))
        bashline.append('%s\n'%sLi)
    else:
        bashline.append('hadd NFHist_region_%s_for_%s_%s.root NFHist_region_%s_for_%s_%s*.root\n'%(region,lepOpt, sL,region, lepOpt, sL))
    bashline.append('mv NFHist_region_%s_for_%s_%s.root %s\n'%(region,lepOpt, sL, Rootfilesdirpath))

l = str(" ".join(s for s in samplesRun))
bashline.append('python NF_SR_Plots.py -l %s -c %s -r %s'%(l, channel , region))
    
fsh = open("NF_SR.sh", "w")
fsh.write(''.join(bashline))
fsh.close()
os.system('chmod 744 NF_SR.sh')

os.system('./NF_SR.sh')
os.system('mv *.root NFparallelJobsubmit.txt NF_SR.sh /home/mmoussa/susy/fake_rate_results/root_txt_sh_files_NF_SR/')

