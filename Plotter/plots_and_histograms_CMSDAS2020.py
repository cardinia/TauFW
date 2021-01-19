#! /usr/bin/env python
# Author: Izaak Neutelings (August 2020)
# Description: Simple plotting script for pico analysis tuples
#   ./plot.py -c mutau -y 2018
import re
import ROOT as R
from TauFW.Plotter.plot.utils import LOG as PLOG
from TauFW.Plotter.sample.utils import LOG, STYLE, ensuredir, repkey, joincuts, setera, getyear, Sel, Var
from TauFW.Plotter.sample.utils import getsampleset as _getsampleset

def getsampleset(channel,era,**kwargs):
  verbosity = LOG.getverbosity(kwargs)
  year  = getyear(era) # get integer year
  tag   = kwargs.get('tag',   ""           )
  table = kwargs.get('table', True         ) # print sample set table
  setera(era) # set era for plot style and lumi normalization

  negative_fractions = {
    "DYJetsToLL_M-50" : 0.0004,
    "WJetsToLNu" : 0.0004,
    "WW_TuneCP5_13TeV-pythia8" : 0.0, # <-- no adaption of effective events needed
    "WZ_TuneCP5_13TeV-pythia8" : 0.0, # <-- no adaption of effective events needed
    "ZZ_TuneCP5_13TeV-pythia8" : 0.0, # <-- no adaption of effective events needed
    "ST_t-channel_top" : 0.033, 
    "ST_t-channel_antitop" : 0.031, 
    "ST_tW_top" : 0.002, 
    "ST_tW_antitop" : 0.002, 
    "TTTo2L2Nu" : 0.004,
    "TTToHadronic" : 0.004,
    "TTToSemiLeptonic" : 0.004,
  }
    
  # SM BACKGROUND MC SAMPLES
  if year == 2018:
    expsamples = [ # table of MC samples to be converted to Sample objects
      # GROUP NAME                     TITLE                 XSEC [pb]      effective NEVENTS = simulated NEVENTS * ( 1  - 2 * negative fraction)
      
      # Cross-secitons: https://twiki.cern.ch/twiki/bin/viewauth/CMS/StandardModelCrossSectionsat13TeV, Z/a* (50)
      ( 'DY', "DYJetsToLL_M-50",       "Drell-Yan 50",       6077.22,       {"nevts" : 100194597 * (1.0 - 2 * negative_fractions["DYJetsToLL_M-50"])}),

      # Cross-sections: https://twiki.cern.ch/twiki/bin/viewauth/CMS/StandardModelCrossSectionsat13TeV, Total W
      ( 'WJ', "WJetsToLNu",            "W + jets",           3*20508.9,     {"nevts" : 71072199 * (1.0 - 2 * negative_fractions["WJetsToLNu"])}),

      # Cross-sections: https://twiki.cern.ch/twiki/bin/viewauth/CMS/StandardModelCrossSectionsat13TeV, W+ W-
      ( 'VV', "WW",                    "WW",                 118.7, {"nevts" : 7850000}),

      # Cross-sections: from generator (https://cms-gen-dev.cern.ch/xsdb with 'process_name=WZ_TuneCP5_13TeV-pythia8')
      ( 'VV', "WZ",                    "WZ",                 27.6, {"nevts" : 3885000}),

      # Cross-sections: from generator (https://cms-gen-dev.cern.ch/xsdb with 'process_name=ZZ_TuneCP5_13TeV-pythia8')
      ( 'VV', "ZZ",                    "ZZ",                 12.14, {"nevts" : 1979000}),

      # Cross-sections: # https://twiki.cern.ch/twiki/bin/viewauth/CMS/SingleTopSigma
      ( 'ST', "ST_t-channel_top",      "ST t-channel t",     136.02, {"nevts" : 154307600 * (1.0 - 2 * negative_fractions["ST_t-channel_top"])}),
      ( 'ST', "ST_t-channel_antitop",  "ST t-channel at",    80.95,  {"nevts" : 79090800 * (1.0 - 2 * negative_fractions["ST_t-channel_antitop"]) }),
      ( 'ST', "ST_tW_top",             "ST tW",              35.85,  {"nevts" : 9598000 * (1.0 - 2 * negative_fractions["ST_tW_top"])  }),
      ( 'ST', "ST_tW_antitop",         "ST atW",             35.85,  {"nevts" : 7623000 * (1.0 - 2 * negative_fractions["ST_tW_antitop"])  }),

      # Cross-sections: https://twiki.cern.ch/twiki/bin/view/LHCPhysics/TtbarNNLO#Top_quark_pair_cross_sections_at, m_top = 172.5 GeV + PDG for W boson decays
      ( 'TT', "TTTo2L2Nu",             "ttbar 2l2#nu",       831.76*(3*0.1086)**2,         {"nevts" : 64310000 * (1.0 - 2 * negative_fractions["TTTo2L2Nu"]) }), 
      ( 'TT', "TTToHadronic",          "ttbar hadronic",     831.76*2*(3*0.1086)*(0.6741), {"nevts" : 199524000 * (1.0 - 2 * negative_fractions["TTToHadronic"])}),
      ( 'TT', "TTToSemiLeptonic",      "ttbar semileptonic", 831.76*(0.6741)**2,           {"nevts" : 199925998 * (1.0 - 2 * negative_fractions["TTToSemiLeptonic"])}),
    ]
  
  if year == 2016:
    expsamples = [ # table of MC samples to be converted to Sample objects                                                                                                         
      # GROUP NAME                     TITLE                 XSEC [pb]      effective NEVENTS = simulated NEVENTS * ( 1  - 2 * negative fraction)                           
      
      # Cross-secitons: https://twiki.cern.ch/twiki/bin/viewauth/CMS/StandardModelCrossSectionsat13TeV, Z/a* (50)                                                           
      ( 'DY', "DYJetsToLL_M-50",       "Drell-Yan 50",          6077.22,       {"nevts" : 49748967 * (1.0 - 2 * negative_fractions["DYJetsToLL_M-50"])}),
      # Cross-secitons: https://github.com/cardinia/HiggsCP/blob/master/Inputs/interface/settingsDNN.h#L695-L699
      ( 'DY', "DY1JetsToLL_M-50",      "Drell-Yan 50 1j",       1012.5,       {"nevts" : 63730337 }),
      ( 'DY', "DY2JetsToLL_M-50",      "Drell-Yan 50 2j",       332.8,       {"nevts" : 19879279 }),
      ( 'DY', "DY3JetsToLL_M-50",      "Drell-Yan 50 3j",       101.8,       {"nevts" : 5857441 }),
      ( 'DY', "DY4JetsToLL_M-50",      "Drell-Yan 50 4j",       54.8,       {"nevts" : 4197868 }),

      # Cross-sections: https://twiki.cern.ch/twiki/bin/viewauth/CMS/StandardModelCrossSectionsat13TeV, Total W                                                                   
      ( 'WJ', "WJetsToLNu",             "W + jets",              3*20508.9,     {"nevts" : 57402435 * (1.0 - 2 * negative_fractions["WJetsToLNu"])}),
      # Cross-secitons: https://github.com/cardinia/HiggsCP/blob/master/Inputs/interface/settingsDNN.h
      ( 'WJ', "W1JetsToLNu",            "W + jets 1j",           9644.5,  {"nevts" : 43773492 }),
      ( 'WJ', "W2JetsToLNu",            "W + jets 2j",           3144.5,  {"nevts" : 30374504 }),
      ( 'WJ', "W3JetsToLNu",            "W + jets 3j",           954.8,     {"nevts" : 39501912 }),
      ( 'WJ', "W4JetsToLNu",            "W + jets 4j",           485.6,     {"nevts" : 18751462 }),

      # Cross-sections: https://github.com/cardinia/HiggsCP/blob/master/Inputs/interface/settingsDNN.h
      ( 'VV', "WW",                    "WW",                 75.88, {"nevts" : 6988168}),

      # Cross-sections: from generator (https://cms-gen-dev.cern.ch/xsdb with 'process_name=WZ_TuneCP5_13TeV-pythia8')                                                            
      ( 'VV', "WZ",                    "WZ",                 27.6, {"nevts" : 2997571}),

      # Cross-sections: from generator (https://cms-gen-dev.cern.ch/xsdb with 'process_name=ZZ_TuneCP5_13TeV-pythia8')                                                           
      ( 'VV', "ZZ",                    "ZZ",                 12.14, {"nevts" : 998034}),

      # Cross-sections: # https://twiki.cern.ch/twiki/bin/viewauth/CMS/SingleTopSigma                                                                                      
      ( 'ST', "ST_t-channel_top",      "ST t-channel t",     136.02, {"nevts" : 31848000 * (1.0 - 2 * negative_fractions["ST_t-channel_top"])}),
      ( 'ST', "ST_t-channel_antitop",  "ST t-channel at",    80.95,  {"nevts" : 17780700 * (1.0 - 2 * negative_fractions["ST_t-channel_antitop"]) }),
      ( 'ST', "ST_tW_top",             "ST tW",              35.85,  {"nevts" : 4983500 * (1.0 - 2 * negative_fractions["ST_tW_top"])  }),
      ( 'ST', "ST_tW_antitop",         "ST atW",             35.85,  {"nevts" : 4980600 * (1.0 - 2 * negative_fractions["ST_tW_antitop"])  }),

      # Cross-sections: https://twiki.cern.ch/twiki/bin/view/LHCPhysics/TtbarNNLO#Top_quark_pair_cross_sections_at, m_top = 172.5 GeV + PDG for W boson decays
      ( 'TT', "TT",             "ttbar",       831.76,         {"nevts" : 76915549 }), #ONLY FOR 2016                                                                             
    ]



  # OBSERVED DATA SAMPLES
  if 'mutau'  in channel: dataset = "SingleMuon_Run%d?"%year
  elif 'etau'  in channel: 
    if year == 2017 or year==2016:
      dataset = "SingleElectron_Run%d?"%year
    else:
      dataset = "EGamma_Run2017?"# LOR CHANGES. MADE FOR 2018
  else:
    LOG.throw(IOError,"Did not recognize channel %r!"%(channel))
  datasample = ('Data',dataset) # Data for chosen channel
  


  # SAMPLE SET
  # TODO section 5: This weight needs to be extended with correction weights common to all simulated samples (MC)
  weight = "genweight/abs(genweight)" # normalize weight, since sometimes the generator cross-section is contained in it.
  kwargs.setdefault('weight',weight)  # common weight for MC
  sampleset = _getsampleset(datasample,expsamples,channel=channel,era=era,**kwargs)


  #STITCHING
  sampleset.stitch("W*Jets",   incl='WJ', name='WJ',xsec_incl=3*20508.9/1.224,kfactor=1.224,title="W jets" )
  sampleset.stitch("DY*J*M-50",incl='DYJ',name="DY_M-50",xsec_incl=6077.22/1.225,kfactor=1.225,title="Drell-Yan M=50GeV")
  
  # JOIN
  # Note: titles are set via STYLE.sample_titles
  sampleset.join('WW', 'WZ', 'ZZ', name='VV'  ) # Diboson
  sampleset.join('VV', 'WJ', name='EWK') # Electroweak

  sampleset.join('TT', name='TT' ) # ttbar
  sampleset.join('ST', name='ST' ) # single top
  sampleset.join('ST','TT', name='Top' ) #ttbar & single top 
  
  # SPLIT
  # TODO section 5: Check the generator matching for various samples in the flat n-tuples.
  # Is it justified to require only the tauh candidate to match to generator level hadronic tau to declare the full process with Z->tautau in mutau final state?
  # What is the major contribution from Drell-Yan to genmatch_2!=5? How does this look like for other processes?
  GMR = "genmatch_2==5"
  GMO = "genmatch_2!=5"
  sampleset.split('DY', [('ZTT',GMR),('ZL',GMO)])
  sampleset.split('Top',[('TopT',GMR),('TopJ',GMO)])
  sampleset.split('EWK',[('EWKT',GMR),('EWKJ',GMO)])
 
  if table:
    sampleset.printtable(merged=True,split=True)
  return sampleset


