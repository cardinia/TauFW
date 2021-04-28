###WIP###
ERA=2016
OUTDIR=coutFR_$ERA
mkdir $OUTDIR


templateFittingETauFR zee_fr_m_vis_eta0to1.448_et-2016.inputs.root VLoose | tee ./zee_fr_m_vis_eta0to1.448_et-2016.inputs.txt
#text2workspace.py -m 90 -P TauFW.Fitter.ETauFR.zttmodels:ztt_eff --PO "eff=0.0491043" zee_fr_m_vis_eta0to1.448_et-2016.inputs.txt -o  WorkSpaceVLooseLt1p460.root
text2workspace.py -m 90 -P TauFW.Fitter.ETauFR.zttmodels:ztt_eff --PO "eff=0.336763350536" ./input/2016/ETauFR/VLoose_eta0to1.448.txt -o  WorkSpaceVLooseLt1p460.root
combine -m 90  -M FitDiagnostics --robustFit=1 --preFitValue=1.0 --rMin=0.7 --rMax=1.5 --cminFallbackAlgo "Minuit2,0:1" -n "" WorkSpaceVLooseLt1p460.root | tee ./$OUTDIR/ScaleVLooseLt1p460.txt
./compare.py -a fitDiagnostics.root | tee ./$OUTDIR/VLooseLt1p460Pull.txt
PostFitShapesFromWorkspace -o ETauFRVLooseLt1p460_PostFitShape.root -m 90 -f fitDiagnostics.root:fit_s --postfit --sampling --print -d zee_fr_m_vis_eta0to1.448_et-2016.inputs.txt -w WorkSpaceVLooseLt1p460.root
