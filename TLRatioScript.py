import os, sys
import types


sys.path.append('../')
from Sample.SampleChain import SampleChain
from Sample.Dir import plotDir
from Sample.FileList_Fake_2016_janik  import samples as samples_2016

#samplesRun = ['WJetsToLNu_comb', 'TTSingleLep_pow', 'TTLep_pow', 'DoubleMuon_Data']
samplesRun = ['WJetsToLNu_comb', 'DYJetsToLL', 'TTLep_pow','TTSingleLep_pow' , 'DoubleMuon_Data']
fileperjobMC = 1 
fileperjobData = 1
TotJobs = 4
year = 2016
channel = 'Muon'

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
                txtline.append("python TLHistMaker.py --sample %s --channel %s --startfile %i --nfiles %i\n"%(sample, channel, i, fileperjobMC))
    else:
        tfiles = len(SampleChain.getfilelist(samplelist[sL][0]))
        fileperjob = fileperjobData if ('Run' in sL or 'Data' in sL) else fileperjobMC
        for i in range(0, tfiles, fileperjobMC):
            txtline.append("python TLHistMaker.py --sample %s  --channel %s --startfile %i --nfiles %i\n"%(sL, channel, i, fileperjobMC))
                
fout = open("TLparallelJobsubmit.txt", "w")
fout.write(''.join(txtline))
fout.close()

Rootfilesdirpath = os.path.join(plotDir,"TLHistFiles")
if not os.path.exists(Rootfilesdirpath):
    os.makedirs(Rootfilesdirpath)

bashline = []    
bashline.append("echo 'Start Running TLHistMaker.py in parallel GPU'\n\n")
bashline.append('parallel --jobs %i < TLparallelJobsubmit.txt\n'%TotJobs)
bashline.append("echo \n'Adding root files from TLHistMaker.py and moving to %s for late use'\n\n"%Rootfilesdirpath)

lepOpt = 'Ele' if 'Electron' in channel else 'Mu'

for sL in samplesRun:
    if 'Data' in sL:
        sLi = sL.replace('Data','')+'Run'
        bashline.append('hadd TLHist_%s_%s.root TLHist_%s_%s*.root\n'%(lepOpt, sL, lepOpt, sLi))
    elif isinstance(samplelist[sL][0], types.ListType):
        sLi = 'hadd TLHist_'+lepOpt+'_'+sL+'.root'+str("".join(' TLHist_'+lepOpt+'_'+list(samplelist.keys())[list(samplelist.values()).index(s)]+'*.root' for s in samplelist[sL]))
        bashline.append('%s\n'%sLi)
    else:
        bashline.append('hadd TLHist_%s_%s.root TLHist_%s_%s_*.root\n'%(lepOpt, sL, lepOpt, sL))
    bashline.append('mv TLHist_%s_%s.root %s\n'%(lepOpt, sL, Rootfilesdirpath))

l = str(" ".join(s for s in samplesRun))
bashline.append('python TLRatioPlot.py -l %s -c %s'%(l, channel))
    
fsh = open("TLRatio.sh", "w")
fsh.write(''.join(bashline))
fsh.close()
os.system('chmod 744 TLRatio.sh')
os.system('./TLRatio.sh')
os.system('mv *.root TLparallelJobsubmit.txt TLRatio.sh /home/mmoussa/susy/fake_rate_results/root_txt_sh_files_TLRatio/')

