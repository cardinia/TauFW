///////////////////////////////////////
// Author: Andrea Cardini (Mar 2021)
// Description: Create datacards for combine


#include <string>
#include <map>
#include <set>
#include <iostream>
#include <utility>
#include <vector>
#include <cstdlib>
#include "CombineHarvester/CombineTools/interface/CombineHarvester.h"
#include "CombineHarvester/CombineTools/interface/Observation.h"
#include "CombineHarvester/CombineTools/interface/Process.h"
#include "CombineHarvester/CombineTools/interface/Utilities.h"
#include "CombineHarvester/CombineTools/interface/Systematics.h"
#include "CombineHarvester/CombineTools/interface/BinByBin.h"
#include "TRegexp.h"

using namespace std;

int main(int argc, char * argv[]) {
  //! [part1]
  // First define the location of the "auxiliaries" directory where we can
  // source the input files containing the datacard shapes
  string aux_shapes = "./input/";

  // Create an empty CombineHarvester instance that will hold all of the
  // datacard configuration and histograms etc.
  ch::CombineHarvester cb;
  // Uncomment this next line to see a *lot* of debug information
  // cb.SetVerbosity(3);

  TString WP="VVVLoose";
  if(argc>1)WP=argv[2];
  TString PassBin=WP+"_pass";
  TString FailBin=WP+"_fail";
  // Each entry in the vector below specifies a bin name and corresponding bin_id.
  ch::Categories cats = {
    {1, PassBin.Data()},
    {2, FailBin.Data()}
  };
  // ch::Categories is just a typedef of vector<pair<int, string>>
  //! [part1]


  //! [part2]
  //vector<string> masses = ch::MassesFromRange("120-135:5");
  // Or equivalently, specify the mass points explicitly:
    vector<string> masses = {"90"};
  //! [part2]

  //! [part3]
  cb.AddObservations({"*"}, {"ETauFR"}, {"13TeV"}, {"et"}, cats);
  //! [part3]

  //! [part4]
  vector<string> bkg_procs = {"ZJ","ZTT","W", "QCD", "TTT","TTL","TTJ","VV","ST"};
  cb.AddProcesses({"*"}, {"ETauFR"}, {"13TeV"}, {"et"}, bkg_procs, cats, false);

  vector<string> sig_procs = {"ZL"};
  cb.AddProcesses(masses, {"ETauFR"}, {"13TeV"}, {"et"}, sig_procs, cats, true);
  //! [part4]


  //Some of the code for this is in a nested namespace, so
  // we'll make some using declarations first to simplify things a bit.
  using ch::syst::SystMap;
  using ch::syst::era;
  using ch::syst::bin_id;
  using ch::syst::process;

  //! [part5]
    cb.cp().process(ch::JoinStr({sig_procs,{"ZJ"},{"ZTT"},{"VV"},{"ST"},{"TTT"},{"TTJ"},{"TTL"}})).AddSyst(cb, "lumi_$ERA", "lnN", SystMap<era>::init({"13TeV"}, 1.026));
    
  //! [part5]

  //! [part6] Define systematic variations

    cb.cp().process({"W"}).AddSyst(cb, "normalizationW", "lnN", SystMap<>::init(1.20));
    cb.cp().process({"ZTT"}).AddSyst(cb, "TauVsJetSF", "lnN", SystMap<>::init(1.10));
    cb.cp().process({"ZJ"}).AddSyst(cb, "jetTauFR", "lnN", SystMap<>::init(1.30));
    cb.cp().process(ch::JoinStr({{"ZL"},{"ZJ"},{"ZTT"}})).AddSyst(cb, "normalizationDY", "lnN", SystMap<>::init(1.05));
    cb.cp().process({"ZL"}).AddSyst(cb, "normalizationZEE", "rateParam", SystMap<>::init(1.));
    cb.cp().process({"QCD"}).AddSyst(cb, "normalizationQCD", "lnN", SystMap<>::init(1.2));
    cb.cp().process({"VV"}).AddSyst(cb, "normalizationVV", "lnN", SystMap<>::init(1.15));
    cb.cp().process({"TT"}).AddSyst(cb, "normalizationTT", "lnN", SystMap<>::init(1.10));
    cb.cp().process(ch::JoinStr({sig_procs,{"ZJ"},{"ZTT"},{"VV"},{"ST"},{"TTT"},{"TTJ"},{"TTL"}})).AddSyst(cb, "CMS_eff_e", "lnN", SystMap<>::init(1.05));
    cb.cp().process(ch::JoinStr({sig_procs,{"ZTT"},{"VV"},{"ST"},{"TTT"},{"TTJ"},{"TTL"}})).AddSyst(cb, "CMS_eff_t", "lnN", SystMap<>::init(1.05));
    cb.cp().process(ch::JoinStr({sig_procs})).AddSyst(cb, "shape_ees", "shape", SystMap<>::init(1));
    cb.cp().process(ch::JoinStr({sig_procs})).AddSyst(cb, "shape_fes", "shapeU", SystMap<>::init(1));
    cb.cp().process({"ZTT"}).AddSyst(cb, "shape_tes", "shape", SystMap<>::init(1));
    //cb.cp().process(ch::JoinStr({sig_procs})).AddSyst(cb, "shape_res", "shape", SystMap<>::init(1)); //Uncomment once fixed
    
  //! [part6]

  //! [part7] Setup location from which to extract the shapes.
    //Usage ExtractShapes(relative-path/filename,root-directory/$PROCESS,root-directory/$PROCESS)
    //Currently the name of the directory in the rootfile is $WP PASS/FAIL, WP is taken as the second argument of the 


  cb.cp().backgrounds().ExtractShapes(
      aux_shapes + argv[1],
      "$BIN/$PROCESS",
      "$BIN/$PROCESS_$SYSTEMATIC");
  cb.cp().signals().ExtractShapes(
      aux_shapes + argv[1],
      "$BIN/$PROCESS",
      "$BIN/$PROCESS_$SYSTEMATIC");

  //! [part7]

  //! [part8]
    auto bbb = ch::BinByBinFactory().SetAddThreshold(0.1).SetFixNorm(true);
    
    bbb.AddBinByBin(cb.cp().backgrounds(),cb);
    
    TString outputdcname = (TString) argv[1];
    TRegexp re(".root");
    outputdcname(re) = ".txt";
  //! [part8]

  //! [part9]
  // First we generate a set of bin names:
  set<string> bins = cb.bin_set();
  // This method will produce a set of unique bin names by considering all
  // Observation, Process and Systematic entries in the CombineHarvester
  // instance.

  // We create the output root file that will contain all the shapes.
  TFile output("htt_et.input.root", "RECREATE");

  // Finally we iterate through each bin,mass combination and write a
  // datacard.
    cb.cp().WriteDatacard((string)outputdcname, output);
  //! [part9]
    float sigRatePassPre = cb.cp().bin({PassBin.Data()}).process({"ZL"}).GetRate();
    float sigRateFailPre = cb.cp().bin({FailBin.Data()}).process({"ZL"}).GetRate();
    float sigErrPassPre = cb.cp().bin({PassBin.Data()}).process({"ZL"}).GetUncertainty();
    float sigErrFailPre = cb.cp().bin({FailBin.Data()}).process({"ZL"}).GetUncertainty();
    cout << "pre-fit fake rate: "
	 << (sigRatePassPre/(sigRatePassPre+sigRateFailPre)) << "\n";

    
    float dfdxPre = sigRateFailPre/((sigRatePassPre+sigRateFailPre)*(sigRatePassPre+sigRateFailPre));
    float dfdyPre = - sigRatePassPre/((sigRatePassPre+sigRateFailPre)*(sigRatePassPre+sigRateFailPre));
    float errfakeratePrefit= sqrt((dfdxPre*sigErrPassPre)*(dfdxPre*sigErrPassPre)+(dfdyPre*sigErrFailPre)*(dfdyPre*sigErrFailPre));
    
    cout << "pre-fit fake rate errors:" << errfakeratePrefit << endl;
    
    
}
