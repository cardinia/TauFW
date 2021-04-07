###WIP###
ERA=2016
OUTDIR=coutFR_$ERA
mkdir $OUTDIR


templateFittingETauFR zee_fr_m_vis_eta0to1.448_et-2016.inputs.root Loose | tee ./zee_fr_m_vis_eta0to1.448_et-2016.inputs.txt
#text2workspace.py -m 90 -P TauFW.Fitter.ETauFR.zttmodels:ztt_eff --PO "eff=0.0491043" zee_fr_m_vis_eta0to1.448_et-2016.inputs.txt -o  WorkSpaceLooseLt1p460.root
text2workspace.py -m 90 -P TauFW.Fitter.ETauFR.zttmodels:ztt_eff --PO "eff=0.00971623" ./input/2016/ETauFR/Loose_eta0to1.448.txt -o  WorkSpaceLooseLt1p460.root
combine -m 90  -M FitDiagnostics --robustFit=1 --preFitValue=1.0 --rMin=0.7 --rMax=1.5 --cminFallbackAlgo "Minuit2,0:1" -n "" WorkSpaceLooseLt1p460.root | tee ./$OUTDIR/ScaleLooseLt1p460.txt
./compare.py -a fitDiagnostics.root | tee ./$OUTDIR/LooseLt1p460Pull.txt
PostFitShapesFromWorkspace -o ETauFRLooseLt1p460_PostFitShape.root -m 90 -f fitDiagnostics.root:fit_s --postfit --sampling --print -d zee_fr_m_vis_eta0to1.448_et-2016.inputs.txt -w WorkSpaceLooseLt1p460.root
