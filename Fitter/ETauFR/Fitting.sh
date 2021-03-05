###WIP###
ERA=2016
OUTDIR=coutFR_$ERA
mkdir OUTDIR



templateFittingETauFR zee_fr_m_vis_eta0to1.448_et-2016.inputs.root VVVLoose | tee ./zee_fr_m_vis_eta0to1.448_et-2016.inputs.txt
text2workspace.py -m 90 -P TauFW.Fitter.ETauFR.zttmodels:ztt_eff --PO "eff=0.0719746" zee_fr_m_vis_eta0to1.448_et-2016.inputs.txt -o  WorkSpaceVVVLooseLt1p460.root
combine -m 90  -M FitDiagnostics --robustFit=1 --preFitValue=1.0 --rMin=0.05 --rMax=4.5 --cminFallbackAlgo "Minuit2,0:1" -n "" WorkSpaceVVVLooseLt1p460.root | tee ./$OUTDIR/ScaleVVVLooseLt1p460.txt
./compare.py -a fitDiagnostics.root | tee ./$OUTDIR/VVVLooseLt1p460Pull.txt
PostFitShapesFromWorkspace -o ETauFRVVVLooseLt1p460_PostFitShape.root -m 90 -f fitDiagnostics.root:fit_s --postfit --sampling --print -d zee_fr_m_vis_eta0to1.448_et-2016.inputs.txt -w WorkSpaceVVVLooseLt1p460.root
