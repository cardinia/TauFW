# -*- coding: utf-8 -*-
# Author: Izaak Neutelings (May 2021)
# Description: Class to automatically make CMS 2D plot.
from TauFW.Plotter.plot.Plot import *
import TauFW.Plotter.plot.Plot
_lcolors2D = [ kOrange+7, kMagenta-4 ] + TauFW.Plotter.plot.Plot._lcolors # kOrange-3,

class Plot2D(Plot):
  """Class to automatically make CMS 2D plot."""
  
  def __init__(self, *args, **kwargs):
    """
    Initialize with list of histograms:
      Plot(hist)
    or with a variable (string or Variable object) as well:
      Plot(xvar,yvar,hists)
    """
    hists, vars = [ ], [ ]
    for arg in args:
      if isinstance(arg,TH2):
        hists.append(arg)
      else:
        vars.append(arg)
    if len(hists)==1 and isinstance(hists[0],TH2):
      hist = hists[0]
      if kwargs.get('clone',False):
        hist = hist.Clone(hist.GetName()+"_clone_Plot2D")
    else:
      LOG.warning("Plot2D.__init__: Did not recognize input: %s"%(args,))
    if len(vars)==1:
      LOG.warning("Plot2D.__init__: Need  one more variable!")
    if len(vars)>=2:
      xvariable   = vars[0]
      yvariable   = vars[1]
    else:
      xvariable   = None
      yvariable   = None
    self.canvas   = None
    self.legend   = None
    self.ratio    = None # not used
    self.profiles = [ ]
    self.graphs   = [ ]
    self.lines    = [ ]
    self.texts    = [ ]
    if isinstance(xvariable,Variable) and isinstance(yvariable,Variable):
      self.xvariable  = xvariable
      self.yvariable  = yvariable
      self.xtitle     = kwargs.get('xtitle',     xvariable.title     )
      self.xmin       = kwargs.get('xmin',       xvariable.xmin      )
      self.xmax       = kwargs.get('xmax',       xvariable.xmax      )
      self.logx       = kwargs.get('logx',       xvariable.logx      )
      self.xbinlabels = kwargs.get('xbinlabels', xvariable.binlabels )
      self.ytitle     = kwargs.get('ytitle',     yvariable.title     )
      self.ymin       = kwargs.get('ymin',       yvariable.xmin      )
      self.ymax       = kwargs.get('ymax',       yvariable.xmax      )
      self.logy       = kwargs.get('logy',       xvariable.logx      )
      self.ybinlabels = kwargs.get('ybinlabels', yvariable.binlabels )
      self.logz       = kwargs.get('logz',       xvariable.logy      )
      self.position   = kwargs.get('position',   xvariable.position  )
    else:
      self.xvariable  = xvariable or hist.GetXaxis().GetTitle()
      self.yvariable  = yvariable or hist.GetYaxis().GetTitle()
      self.xtitle     = kwargs.get('xtitle',     xvariable                 )
      self.xmin       = kwargs.get('xmin',       hist.GetXaxis().GetXmin() )
      self.xmax       = kwargs.get('xmax',       hist.GetXaxis().GetXmax() )
      self.logx       = kwargs.get('logx',       False                     )
      self.xbinlabels = kwargs.get('xbinlabels', None                      )
      self.ytitle     = kwargs.get('ytitle',     yvariable                 )
      self.ymin       = kwargs.get('ymin',       hist.GetYaxis().GetXmin() )
      self.ymax       = kwargs.get('ymax',       hist.GetYaxis().GetXmax() )
      self.logy       = kwargs.get('logy',       False                     )
      self.ybinlabels = kwargs.get('ybinlabels', None                      )
      self.logz       = kwargs.get('logz',       False                     )
      self.position   = kwargs.get('position',   ""                        )
    self.zmin = kwargs.get('zmin', hist.GetMinimum() )
    self.zmax = kwargs.get('zmax', hist.GetMaximum() )
    self.hist = hist
    self.name = kwargs.get('name',"%s_vs_%s"%(yvariable,xvariable))
    
  def draw(self,*args,**kwargs):
    """Central method of Plot class: make plot with canvas, axis, error, ratio..."""
    hist         = self.hist
    yoffset      = kwargs.get('yoffset',      1.35 if self.hist.GetYaxis().GetXmax()>=1000 else 1.15 )
    option       = kwargs.get('option',       'COLZ',                     ) # COLZTEXT44
    title        = kwargs.get('title',        ""                          )
    xtitle       = kwargs.get('xtitle',       self.xtitle                 )
    ytitle       = kwargs.get('ytitle',       self.ytitle                 )
    ztitle       = kwargs.get('ztitle',       ""                          )
    xmin         = kwargs.get('xmin',         self.xmin                   )
    xmax         = kwargs.get('xmax',         self.xmax                   )
    ymin         = kwargs.get('ymin',         self.ymin                   )
    ymax         = kwargs.get('ymax',         self.ymax                   )
    zmin         = kwargs.get('zmin',         self.zmin                   )
    zmax         = kwargs.get('zmax',         self.zmax                   )
    logx         = kwargs.get('logx',         self.logx                   )
    logy         = kwargs.get('logy',         self.logy                   )
    logz         = kwargs.get('logz',         self.logz                   )
    lentries     = kwargs.get('lentry',       [ ]                         )
    tsize        = kwargs.get('tsize',        0.050                       )
    tcolor       = kwargs.get('tcolor',       kBlack                      )
    format       = kwargs.get('format',       ".2f"                       )
    legend       = kwargs.get('legend',       False                       )
    lcolor       = kwargs.get('lcolor',       kBlack                      )
    cwidth       = kwargs.get('width',        850                         )
    cheight      = kwargs.get('height',       750                         )
    position     = kwargs.get('position',     self.position               )
    lmargin      = 0.16 if self.hist.GetYaxis().GetXmax()>=1000 else 0.14
    rmargin      = (0.12 if logz else 0.16 if hist.GetMaximum()>=1000 else 0.14) + (0.06 if ztitle else 0.0)
    yoffset      = 1.35 if (not logy and self.hist.GetYaxis().GetXmax()>=1000) else 1.15
    tmargin      = kwargs.get('tmargin',      0.05                        )
    bmargin      = kwargs.get('bmargin',      0.14                        )
    lmargin      = kwargs.get('lmargin',      lmargin                     )
    rmargin      = kwargs.get('rmargin',      rmargin                     )
    xoffset      = kwargs.get('xoffset',      1.02                        )
    yoffset      = kwargs.get('yoffset',      yoffset                     )
    zoffset      = kwargs.get('zoffset',      5.5 if logz else 7.3        )*rmargin
    labelsize    = kwargs.get('labelsize',    0.048                       )
    xbinlabels   = kwargs.get('xbinlabels',   self.xbinlabels             )
    ybinlabels   = kwargs.get('ybinlabels',   self.ybinlabels             )
    xlabelsize   = kwargs.get('xlabelsize',   labelsize*(1.7 if xbinlabels else 1) )
    ylabelsize   = kwargs.get('ylabelsize',   labelsize*(1.7 if ybinlabels else 1) )
    xlabeloffset = kwargs.get('xlabeloffset', 0.005 if xbinlabels else -0.004 if logx else 0.01 )
    ylabeloffset = kwargs.get('ylabeloffset', 0.008 if ybinlabels else 0.005                    )
    zlabeloffset = kwargs.get('zlabeloffset', -0.003 if logz else 0.01    )
    markersize   = kwargs.get('markersize',   1.0                         )
    if zmin: hist.SetMinimum(zmin)
    if zmax: hist.SetMaximum(zmax)
    self.xmin, self.xmax = xmin, xmax
    self.ymin, self.ymax = ymin, ymax
    self.zmin, self.zmax = zmin, zmax
    
    # CANVAS
    canvas = TCanvas("canvas","canvas",100,100,int(cwidth),int(cheight))
    canvas.SetFillColor(0)
    canvas.SetBorderMode(0)
    canvas.SetFrameFillStyle(0)
    canvas.SetFrameBorderMode(0)
    canvas.SetTopMargin(  tmargin ); canvas.SetBottomMargin( bmargin )
    canvas.SetLeftMargin( lmargin ); canvas.SetRightMargin(  rmargin )
    canvas.SetTickx(0); canvas.SetTicky(0)
    canvas.SetGrid()
    canvas.cd()
    self.canvas = canvas
    if logy: canvas.Update(); canvas.SetLogy()
    if logx: canvas.Update(); canvas.SetLogx()
    if logz: canvas.Update(); canvas.SetLogz()
    
    # AXES
    hist.SetTitle("")
    hist.GetXaxis().SetTitleSize(0.058)
    hist.GetYaxis().SetTitleSize(0.058)
    hist.GetZaxis().SetTitleSize(0.056)
    hist.GetXaxis().SetLabelSize(xlabelsize)
    hist.GetYaxis().SetLabelSize(ylabelsize)
    hist.GetZaxis().SetLabelSize(0.044)
    hist.GetXaxis().SetLabelOffset(xlabeloffset)
    hist.GetYaxis().SetLabelOffset(ylabeloffset)
    hist.GetZaxis().SetLabelOffset(zlabeloffset)
    hist.GetXaxis().SetTitleOffset(0.97)
    hist.GetXaxis().SetTitleOffset(xoffset)
    hist.GetYaxis().SetTitleOffset(yoffset)
    hist.GetZaxis().SetTitleOffset(zoffset)
    hist.GetZaxis().CenterTitle(True)
    hist.GetXaxis().SetTitle(makelatex(xtitle))
    hist.GetYaxis().SetTitle(makelatex(ytitle))
    hist.GetZaxis().SetTitle(makelatex(ztitle))
    hist.GetXaxis().SetRangeUser(xmin,xmax)
    hist.GetYaxis().SetRangeUser(ymin,ymax)
    if "text" in option.lower():
      gStyle.SetPaintTextFormat(format)
      hist.SetMarkerSize(markersize)
      hist.SetMarkerColor(tcolor)
      #hist.SetMarkerSize(1)
    if zmin!=None: hist.SetMinimum(zmin)
    if zmax!=None: hist.SetMaximum(zmax)
    hist.Draw(option)
    canvas.RedrawAxis()
    
    # alphanumerical bin labels
    if xbinlabels:
      nxbins = hist.GetXaxis().GetNbins()
      if len(xbinlabels)<nxbins:
        LOG.warning("Plot2D.plot: len(xbinlabels)=%d < %d=nxbins"%(len(xbinlabels),nxbins))
      for i, xbinlabels in zip(range(1,nxbins+1),xbinlabels):
        hist.GetXaxis().SetBinLabel(i,makelatex(xbinlabels,units=False))
    if ybinlabels:
      nybins = hist.GetYaxis().GetNbins()
      if len(ybinlabels)<nybins:
        LOG.warning("Plot2D.plot: len(ybinlabels)=%d < %d=nybins"%(len(ybinlabels),nybins))
      for i, ybinlabels in zip(range(1,nybins+1),ybinlabels):
        hist.GetYaxis().SetBinLabel(i,makelatex(ybinlabels,units=False))
    
    # CMS STYLE
    if CMSStyle.lumiText:
      CMSStyle.setCMSLumiStyle(gPad,0)
  
  def drawprofile(self,axes,entries=[ ],**kwargs):
    """Draw profile on canvas."""
    self.profiles = [ ]
    # MAKE PROFILE
    for i, axis in enumerate(axes):
      profile = self.hist.ProfileX() if "x"==axis.lower() else self.hist.ProfileY()
      color   = kRed
      if i<len(entries):
        profile.SetTitle(entries[i])
      profile.SetLineColor(color)
      profile.SetMarkerColor(color)
      profile.SetLineWidth(3)
      profile.SetLineStyle(1)
      profile.SetMarkerStyle(20)
      profile.SetMarkerSize(0.9)
      profile.Draw('SAME') 
      self.profiles.append(profile)
    return self.profiles
    
  def close(self,keep=False,**kwargs):
    """Close canvas and delete the histograms."""
    verbosity = LOG.getverbosity(self,kwargs)
    if self.canvas:
      self.canvas.Close()
    if not keep: # do not keep histograms
      if self.hist:
        deletehist(self.hist)
    for profile in self.profiles:
      deletehist(graph)
    for graph in self.graphs:
      deletehist(graph)
    for line in self.lines:
      deletehist(line)
    LOG.verb("closed\n>>>",verbosity,2)
    
  def drawgraph(self,graphs,entries=[ ],**kwargs):
    """Draw graphs on canvas."""
    graphs  = [ g for g in ensurelist(graphs) if g ]
    entries = kwargs.get('entry', [ ] )
    for i, graph in enumerate(graphs):
      if not graph: continue
      color = _lcolors2D[i%len(_lcolors2D)]
      if i<len(entries):
        graph.SetTitle(entries[i])
      graph.SetTitle(gtitle)
      graph.SetLineColor(color)
      graph.SetMarkerColor(color)
      graph.SetLineWidth(3)
      graph.SetMarkerSize(3)
      graph.SetLineStyle(1)
      graph.SetMarkerStyle(3)
      graph.Draw('LPSAME')
    self.grahps = graphs[:]
    return graphs
    
  def drawlegend(**kwargs):
    tsize  = 0.041
    width  = 0.26
    height = tsize*1.10*len([o for o in graphs+lentries+pentries+[title,text] if o])
    if 'left' in position.lower():   x1 = 0.17; x2 = x1+width
    else:                            x1 = 0.78; x2 = x1-width 
    if 'bottom' in position.lower(): y1 = 0.20; y2 = y1+height
    else:                            y1 = 0.90; y2 = y1-height
    legend = TLegend(x1,y1,x2,y2)
    legend.SetTextSize(tsize)
    legend.SetTextColor(lcolor)
    legend.SetBorderSize(0)
    legend.SetFillStyle(0)
    #legend.SetFillStyle(1001)
    #legend.SetFillStyle(4050)
    legend.SetFillColor(0)
    #legend.SetFillColor(kWhiteTransparent)
    #legend.SetFillColorAlpha(kBlue, 0.50)
    if title:
      legend.SetTextFont(62)
      legend.SetHeader(title) 
    legend.SetTextFont(42)
    for graph in self.graphs:
      self.legend.AddEntry(graph,graph.GetTitle(),'lp')
    for profile in self.profiles:
      legend.AddEntry(profile,profile.GetTitle(),'lep')
    self.canvas.cd()
    legend.Draw('SAME')
    self.legend = legend
    