def plot(sampleset,channel,parallel=True,tag="",outdir="plots",histdir="",era=""):
  """Test plotting of SampleSet class for data/MC comparison."""
  LOG.header("plot")
  
  # SELECTIONS
  inclusive = "(q_1*q_2<0)"
  
  inclusive_cr_qcd = inclusive.replace("q_1*q_2<0","q_1*q_2>0") # inverting the opposite-sign requirement of the mutau pair into a same-sign requirment
  general_cuts = "(iso_1<0.1)&&(pt_1>26.0)&&(pt_2>20.0)&&(eta_1>-2.1)&&(eta_1<2.1)&&(eta_2>-2.3)&&(eta_2<2.3)"
  
  mvis_cuts1 = "(m_vis>60) && (m_vis < 120) && (mt_2 < 60) && (idDeepTau2017v2p1VSe_2 >= 16 )"
  mvis_cuts2 = "(m_vis>60) && (m_vis < 120) && (mt_2 < 60) && (idDeepTau2017v2p1VSe_2 >= 32 )" #LOR CUTS 16 DIC 2020

  mvis_cuts3 = "(m_vis>60) && (m_vis < 120) && (mt_1 < 60) && (idDeepTau2017v2p1VSe_2 >= 1 )"#VVVLose
  mvis_cuts4 = "(m_vis>60) && (m_vis < 120) && (mt_1 < 60) && (idDeepTau2017v2p1VSe_2 >= 4 )"#VLose
  mvis_cuts5 = "(m_vis>60) && (m_vis < 120) && (mt_1 < 60) && (idDeepTau2017v2p1VSe_2 >= 16 )"#Medium
  mvis_cuts6 = "(m_vis>60) && (m_vis < 120) && (mt_1 < 60) && (idDeepTau2017v2p1VSe_2 >= 64 )"#VTight

  id_cuts3 = "(idDeepTau2017v2p1VSjet_2>= 16)"#&&(idDeepTau2017v2p1VSe_2 >= 1 )"#VVVLose
  id_cuts4 = "(idDeepTau2017v2p1VSjet_2>= 16)&&(idDeepTau2017v2p1VSe_2 >= 4 )"#VLose
  id_cuts5 = "(idDeepTau2017v2p1VSjet_2>= 16)&&(idDeepTau2017v2p1VSe_2 >= 16 )"#Medium
  id_cuts6 = "(idDeepTau2017v2p1VSjet_2>= 16)"#&&(idDeepTau2017v2p1VSe_2 >= 64 )"#VTight

  mt1_cuts= "(mt_1 < 60)"
 #prepara VVL e VT, no taglio m_t
 #da fare pt,phi e eta ele e tau, njet,mt,mvis,jetpt e discrimani,
  inclusive = inclusive.replace(" ","")
  general_cuts = general_cuts.replace(" ","")
  mvis_cuts1 = mvis_cuts1.replace(" ","")
  mvis_cuts2 = mvis_cuts2.replace(" ","")
  mvis_cuts3 = mvis_cuts3.replace(" ","")
  mvis_cuts4 = mvis_cuts4.replace(" ","")
  mvis_cuts5 = mvis_cuts5.replace(" ","")
  mvis_cuts6 = mvis_cuts6.replace(" ","")

  id_cuts3 = id_cuts3.replace(" ","")
  id_cuts4 = id_cuts4.replace(" ","")
  id_cuts5 = id_cuts5.replace(" ","")
  id_cuts6 = id_cuts6.replace(" ","")
  
  mt1_cuts = mt1_cuts.replace(" ","")

  
  #SUM OF SELECTIONS
  tot_cuts1 = general_cuts + "&&" + mvis_cuts1
  tot_cuts1 = tot_cuts1.replace(" ","")
  tot_cuts2 = general_cuts + "&&" + mvis_cuts2
  tot_cuts2 = tot_cuts2.replace(" ","")

  tot_cuts3 = general_cuts + "&&" + mvis_cuts3
  tot_cuts3 = tot_cuts3.replace(" ","")
  tot_cuts4 = general_cuts + "&&" + mvis_cuts4
  tot_cuts4 = tot_cuts4.replace(" ","")
  tot_cuts5 = general_cuts + "&&" + mvis_cuts5
  tot_cuts5 = tot_cuts5.replace(" ","")
  tot_cuts6 = general_cuts + "&&" + mvis_cuts6
  tot_cuts6 = tot_cuts6.replace(" ","")


  totid_cuts3 = general_cuts + "&&" + id_cuts3
  totid_cuts3 = totid_cuts3.replace(" ","")
  totid_cuts4 = general_cuts + "&&" + id_cuts4
  totid_cuts4 = totid_cuts4.replace(" ","")
  totid_cuts5 = general_cuts + "&&" + id_cuts5
  totid_cuts5 = totid_cuts5.replace(" ","")
  totid_cuts6 = general_cuts + "&&" + id_cuts6
  totid_cuts6 = totid_cuts6.replace(" ","")
  
  tot_mt1_cuts1 = general_cuts + "&&" + mt1_cuts
  tot_mt1_cuts1 = tot_mt1_cuts1.replace(" ","")


  selections = [
    #Sel('kinematic sel.',general_cuts),
    #Sel('tot_PuppiMET_DTMedium',tot_cuts1),
    #Sel('tot_PuppiMET_DTTight',tot_cuts2),
    #Sel('tot_PFMET_DTVVVL',tot_cuts3),
    #Sel('tot_PFMET_DTVL',tot_cuts4),
    #Sel('tot_PFMET_DTMedium',tot_cuts5),
    #Sel('tot_PFMET_DTVTight',tot_cuts6),
    
    Sel('id_VSjM-VSeVVVL',totid_cuts3),
    #Sel('id_VSjM-VSeVL',totid_cuts4),
    #Sel('id_VSjM-VSeM',totid_cuts5),
    Sel('id_VSjM-VSeVT',totid_cuts6),

    #Sel('inclusive',inclusive),
    #Sel('inclusive_cr_qcd',inclusive_cr_qcd),
    
    #Sel('mt1_VSjM',tot_mt1_cuts1),
  ]
  
  # VARIABLES
  # TODO section 5: extend with other variables, which are available in the flat n-tuples
  variables = [
     #Var('m_vis',  11,  60, 120),
     #Var('pt_1',  "Muon pt",    40,  35, 120, ctitle={'etau':"Electron pt",'tautau':"Leading tau_h pt",'emu':"Electron pt"}),
     #Var('pt_2',  "tau_h pt",   40,  20, 120, ctitle={'tautau':"Subleading tau_h pt",'emu':"Muon pt"}),
     #Var('eta_1', "Electron eta",   30, -3, 3, ctitle={'etau':"Electron eta",'tautau':"Leading tau_h eta",'emu':"Electron eta"},ymargin=1.6,pos='T',ncols=2),
     #Var('eta_2', "tau_h eta",  30, -3, 3, ctitle={'etau':"Tau eta",'tautau':"Subleading tau_h eta",'emu':"Muon eta"},ymargin=1.6,pos='T',ncols=2),
     #Var('m_vis',  40,  0, 200),
     #Var('mt_1',  "mt(e,MET)", 40,  0, 200),
     #Var('mt_2',  "mt(e,PuppiMET)", 40,  0, 200),
     #Var("jpt_1",  29,   10,  300, veto=[r"njets\w*==0"]),
     #Var("jpt_2",  29,   10,  300, veto=[r"njets\w*==0"]),
     #Var("jeta_1", 53, -5.4,  5.2, ymargin=1.6,pos='T',ncols=2,veto=[r"njets\w*==0"]),
     #Var("jeta_2", 53, -5.4,  5.2, ymargin=1.6,pos='T',ncols=2,veto=[r"njets\w*==0"]),
     #Var('njets',   8,  0,   8),
     #Var('met',    50,  0, 150),
     #Var('puppimetpt', "PuppiMET"  , 50,  0, 150),
     #Var('pt_ll',   "p_{T}(mutau_h)", 25, 0, 200, ctitle={'etau':"p_{T}(etau_h)",'tautau':"p_{T}(tau_htau_h)",'emu':"p_{T}(emu)"}),
     #Var('dR_ll',   "DR(mutau_h)",    30, 0, 6.0, ctitle={'etau':"DR(etau_h)",'tautau':"DR(tau_htau_h)",'emu':"DR(emu)"}),
     #Var('deta_ll', "deta(mutau_h)",  20, 0, 6.0, ctitle={'etau':"deta(etau_h)",'tautau':"deta(tautau)",'emu':"deta(emu)"},logy=True,pos='TRR'), #, ymargin=8, logyrange=2.6
     #Var('dzeta',  56, -180, 100, pos='L;y=0.88',units='GeV'),
     #Var("pzetavis", 50,    0, 200 ), 
     #Var('rawDeepTau2017v2p1VSjet_2', "rawDeepTau2017v2p1VSjet", 100, 0.0, 1, ncols=2,pos='L;y=0.85',logy=True,ymargin=2.5),
     #Var('rawDeepTau2017v2p1VSjet_2', "rawDeepTau2017v2p1VSjet", 20, 0.80, 1, fname="$VAR_zoom",ncols=2,pos='L;y=0.85'),
     Var('rawDeepTau2017v2p1VSe_2',   "rawDeepTau2017v2p1VSe",   100, 0.0, 1, fname="$VAR",ncols=2,ymin=1.0, logy=True,pos='L;y=0.85'),
     Var('rawDeepTau2017v2p1VSe_2',   "rawDeepTau2017v2p1VSe",   30, 0.70, 1, fname="$VAR_zoom",ncols=2,logy=True,pos='L;y=0.85'),
     #Var('rawDeepTau2017v2p1VSmu_2',  "rawDeepTau2017v2p1VSmu",  100, 0.0, 1, fname="$VAR",ncols=2,logy=True,logyrange=4,pos='L;y=0.85'),                                    
     #Var('rawDeepTau2017v2p1VSmu_2',  "rawDeepTau2017v2p1VSmu",  20, 0.80, 1, fname="$VAR_zoom",ncols=2,logy=True,logyrange=4,pos='L;y=0.85'),                                    

#     Var('npv',    40,    0,  80 ), 

  ]
  
  # PLOT and HIST
  outdir   = ensuredir(repkey(outdir,CHANNEL=channel,ERA=era))
  histdir  = ensuredir(repkey(histdir,CHANNEL=channel,ERA=era))
  outhists = R.TFile.Open(histdir,'recreate')
  exts     = ['png','pdf']
  for selection in selections:
    outhists.mkdir(selection.filename)
    stacks = sampleset.getstack(variables,selection,method='QCD_OSSS',scale=1.1,parallel=parallel) # the 'scale' keyword argument - chosen as 1.1 for mutau - 
                                                                                                   # is an extrapolation factor for the QCD shape from the same-sign
                                                                                                   # to the opposite-sign region
    fname  = "%s/$VAR_%s-%s-%s$TAG"%(outdir,channel,selection.filename,era)
    text   = "%s: %s"%(channel.replace('mu',"#mu").replace('tau',"#tau_{h}"),selection.title)
    for stack, variable in stacks.iteritems():
      outhists.cd(selection.filename)
      for h in stack.hists:
        h.Write(h.GetName().replace("QCD_","QCD"),R.TH1.kOverwrite)
      stack.draw()
      stack.drawlegend(x1=0.40,x2=0.95,y1=0.70,y2=0.95)
      stack.drawtext(text)
      stack.saveas(fname,ext=exts,tag=tag)
      stack.close()
  outhists.Close()
  

