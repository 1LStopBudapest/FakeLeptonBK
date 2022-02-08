import os, sys
import types


sys.path.append('../')
from Sample.SampleChain import SampleChain
from Sample.Dir import plotDir
from Sample.FileList_Fake_2016_janik  import samples as samples_2016

samplesRun = [ 'DYJetsToLL', 'WJetsToLNu_comb', 'TTLep_pow' , 'TTSingleLep_pow' , 'QCD', 'DoubleMuon_Data']
#samplesRun = ['QCD', 'WJetsToLNu_comb' , 'DoubleMuon_Data']
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
                txtline.append("python FRStackHistMaker.py --sample %s --channel %s --startfile %i --nfiles %i\n"%(sample, channel, i, fileperjobMC))
    else:
        tfiles = len(SampleChain.getfilelist(samplelist[sL][0]))
        fileperjob = fileperjobData if ('Run' in sL or 'Data' in sL) else fileperjobMC
        for i in range(0, tfiles, fileperjobMC):
            txtline.append("python FRStackHistMaker.py --sample %s  --channel %s --startfile %i --nfiles %i\n"%(sL, channel, i, fileperjobMC))
                
fout = open("parallelJobsubmit.txt", "w")
fout.write(''.join(txtline))
fout.close()

Rootfilesdirpath = os.path.join(plotDir,"FRStackFiles")
if not os.path.exists(Rootfilesdirpath):
    os.makedirs(Rootfilesdirpath)

bashline = []    
bashline.append('parallel --jobs %i < parallelJobsubmit.txt\n'%TotJobs)

lepOpt = 'Ele' if 'Electron' in channel else 'Mu'

for sL in samplesRun:
    if 'Data' in sL:
        sLi = sL.replace('Data','')+'Run'
        bashline.append('hadd FRStackHist_%s_%s.root FRStackHist_%s_%s*.root\n'%(lepOpt, sL, lepOpt, sLi))
    elif isinstance(samplelist[sL][0], types.ListType):
        sLi = 'hadd FRStackHist_'+lepOpt+'_'+sL+'.root'+str("".join(' FRStackHist_'+lepOpt+'_'+list(samplelist.keys())[list(samplelist.values()).index(s)]+'*.root' for s in samplelist[sL]))
        bashline.append('%s\n'%sLi)
    else:
        bashline.append('hadd FRStackHist_%s_%s.root FRStackHist_%s_%s_*.root\n'%(lepOpt, sL, lepOpt, sL))
    bashline.append('mv FRStackHist_%s_%s.root %s\n'%(lepOpt, sL, Rootfilesdirpath))

l = str(" ".join(s for s in samplesRun))
bashline.append('python  FRStackPlot.py -l %s -c %s'%(l, channel))
    
fsh = open("parallelStackHist.sh", "w")
fsh.write(''.join(bashline))
fsh.close()
os.system('chmod 744 parallelStackHist.sh')
os.system('./parallelStackHist.sh')
#os.system('mv *.root parallelJobsubmit.txt parallelStackHist.sh ../../../fake_rate_results/root_txt_sh_files/')

