#! /usr/bin/env python
# Author: Izaak Neutelings (August 2020)
# Description: Create input histograms for datacards
#   ./createinputs.py -c mutau -y UL2017
import sys
from collections import OrderedDict
sys.path.append("../../Plotter/") # for config.samples
from config.samples import *
from TauFW.Plotter.plot.utils import LOG as PLOG
from TauFW.Plotter.plot.datacard import createinputs, plotinputs


def main(args):
  channels  = args.channels
  eras      = args.eras
  parallel  = args.parallel
  verbosity = args.verbosity
  plot      = True
  outdir    = ensuredir("input")
  plotdir   = ensuredir(outdir,"plots")
  analysis  = 'zee_fr' # $PROCESS_$ANALYSIS
  tag       = ""
  
  for era in eras:
    for channel in channels:
      if channel=='mutau' :
        analysis  = 'zmm_fr'
      
      
      ###############
      #   SAMPLES   #
      ###############
      # sample set and their systematic variations
      
      # GET SAMPLESET
      join      = ['VV','TT','ST']
      sname     = "$PICODIR/$SAMPLE_$CHANNEL$TAG.root"
      sampleset = getsampleset(channel,era,fname=sname,join=join,split=None,table=False)
      
      if channel=='mumu':
        
        # RENAME (HTT convention)
        sampleset.rename('DY_M50','ZLL')
        sampleset.rename('WJ','W')
        sampleset.datasample.name = 'data_obs'
        
        # SYSTEMATIC VARIATIONS
        varprocs = { # processes to be varied
          'Nom': ['ZLL','W','VV','ST','TT','QCD','data_obs'],
        }
        samplesets = { # sets of samples per variation
          'Nom': sampleset, # nominal
        }
        samplesets['Nom'].printtable(merged=True,split=True)
        if verbosity>=2:
          samplesets['Nom'].printobjs(file=True)
      
      else:
        
        # SPLIT & RENAME (HTT convention)
        GMR = "genmatch_2==5"
        GML = "genmatch_2>0 && genmatch_2<5"
        GMJ = "genmatch_2==0"
        GMF = "genmatch_2<5"
        sampleset.split('DY',[('ZTT',GMR),('ZL',GML),('ZJ',GMJ),])
        sampleset.split('TT',[('TTT',GMR),('TTL',GML),('TTJ',GMJ)])
        #sampleset.split('ST',[('STT',GMR),('STJ',GMF),]) # small background
        sampleset.rename('WJ','W')
        sampleset.datasample.name = 'data_obs'
        
        # SYSTEMATIC VARIATIONS
        varprocs = OrderedDict([ # processes to be varied
          ('Nom',     ['ZTT','ZL','ZJ','W','VV','ST','TTT','TTL','TTJ','QCD','data_obs']), #,'STT','STJ'
          ('TESUp',   ['ZTT']),
          ('TESDown', ['ZTT']),
          ('FESUp',   ['ZL']),
          ('FESDown', ['ZL']),
          ('EESUp',   ['ZL']), #Electron energy scale
          ('EESDown', ['ZL']),
          #('JTFUp',   ['ZJ', 'TTJ', 'QCD', 'W']),
          #('JTFDown', ['ZJ', 'TTJ', 'QCD', 'W']),
        ])
        samplesets = { # sets of samples per variation
          'Nom':     sampleset, # nominal
          'TESUp':   sampleset.shift(varprocs['TESUp'],  "_TES1p05","_TESUp",  " +5% TES", split=True,filter=False,share=True),
          'TESDown': sampleset.shift(varprocs['TESDown'],"_TES0p95","_TESDown"," -5% TES", split=True,filter=False,share=True),
          'FESUp':   sampleset.shift(varprocs['FESUp'],  "_FES1p25","_FESUp",  " +25% FES", split=True,filter=False,share=True),
          'FESDown': sampleset.shift(varprocs['FESDown'],"_FES0p75","_FESDown"," -25% FES", split=True,filter=False,share=True),
          'EESUp':   sampleset.shift(varprocs['EESUp'],  "_EES1p01","_EESUp",  " +1% EES", split=True,filter=False,share=True),
          'EESDown': sampleset.shift(varprocs['EESDown'],"_EES0p99","_EESDown"," -1% EES", split=True,filter=False,share=True),
        }
        keys = samplesets.keys() if verbosity>=1 else ['Nom','TESUp','TESDown']
        for shift in keys:
          if not shift in samplesets: continue
          samplesets[shift].printtable(merged=True,split=True)
          if verbosity>=2:
            samplesets[shift].printobjs(file=True)
      
      
      ###################
      #   OBSERVABLES   #
      ###################
      # observable/variables to be fitted in combine
      
      if channel=='mumu':
      
        observables = [
          Var('m_vis', 1, 60, 120, ymargin=1.6, rrange=0.08),
        ]
      
      else:
        
        mvis_pass = Var('m_vis', 11, 60, 120)
        mvis_fail = Var('m_vis', 1, 60, 120)
        observables_pass = []
        observables_fail = []
        
        # ADDED Eta for E->Tau FR
        # PT & DM BINS
        # drawing observables can be run in parallel
        # => use 'cut' option as hack to save time drawing pt or DM bins
        #    instead of looping over many selection,
        #    also, each pt/DM bin will be a separate file
        dmbins = [0,1,10,11]
        etabins = [0,1.448,1.560,2.3] #ETauFR binning
        if channel=='mutau' :
          etabins = [0,0.4,0.8,1.2,1.7,2.3] #MuTauFR binning
          
        ptbins = [20,25,30,35,40,50,70,2000] #500,1000]
        if "fr" not in analysis :
          print ">>> DM cuts:"
          for dm in dmbins:
            dmcut = "pt_2>40 && dm_2==%d"%(dm)
            fname = "$VAR_dm%s"%(dm)
            mvis_cut = mvis.clone(fname=fname,cut=dmcut) # create observable with extra cut for dm bin
            print ">>>   %r (%r)"%(dmcut,fname)
            observables.append(mvis_cut)
          print ">>> pt cuts:"
          for imax, ptmin in enumerate(ptbins,1):
            if imax<len(ptbins):
              ptmax = ptbins[imax]
              ptcut = "pt_2>%s && pt_2<=%s"%(ptmin,ptmax)
              fname = "$VAR_pt%sto%s"%(ptmin,ptmax)
            else: # overflow
              #ptcut = "pt_2>%s"%(ptmin)
              #fname = "$VAR_ptgt%s"%(ptmin)
              continue # skip overflow bin
            mvis_cut = mvis.clone(fname=fname,cut=ptcut) # create observable with extra cut for pt bin
            print ">>>   %r (%r)"%(ptcut,fname)
            observables.append(mvis_cut)
        else :
          print ">>> eta cuts:"
          for imax,etamin in enumerate(etabins,1):
            if imax<len(etabins):
              etamax = etabins[imax]
              etacut = "abs(eta_2)>%s && abs(eta_2)<=%s"%(etamin,etamax)
              fname = "$VAR_eta%sto%s"%(etamin,etamax)
            else: 
              continue # skip overflow bin
            mvis_pass_cut = mvis_pass.clone(fname=fname,cut=etacut) # create observable with extra cut for eta bin
            mvis_fail_cut = mvis_fail.clone(fname=fname,cut=etacut) # create observable with extra cut for eta bin
            print ">>>   %r (%r)"%(etacut,fname)
            observables_pass.append(mvis_pass_cut)
            observables_fail.append(mvis_fail_cut)
          
      
      ############
      #   BINS   #
      ############
      # selection categories
      
      if channel=='mumu':
        
        baseline  = "q_1*q_2<0 && iso_1<0.15 && iso_2<0.15 && !lepton_vetoes && metfilter"
        bins = [
          Sel('ZMM', baseline),
        ]
      
      else:
        
        tauwps    = ['VVVLoose','VVLoose','VLoose','Loose','Medium','Tight','VTight','VVTight']
        if channel=='mutau' :
          tauwps    = ['VLoose','Loose','Medium','Tight']
        tauwpbits = { wp: 2**i for i, wp in enumerate(tauwps)}
        iso_1     = "iso_1<0.15"
        iso_2     = "idDecayModeNewDMs_2 && idDeepTau2017v2p1VSjet_2>=16 && idDeepTau2017v2p1VSe_2>=$WP && idDeepTau2017v2p1VSmu_2>=1"
        iso_2_fail     = "idDecayModeNewDMs_2 && idDeepTau2017v2p1VSjet_2>=16 && idDeepTau2017v2p1VSe_2<$WP && idDeepTau2017v2p1VSmu_2>=1"
        if channel=='mutau' :
          iso_2     = "idDecayModeNewDMs_2 && idDeepTau2017v2p1VSjet_2>=16 && idDeepTau2017v2p1VSe_2>=1 && idDeepTau2017v2p1VSmu_2>=$WP"
          iso_2_fail     = "idDecayModeNewDMs_2 && idDeepTau2017v2p1VSjet_2>=16 && idDeepTau2017v2p1VSe_2>=1 && idDeepTau2017v2p1VSmu_2>=$WP"
          
        passregion  = "q_1*q_2<0 && mt_1<60 && %s && %s && !lepton_vetoes_notau && metfilter"%(iso_1,iso_2)
        failregion = "q_1*q_2<0 && mt_1<60 && %s && %s && !lepton_vetoes_notau && metfilter"%(iso_1,iso_2_fail)
        #zttregion = "%s && mt_1<60 && dzeta>-25 && abs(deta_ll)<1.5"%(baseline)
        bins_pass = [
          #Sel('baseline', repkey(baseline,WP=16)),
          #Sel('zttregion',repkey(zttregion,WP=16)),
        ]
        bins_fail = []
        TPRegion = ['Pass','Fail']
        for wpname in tauwps: # loop over tauVsEle WPs
          wpbit = tauwpbits[wpname]
          for regionname in TPRegion:
            if regionname =='Pass':
                bins_pass.append(Sel(wpname+regionname,repkey(passregion,WP=wpbit)))
            else:
                bins_fail.append(Sel(wpname+regionname,repkey(failregion,WP=wpbit)))
      
      
      
      #######################
      #   DATACARD INPUTS   #
      #######################
      # histogram inputs for the datacards
      
      # https://twiki.cern.ch/twiki/bin/viewauth/CMS/SMTauTau2016
      chshort = channel.replace('tau','t').replace('mu','m') # abbreviation of channel
      fname   = "%s/%s_$OBS_%s-%s$TAG%s.inputs.root"%(outdir,analysis,chshort,era,tag)
      createinputs(fname,samplesets['Nom'],    observables_pass,bins_pass,recreate=True)
      if channel in ['mutau']:
        createinputs(fname,samplesets['TESUp'],  observables_pass,bins_pass,filter=varprocs['TESUp']  )
        createinputs(fname,samplesets['TESDown'],observables_pass,bins_pass,filter=varprocs['TESDown'])
        createinputs(fname,samplesets['FESUp'],  observables_pass,bins_pass,filter=varprocs['FESUp']  )
        createinputs(fname,samplesets['FESDown'],observables_pass,bins_pass,filter=varprocs['FESDown'])
        createinputs(fname,samplesets['EESUp'],  observables_pass,bins_pass,filter=varprocs['EESUp']  )
        createinputs(fname,samplesets['EESDown'],observables_pass,bins_pass,filter=varprocs['EESDown'])
        createinputs(fname,samplesets['Nom']    ,observables_pass.replace('m_vis','m_vis_resoUp'),bins_pass,filter=varprocs['RESUp']  ,htag='RESUp'  )
        createinputs(fname,samplesets['Nom']    ,observables_pass.replace('m_vis','m_vis_resoDown'),bins_pass,filter=varprocs['RESDown'],htag='RESDown')
      createinputs(fname,samplesets['Nom'],    observables_fail,bins_fail)
      if channel in ['mutau']:
        createinputs(fname,samplesets['TESUp'],  observables_fail,bins_fail,filter=varprocs['TESUp']  )
        createinputs(fname,samplesets['TESDown'],observables_fail,bins_fail,filter=varprocs['TESDown'])
        createinputs(fname,samplesets['FESUp'],  observables_fail,bins_fail,filter=varprocs['FESUp']  )
        createinputs(fname,samplesets['FESDown'],observables_fail,bins_fail,filter=varprocs['FESDown'])
        createinputs(fname,samplesets['EESUp'],  observables_fail,bins_fail,filter=varprocs['EESUp']  )
        createinputs(fname,samplesets['EESDown'],observables_fail,bins_fail,filter=varprocs['EESDown'])
        createinputs(fname,samplesets['Nom']    ,observables_fail.replace('m_vis','m_vis_resoUp'),bins_fail,filter=varprocs['RESUp']  ,htag='RESUp'  )
        createinputs(fname,samplesets['Nom']    ,observables_fail.replace('m_vis','m_vis_resoDown'),bins_fail,filter=varprocs['RESDown'],htag='RESDown')
      
      
      ############
      #   PLOT   #
      ############
      # control plots of the histogram inputs
      
      if plot:
        pname  = "%s/%s_$OBS_%s-$BIN-%s$TAG%s.png"%(plotdir,analysis,chshort,era,tag)
        text   = "%s: $BIN"%(channel.replace("mu","#mu").replace("tau","#tau_{h}"))
        groups = [ ] #(['^TT','ST'],'Top'),]
        plotinputs(fname,varprocs,observables_pass,bins_pass,text=text,
                   pname=pname,tag=tag,group=groups)
      

if __name__ == "__main__":
  from argparse import ArgumentParser
  argv = sys.argv
  description = """Create input histograms for datacards"""
  parser = ArgumentParser(prog="createInputs",description=description,epilog="Good luck!")
  parser.add_argument('-y', '--era',     dest='eras', nargs='*', choices=['2016','2017','2018','UL2017'], default=['UL2017'], action='store',
                                         help="set era" )
  parser.add_argument('-c', '--channel', dest='channels', nargs='*', choices=['mutau','mumu','etau'], default=['etau'], action='store',
                                         help="set channel" )
  parser.add_argument('-s', '--serial',  dest='parallel', action='store_false',
                                         help="run Tree::MultiDraw serial instead of in parallel" )
  parser.add_argument('-v', '--verbose', dest='verbosity', type=int, nargs='?', const=1, default=0, action='store',
                                         help="set verbosity" )
  args = parser.parse_args()
  LOG.verbosity = args.verbosity
  PLOG.verbosity = args.verbosity
  main(args)
  print "\n>>> Done."
  