def main(args):
  channel = args.channel
  era     = args.era
  parallel = args.parallel
  outdir   = "plots/$ERA"
  histdir  = "hists/$ERA/$CHANNEL.root"
  tag      = ""
  fpattern = args.picopattern

  setera(era) # set era for plot style and lumi-xsec normalization
  sampleset = getsampleset(channel,era,file=fpattern,tag=tag,table=True)
  plot(sampleset,channel,parallel=parallel,tag=tag,outdir=outdir,histdir=histdir,era=era)
  

if __name__ == "__main__":
  import sys
  from argparse import ArgumentParser
  argv = sys.argv
  description = """Simple plotting script for pico analysis tuples"""
  parser = ArgumentParser(prog="plot",description=description,epilog="Good luck!")
  parser.add_argument('-y', '--era',     dest='era', type=str, default='2017',
                                         help="Set era. Default: %(default)s" )
  parser.add_argument('-c', '--channel', dest='channel', type=str, default="mutau",
                                         help="Set channel. Default: %(default)s" )
  parser.add_argument('-s', '--serial',  dest='parallel', action='store_false',
                                         help="Run Tree::MultiDraw serial instead of in parallel" )
  parser.add_argument('-v', '--verbose', dest='verbosity', type=int, nargs='?', const=1, default=0, action='store',
                                         help="Set verbosity" )
  parser.add_argument('--picopattern',   dest='picopattern', type=str, default="$PICODIR/$SAMPLE_$CHANNEL$TAG.root",
                                         help="Name pattern of the flat n-tuple files. Default: %(default)s" )
  args = parser.parse_args()
  LOG.verbosity = args.verbosity
  PLOG.verbosity = args.verbosity
  main(args)
  print "\n>>> Done."
  


