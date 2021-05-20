###WIP###
ERA=2016
OUTDIR=coutFR_$ERA
mkdir $OUTDIR
apath=/afs/cern.ch/work/l/lvigilan/TauWork/CMSSW_8_1_0/src/

cd /afs/cern.ch/work/l/lvigilan/TauWork/CMSSW_8_1_0/src/
eval `scramv1 runtime -sh`
cd - 
#templateFittingETauFR zee_fr_m_vis_eta0to1.448_et-2016.inputs.root VLoose | tee ./zee_fr_m_vis_eta0to1.448_et-2016.inputs.txt
#text2workspace.py -m 90 -P TauFW.Fitter.ETauFR.zttmodels:ztt_eff --PO "eff=0.0491043" zee_fr_m_vis_eta0to1.448_et-2016.inputs.txt -o  WorkSpaceVLooseLt1p460.root

text2workspace.py -m 90 -P HiggsAnalysis.ETauFR.zttmodels:ztt_eff --PO "0.683516577326" ./input/2016/ETauFR/VVLoose_eta0to1.46.txt -o  WorkSpaceVVLooseLt1p46.root
combine -m 90  -M FitDiagnostics --robustFit=1 --expectSignal=1.0 --rMin=0.7 --rMax=1.5 --cminFallbackAlgo "Minuit2,0:1" -n "" WorkSpaceVVLooseLt1p46.root | tee ./$OUTDIR/ScaleVVLooseLt1p46.txt
#combine -m 90  -M FitDiagnostics --robustFit=0 --expectSignal=1.0 --rMin=0.0 --rMax=3.0 --cminFallbackAlgo "Minuit2,0:1" -n "" WorkSpaceVVLooseLt1p46.root | tee ./$OUTDIR/ScaleVVLooseLt1p46.txt
./compare.py -a fitDiagnostics.root | tee ./$OUTDIR/VVLooseLt1p46Pull.txt
#./compare.py -a fitDiagnostics.root | tee ./$OUTDIR/VVLooseLt1p46Pull.txt
#PostFitShapesFromWorkspace -o ETauFRVVLooseLt1p46_PostFitShape.root -m 90 -f fitDiagnostics.root:fit_s --postfit --sampling --print -d zee_fr_m_vis_eta0to1.46_et-2016.inputs.txt -w WorkSpaceVVLooseLt1p46.root
PostFitShapesFromWorkspace -o ETauFRVVLooseLt1p46_PostFitShape.root -m 90 -f fitDiagnostics.root:fit_s --postfit --sampling --print -d ./input/2016/ETauFR/VVLoose_eta0to1.46.txt -w WorkSpaceVVLooseLt1p46.root
