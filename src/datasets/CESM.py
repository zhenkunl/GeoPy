'''
Created on 2013-12-04

This module contains common meta data and access functions for CESM model output. 

@author: Andre R. Erler, GPL v3
'''

# external imports
import numpy as np
import os, pickle
from collections import OrderedDict
# from atmdyn.properties import variablePlotatts
from geodata.base import Variable, Axis, concatDatasets
from geodata.netcdf import DatasetNetCDF, VarNC
from geodata.gdal import addGDALtoDataset, GDALError
from geodata.misc import DatasetError, AxisError, DateError, ArgumentError, isNumber, isInt
from datasets.common import translateVarNames, data_root, grid_folder, default_varatts, addLengthAndNamesOfMonth 
from geodata.gdal import loadPickledGridDef, griddef_pickle
from datasets.WRF import Exp as WRF_Exp
from processing.process import CentralProcessingUnit

# some meta data (needed for defaults)
root_folder = data_root + 'CESM/' # long-term mean folder
outfolder = root_folder + 'cesmout/' # WRF output folder
avgfolder = root_folder + 'cesmavg/' # monthly averages and climatologies
cvdpfolder = root_folder + 'cvdp/' # CVDP output (netcdf files and HTML tree)
diagfolder = root_folder + 'diag/' # output from AMWG diagnostic package (climatologies and HTML tree) 

## list of experiments
class Exp(WRF_Exp): 
  parameters = WRF_Exp.parameters.copy()
  defaults = WRF_Exp.defaults.copy()
  defaults['avgfolder'] = lambda atts: '{0:s}/{1:s}/'.format(avgfolder,atts['name'])
  parameters['cvdpfolder'] = dict(type=basestring,req=True) # new parameters need to be registered
  defaults['cvdpfolder'] = lambda atts: '{0:s}/{1:s}/'.format(cvdpfolder,atts['name'])
  parameters['diagfolder'] = dict(type=basestring,req=True) # new parameters need to be registered
  defaults['diagfolder'] = lambda atts: '{0:s}/{1:s}/'.format(diagfolder,atts['name'])
  defaults['parents'] = None # not applicable here
  
# list of experiments
# N.B.: This is the reference list, with unambiguous, unique keys and no aliases/duplicate entries  
experiments = OrderedDict() # dictionary of experiments
# historical 
# N.B.: the extnded ensemble end data is necessary for CVDP
experiments['ens20trcn1x1'] = Exp(shortname='Ens', name='ens20trcn1x1', title='CESM Ensemble Mean', begindate='1979-01-01', enddate='2039-01-01', grid='cesm1x1')
experiments['tb20trcn1x1'] = Exp(shortname='Ctrl-1', name='tb20trcn1x1', title='Exp 1 (CESM)', begindate='1979-01-01', enddate='1994-01-01', grid='cesm1x1', ensemble='ens20trcn1x1')
experiments['hab20trcn1x1'] = Exp(shortname='Ctrl-A', name='hab20trcn1x1', title='Exp 2 (CESM)', begindate='1979-01-01', enddate='1994-01-01', grid='cesm1x1', ensemble='ens20trcn1x1')
experiments['hbb20trcn1x1'] = Exp(shortname='Ctrl-B', name='hbb20trcn1x1', title='Exp 3 (CESM)', begindate='1979-01-01', enddate='1994-01-01', grid='cesm1x1', ensemble='ens20trcn1x1')
experiments['hcb20trcn1x1'] = Exp(shortname='Ctrl-C', name='hcb20trcn1x1', title='Exp 4 (CESM)', begindate='1979-01-01', enddate='1994-01-01', grid='cesm1x1', ensemble='ens20trcn1x1')
# mid-21st century
experiments['ensrcp85cn1x1'] = Exp(shortname='Ens-2050', name='ensrcp85cn1x1', title='CESM Ensemble Mean (2050)', begindate='2045-01-01', enddate='2105-01-01', grid='cesm1x1')
experiments['seaice-5r-hf'] = Exp(shortname='Seaice-2050', name='seaice-5r-hf', title='Seaice (CESM, 2050)', begindate='2045-01-01', enddate='2060-01-01', grid='cesm1x1')
experiments['htbrcp85cn1x1'] = Exp(shortname='Ctrl-1-2050', name='htbrcp85cn1x1', title='Exp 1 (CESM, 2050)', begindate='2045-01-01', enddate='2060-01-01', grid='cesm1x1', ensemble='ensrcp85cn1x1')
experiments['habrcp85cn1x1'] = Exp(shortname='Ctrl-A-2050', name='habrcp85cn1x1', title='Exp 2 (CESM, 2050)', begindate='2045-01-01', enddate='2060-01-01', grid='cesm1x1', ensemble='ensrcp85cn1x1')
experiments['hbbrcp85cn1x1'] = Exp(shortname='Ctrl-B-2050', name='hbbrcp85cn1x1', title='Exp 3 (CESM, 2050)', begindate='2045-01-01', enddate='2060-01-01', grid='cesm1x1', ensemble='ensrcp85cn1x1')
experiments['hcbrcp85cn1x1'] = Exp(shortname='Ctrl-C-2050', name='hcbrcp85cn1x1', title='Exp 4 (CESM, 2050)', begindate='2045-01-01', enddate='2060-01-01', grid='cesm1x1', ensemble='ensrcp85cn1x1')
# mid-21st century
experiments['ensrcp85cn1x1d'] = Exp(shortname='Ens-2100', name='ensrcp85cn1x1d', title='CESM Ensemble Mean (2100)', begindate='2085-01-01', enddate='2145-01-01', grid='cesm1x1')
experiments['seaice-5r-hfd'] = Exp(shortname='Seaice-2100', name='seaice-5r-hfd', title='Seaice (CESM, 2100)', begindate='2085-01-01', enddate='2100-01-01', grid='cesm1x1')
experiments['htbrcp85cn1x1d'] = Exp(shortname='Ctrl-1-2100', name='htbrcp85cn1x1d', title='Exp 1 (CESM, 2100)', begindate='2085-01-01', enddate='2100-01-01', grid='cesm1x1', ensemble='ensrcp85cn1x1d')
experiments['habrcp85cn1x1d'] = Exp(shortname='Ctrl-A-2100', name='habrcp85cn1x1d', title='Exp 2 (CESM, 2100)', begindate='2085-01-01', enddate='2100-01-01', grid='cesm1x1', ensemble='ensrcp85cn1x1d')
experiments['hbbrcp85cn1x1d'] = Exp(shortname='Ctrl-B-2100', name='hbbrcp85cn1x1d', title='Exp 3 (CESM, 2100)', begindate='2085-01-01', enddate='2100-01-01', grid='cesm1x1', ensemble='ensrcp85cn1x1d')
experiments['hcbrcp85cn1x1d'] = Exp(shortname='Ctrl-C-2100', name='hcbrcp85cn1x1d', title='Exp 4 (CESM, 2100)', begindate='2085-01-01', enddate='2100-01-01', grid='cesm1x1', ensemble='ensrcp85cn1x1d')
## an alternate dictionary using short names and aliases for referencing
exps = OrderedDict()
# use short names where available, normal names otherwise
for key,item in experiments.iteritems():
  exps[item.name] = item
  if item.shortname is not None: 
    exps[item.shortname] = item
  # both, short and long name are added to list
# add aliases here
CESM_exps = exps # alias for whole dict
CESM_experiments = experiments # alias for whole dict
## dict of ensembles
ensembles = CESM_ens = OrderedDict()
ensemble_list = list(set([exp.ensemble for exp in experiments.values() if exp.ensemble]))
# ensemble_list.sort()
for ensemble in ensemble_list:
  #print ensemble, experiments[ensemble].shortname
  members = [exp for exp in experiments.values() if exp.ensemble and exp.ensemble == ensemble]
#   members.sort()
  ensembles[experiments[ensemble].shortname] = members

# return name and folder
def getFolderName(name=None, experiment=None, folder=None, mode='avg', cvdp_mode=None, lcheckExp=True):
  ''' Convenience function to infer and type-check the name and folder of an experiment based on various input. '''
  # N.B.: 'experiment' can be a string name or an Exp instance
  # figure out experiment name
  if experiment is None and name not in exps:
    if cvdp_mode is None: cvdp_mode = 'ensemble' # backwards-compatibility
    if not isinstance(folder,basestring):
      if mode == 'cvdp' and ( cvdp_mode == 'observations' or cvdp_mode == 'grand-ensemble' ): 
        folder = "{:s}/grand-ensemble/".format(cvdpfolder)              
      else: raise IOError, "Need to specify an experiment folder in order to load data."    
  else:
    # load experiment meta data
    if isinstance(experiment,Exp): pass # preferred option
    elif isinstance(experiment,basestring): experiment = exps[experiment] 
    elif isinstance(name,basestring) and name in exps: experiment = exps[name]
    else: raise DatasetError, 'Dataset of name \'{0:s}\' not found!'.format(name or experiment)
    if cvdp_mode is None:
      if not experiment.ensemble or experiment.ensemble == experiment.name: cvdp_mode = 'ensemble'
      else: cvdp_mode = ''  
    # root folder
    if folder is None: 
      if mode == 'avg': folder = experiment.avgfolder
      elif mode == 'cvdp': 
        if cvdp_mode == 'ensemble': 
          expfolder = experiment.ensemble or experiment.name 
          folder = "{:s}/{:s}/".format(cvdpfolder,expfolder)
        elif cvdp_mode == 'grand-ensemble': folder = "{:s}/grand-ensemble/".format(cvdpfolder)
        else: folder = experiment.cvdpfolder
      elif mode == 'diag': folder = experiment.diagfolder
      else: raise NotImplementedError,"Unsupported mode: '{:s}'".format(mode)
    elif not isinstance(folder,basestring): raise TypeError
    # name
    if name is None: name = experiment.name
    if not isinstance(name,basestring): raise TypeError      
  # check if folder exists
  if not os.path.exists(folder): raise IOError, 'Dataset folder does not exist: {0:s}'.format(folder)
  # return name and folder
  return folder, experiment, name


# function to undo NCL's lonFlip
def flipLon(data, flip=144, lrev=False, var=None, slc=None):
  ''' shift longitude on the fly, so as to undo NCL's lonFlip; only works on entire array '''
  if var is not None: # ignore parameters
    if not isinstance(var,VarNC): raise TypeError
    ax = var.axisIndex('lon')
    flip = len(var.lon)/2
  if data.ndim < var.ndim: # some dimensions have been squeezed
    sd = 0 # squeezed dimensions before ax
    for sl in slc:
      if isinstance(sl,(int,np.integer)): sd += 1
    ax -= sd # remove squeezed dimensions
  if not ( data.ndim > ax and data.shape[ax] == flip*2 ): 
    raise NotImplementedError, "Can only shift longitudes of the entire array!"
  # N.B.: this operation only makes sense with a full array!
  if lrev: flip *= -1 # reverse flip  
  data = np.roll(data, shift=flip, axis=ax) # shift values half way along longitude
  return data


## variable attributes and name
class FileType(object): 
  ''' Container class for all attributes of of the constants files. '''
  atts = NotImplemented
  vars = NotImplemented
  climfile = None
  tsfile = None
  cvdpfile = None
  diagfile = None
  
# surface variables
class ATM(FileType):
  ''' Variables and attributes of the surface files. '''
  def __init__(self):
    self.atts = dict(TREFHT   = dict(name='T2', units='K'), # 2m Temperature
#                                      transform=flipLon), # shift longitude
                     TREFMXAV = dict(name='Tmax', units='K'),   # Daily Maximum Temperature (at surface)                     
                     TREFMNAV = dict(name='Tmin', units='K'),   # Daily Minimum Temperature (at surface)
                     QREFHT   = dict(name='q2', units='kg/kg'), # 2m water vapor mass mixing ratio                     
                     TS       = dict(name='Ts', units='K'), # Skin Temperature (SST)
                     TSMX     = dict(name='MaxTs', units='K'),   # Maximum Skin Temperature (SST)
                     TSMN     = dict(name='MinTs', units='K'),   # Minimum Skin Temperature (SST)                     
                     PRECT    = dict(name='precip', units='kg/m^2/s', scalefactor=1000.), # total precipitation rate (kg/m^2/s) 
                     PRECC    = dict(name='preccu', units='kg/m^2/s', scalefactor=1000.), # convective precipitation rate (kg/m^2/s)
                     PRECL    = dict(name='precnc', units='kg/m^2/s', scalefactor=1000.), # grid-scale precipitation rate (kg/m^2/s)
                     #NetPrecip    = dict(name='p-et', units='kg/m^2/s'), # net precipitation rate
                     #LiquidPrecip = dict(name='liqprec', units='kg/m^2/s'), # liquid precipitation rate
                     PRECSL   = dict(name='solprec', units='kg/m^2/s', scalefactor=1000.), # solid precipitation rate
                     #SNOWLND   = dict(name='snow', units='kg/m^2'), # snow water equivalent
                     SNOWHLND = dict(name='snowh', units='m'), # snow depth
                     SNOWHICE = dict(name='snowhice', units='m'), # snow depth
                     ICEFRAC  = dict(name='seaice', units=''), # seaice fraction
                     SHFLX    = dict(name='hfx', units='W/m^2'), # surface sensible heat flux
                     LHFLX    = dict(name='lhfx', units='W/m^2'), # surface latent heat flux
                     QFLX     = dict(name='evap', units='kg/m^2/s'), # surface evaporation
                     FLUT     = dict(name='OLR', units='W/m^2'), # Outgoing Longwave Radiation
                     FLDS     = dict(name='GLW', units='W/m^2'), # Ground Longwave Radiation
                     FSDS     = dict(name='SWD', units='W/m^2'), # Downwelling Shortwave Radiation                     
                     PS       = dict(name='ps', units='Pa'), # surface pressure
                     PSL      = dict(name='pmsl', units='Pa'), # mean sea level pressure
                     PHIS     = dict(name='zs', units='m', scalefactor=1./9.81), # surface elevation
                     #LANDFRAC = dict(name='landfrac', units=''), # land fraction
                     )
    self.vars = self.atts.keys()    
    self.climfile = 'cesmatm{0:s}_clim{1:s}.nc' # the filename needs to be extended by ('_'+grid,'_'+period)
    self.tsfile = 'cesmatm{0:s}_monthly.nc' # the filename needs to be extended by ('_'+grid)
# CLM variables
class LND(FileType):
  ''' Variables and attributes of the land surface files. '''
  def __init__(self):
    self.atts = dict(topo     = dict(name='hgt', units='m'), # surface elevation
                     landmask = dict(name='landmask', units=''), # land mask
                     landfrac = dict(name='landfrac', units=''), # land fraction
                     FSNO     = dict(name='snwcvr', units=''), # snow cover (fractional)
                     QMELT    = dict(name='snwmlt', units='kg/m^2/s'), # snow melting rate
                     QOVER    = dict(name='sfroff', units='kg/m^2/s'), # surface run-off
                     QRUNOFF  = dict(name='runoff', units='kg/m^2/s'), # total surface and sub-surface run-off
                     QIRRIG   = dict(name='irrigation', units='kg/m^2/s'), # water flux through irrigation
                     )
    self.vars = self.atts.keys()    
    self.climfile = 'cesmlnd{0:s}_clim{1:s}.nc' # the filename needs to be extended by ('_'+grid,'_'+period)
    self.tsfile = 'cesmlnd{0:s}_monthly.nc' # the filename needs to be extended by ('_'+grid)
# CICE variables
class ICE(FileType):
  ''' Variables and attributes of the seaice files. '''
  def __init__(self):
    self.atts = dict() # currently not implemented...                     
    self.vars = self.atts.keys()
    self.climfile = 'cesmice{0:s}_clim{1:s}.nc' # the filename needs to be extended by ('_'+grid,'_'+period)
    self.tsfile = 'cesmice{0:s}_monthly.nc' # the filename needs to be extended by ('_'+grid)

# CVDP variables
class CVDP(FileType):
  ''' Variables and attributes of the CVDP netcdf files. '''
  def __init__(self):
    self.atts = dict(pdo_pattern_mon = dict(name='PDO_eof', units=''), # PDO EOF
                     pdo_timeseries_mon = dict(name='PDO', units=''), # PDO time-series
                     pna_mon = dict(name='PNA_eof', units=''), # PNA EOF
                     pna_pc_mon = dict(name='PNA', units=''), # PNA time-series
                     npo_mon = dict(name='NPO_eof', units=''), # NPO EOF
                     npo_pc_mon = dict(name='NPO', units=''), # NPO time-series
                     nao_mon = dict(name='NAO_eof', units=''), # PDO EOF
                     nao_pc_mon = dict(name='NAO', units=''), # PDO time-series
                     nam_mon = dict(name='NAM_eof', units=''), # NAM EOF
                     nam_pc_mon = dict(name='NAM', units=''), # NAM time-series
                     amo_pattern_mon = dict(name='AMO_eof', units='', # AMO EOF
                                            transform=flipLon), # undo shifted longitude (done by NCL)
                     amo_timeseries_mon = dict(name='AMO', units=''), # AMO time-series 
                     nino34 = dict(name='NINO34', units=''), # ENSO Nino34 index
                     npi_ndjfm = dict(name='NPI', units=''), # some North Pacific Index ???
                     )                    
    self.vars = self.atts.keys()
    self.indices = [var['name'] for var in self.atts.values() if var['name'].upper() == var['name'] and var['name'] != 'NPI']
    self.eofs = [var['name'] for var in self.atts.values() if var['name'][-4:] == '_eof']
    self.cvdpfile = '{:s}.cvdp_data.{:s}.nc' # filename needs to be extended with experiment name and period

# AMWG diagnostic variables
class Diag(FileType):
  ''' Variables and attributes of the AMWG diagnostic netcdf files. '''
  def __init__(self):
    self.atts = dict() # currently not implemented...                     
    self.vars = self.atts.keys()
    self.diagfile = NotImplemented # filename needs to be extended with experiment name and period

# axes (don't have their own file)
class Axes(FileType):
  ''' A mock-filetype for axes. '''
  def __init__(self):
    self.atts = dict(time        = dict(name='time', units='days', offset=-47116.0), # time coordinate (days since 1979-01-01)
                     TIME        = dict(name='year', units='year'), # yearly time coordinate in CVDP files
                     # N.B.: the time coordinate is only used for the monthly time-series data, not the LTM
                     #       the time offset is chose such that 1979 begins with the origin (time=0)
                     lon           = dict(name='lon', units='deg E'), # west-east coordinate
                     lat           = dict(name='lat', units='deg N'), # south-north coordinate
                     LON           = dict(name='lon', units='deg E'), # west-east coordinate (actually identical to lon!)
                     LAT           = dict(name='lat', units='deg N'), # south-north coordinate (actually identical to lat!)                     
                     levgrnd = dict(name='s', units=''), # soil layers
                     lev = dict(name='lev', units='')) # hybrid pressure coordinate
    self.vars = self.atts.keys()

# data source/location
fileclasses = dict(atm=ATM(), lnd=LND(), axes=Axes(), cvdp=CVDP()) # ice=ICE() is currently not supported because of the grid
# list of variables and dimensions that should be ignored
ignore_list_2D = ('nbnd', 'slat', 'slon', 'ilev', # atmosphere file
                  'levlak', 'latatm', 'hist_interval', 'latrof', 'lonrof', 'lonatm', # land file
                  ) # CVDP file (omit shifted longitude)
ignore_list_3D = ('lev', 'levgrnd',) # ignore all 3D variables (and vertical axes)

## Functions to load different types of CESM datasets

# CVDP diagnostics (monthly time-series, EOF pattern and correlations) 
def loadCVDP_Obs(name=None, grid=None, period=None, varlist=None, varatts=None, 
                 translateVars=None, lautoregrid=None, ignore_list=None, lindices=False, leofs=False):
  ''' Get a properly formatted monthly observational dataset as NetCDFDataset. '''
  if grid is not None: raise NotImplementedError
  # check datasets
  if name is None:
    if varlist is not None:
      if any(ocnvar in varlist for ocnvar in ('PDO','NINO34','AMO')): 
        name = 'HadISST'
      elif any(ocnvar in varlist for ocnvar in ('NAO','NPI','PNA', 'NPO')): 
        name = '20thC_ReanV2'
    else: raise ArgumentError, "Need to provide either 'name' or 'varlist'!"
  name = name.lower() # ignore case
  if name in ('hadisst','sst','ts'):
    name = 'HadISST'; period = period or (1920,2012)
  elif name in ('mlost','t2','tas'):
    name = 'MLOST'; period = period or (1920,2012)
  elif name in ('20thc_reanv2','ps','psl'):
    name = '20thC_ReanV2'; period = period or (1920,2012)
  elif name in ('gpcp','precip','prect','ppt'):
    name = 'GPCP'; period = period or (1979,2014)
  else: raise NotImplementedError, "The dataset '{:s}' is not available.".format(name)
  # load smaller selection
  if varlist is None and ( lindices or leofs ):
    varlist = []
  if lindices: varlist += fileclasses['cvdp'].indices
  if leofs: varlist += fileclasses['cvdp'].eofs
  return loadCESM_All(experiment=None, name=name, grid=grid, period=period, filetypes=('cvdp',), 
                      varlist=varlist, varatts=varatts, translateVars=translateVars, 
                      lautoregrid=lautoregrid, load3D=False, ignore_list=ignore_list, mode='CVDP', 
                      cvdp_mode='observations', lcheckExp=False)

# CVDP diagnostics (monthly time-series, EOF pattern and correlations) 
def loadCVDP(experiment=None, name=None, grid=None, period=None, varlist=None, varatts=None, 
             cvdp_mode=None, translateVars=None, lautoregrid=None, ignore_list=None, 
             lcheckExp=True, lindices=False, leofs=False, lreplaceTime=True):
  ''' Get a properly formatted monthly CESM climatology as NetCDFDataset. '''
  if grid is not None: raise NotImplementedError
#   if period is None: period = 15
  # load smaller selection
  if varlist is None and ( lindices or leofs ):
    varlist = []
    if lindices: varlist += fileclasses['cvdp'].indices
    if leofs: varlist += fileclasses['cvdp'].eofs
  return loadCESM_All(experiment=experiment, name=name, grid=grid, period=period, filetypes=('cvdp',), 
                  varlist=varlist, varatts=varatts, translateVars=translateVars, lautoregrid=lautoregrid, 
                  load3D=True, ignore_list=ignore_list, mode='CVDP', cvdp_mode=cvdp_mode, 
                  lcheckExp=lcheckExp, lreplaceTime=lreplaceTime)

# Station Time-Series (monthly)
def loadCESM_StnTS(experiment=None, name=None, station=None, filetypes=None, varlist=None, varatts=None,  
                   translateVars=None, load3D=False, ignore_list=None, lcheckExp=True, lreplaceTime=True):
  ''' Get a properly formatted CESM dataset with a monthly time-series at station locations. '''
  return loadCESM_All(experiment=experiment, name=name, grid=None, period=None, station=station, 
                      filetypes=filetypes, varlist=varlist, varatts=varatts, lreplaceTime=lreplaceTime, 
                      translateVars=translateVars, lautoregrid=False, load3D=load3D, 
                      ignore_list=ignore_list, mode='time-series', lcheckExp=lcheckExp)

# Station Time-Series (monthly)
def loadCESM_ShpTS(experiment=None, name=None, shape=None, filetypes=None, varlist=None, varatts=None,  
                   translateVars=None, load3D=False, ignore_list=None, lcheckExp=True, lreplaceTime=True,
                   lencl=False):
  ''' Get a properly formatted CESM dataset with a monthly time-series averaged over regions. '''
  return loadCESM_All(experiment=experiment, name=name, grid=None, period=None, shape=shape, lencl=lencl, 
                      filetypes=filetypes, varlist=varlist, varatts=varatts, lreplaceTime=lreplaceTime, 
                      translateVars=translateVars, lautoregrid=False, load3D=load3D, station=None, 
                      ignore_list=ignore_list, mode='time-series', lcheckExp=lcheckExp)

# Time-Series (monthly)
def loadCESM_TS(experiment=None, name=None, grid=None, filetypes=None, varlist=None, varatts=None,  
                translateVars=None, lautoregrid=None, load3D=False, ignore_list=None, lcheckExp=True,
                lreplaceTime=True):
  ''' Get a properly formatted CESM dataset with a monthly time-series. (wrapper for loadCESM)'''
  return loadCESM_All(experiment=experiment, name=name, grid=grid, period=None, station=None, 
                      filetypes=filetypes, varlist=varlist, varatts=varatts, translateVars=translateVars, 
                      lautoregrid=lautoregrid, load3D=load3D, ignore_list=ignore_list, mode='time-series', 
                      lcheckExp=lcheckExp, lreplaceTime=lreplaceTime)

# Station Climatologies (monthly)
def loadCESM_Stn(experiment=None, name=None, station=None, period=None, filetypes=None, varlist=None, 
                 varatts=None, translateVars=None, lautoregrid=None, load3D=False, ignore_list=None, 
                 lcheckExp=True):
  ''' Get a properly formatted CESM dataset with the monthly climatology at station locations. '''
  return loadCESM_All(experiment=experiment, name=name, grid=None, period=period, station=station, 
                      filetypes=filetypes, varlist=varlist, varatts=varatts, lreplaceTime=False, 
                      translateVars=translateVars, lautoregrid=lautoregrid, load3D=load3D, 
                      ignore_list=ignore_list, mode='climatology', lcheckExp=lcheckExp)

# Regional Climatologies (monthly)
def loadCESM_Shp(experiment=None, name=None, shape=None, period=None, filetypes=None, varlist=None, 
                 varatts=None, translateVars=None, lautoregrid=None, load3D=False, ignore_list=None, 
                 lcheckExp=True, lencl=False):
  ''' Get a properly formatted CESM dataset with the monthly climatology averaged over regions. '''
  return loadCESM_All(experiment=experiment, name=name, grid=None, period=period, station=None, 
                      shape=shape, lencl=lencl, filetypes=filetypes, varlist=varlist, varatts=varatts, 
                      lreplaceTime=False, translateVars=translateVars, lautoregrid=lautoregrid, 
                      load3D=load3D, ignore_list=ignore_list, mode='climatology', lcheckExp=lcheckExp)

# load minimally pre-processed CESM climatology files 
def loadCESM(experiment=None, name=None, grid=None, period=None, filetypes=None, varlist=None, 
             varatts=None, translateVars=None, lautoregrid=None, load3D=False, ignore_list=None, 
             lcheckExp=True, lencl=False):
  ''' Get a properly formatted monthly CESM climatology as NetCDFDataset. '''
  return loadCESM_All(experiment=experiment, name=name, grid=grid, period=period, station=None, 
                      filetypes=filetypes, varlist=varlist, varatts=varatts, translateVars=translateVars, 
                      lautoregrid=lautoregrid, load3D=load3D, ignore_list=ignore_list, mode='climatology', 
                      lcheckExp=lcheckExp, lreplaceTime=False)


# load any of the various pre-processed CESM climatology and time-series files 
def loadCESM_All(experiment=None, name=None, grid=None, station=None, shape=None, period=None, 
                 varlist=None, varatts=None, translateVars=None, lautoregrid=None, load3D=False, 
                 ignore_list=None, mode='climatology', cvdp_mode=None, lcheckExp=True, 
                 lreplaceTime=True, filetypes=None, lencl=False):
  ''' Get any of the monthly CESM files as a properly formatted NetCDFDataset. '''
  # period
  if isinstance(period,(tuple,list)):
    if not all(isNumber(period)): raise ValueError
  elif isinstance(period,basestring): period = [int(prd) for prd in period.split('-')]
  elif isinstance(period,(int,np.integer)) or period is None : pass # handled later
  else: raise DateError, "Illegal period definition: {:s}".format(str(period))
  # prepare input  
  lclim = False; lts = False; lcvdp = False; ldiag = False # mode switches
  if mode.lower() == 'climatology': # post-processed climatology files
    lclim = True
    folder,experiment,name = getFolderName(name=name, experiment=experiment, folder=None, mode='avg', lcheckExp=lcheckExp)    
    if period is None: raise DateError, 'Currently CESM Climatologies have to be loaded with the period explicitly specified.'
  elif mode.lower() in ('time-series','timeseries'): # concatenated time-series files
    lts = True
    folder,experiment,name = getFolderName(name=name, experiment=experiment, folder=None, mode='avg', lcheckExp=lcheckExp)
    lclim = False; period = None; periodstr = None # to indicate time-series (but for safety, the input must be more explicit)
    if lautoregrid is None: lautoregrid = False # this can take very long!
  elif mode.lower() == 'cvdp': # concatenated time-series files
    lcvdp = True
    folder,experiment,name = getFolderName(name=name, experiment=experiment, folder=None, mode='cvdp', 
                                           cvdp_mode=cvdp_mode, lcheckExp=lcheckExp)
    if period is None:
      if not isinstance(experiment,Exp): raise DatasetError, 'Periods can only be inferred for registered datasets.'
      period = (experiment.beginyear, experiment.endyear)  
  elif mode.lower() == 'diag': # concatenated time-series files
    ldiag = True
    folder,experiment,name = getFolderName(name=name, experiment=experiment, folder=None, mode='diag', lcheckExp=lcheckExp)
    raise NotImplementedError, "Loading AMWG diagnostic files is not supported yet."
  else: raise NotImplementedError,"Unsupported mode: '{:s}'".format(mode)  
  if station and shape: raise ArgumentError
  elif station or shape: 
    if grid is not None: raise NotImplementedError, 'Currently CESM station data can only be loaded from the native grid.'
    if lcvdp: raise NotImplementedError, 'CVDP data is not available as station data.'
    if lautoregrid: raise GDALError, 'Station data can not be regridded, since it is not map data.'   
    lstation = bool(station); lshape = bool(shape)
  else:
    lstation = False; lshape = False
  # period  
  if isinstance(period,(int,np.integer)):
    if not isinstance(experiment,Exp): raise DatasetError, 'Integer periods are only supported for registered datasets.'
    period = (experiment.beginyear, experiment.beginyear+period)
  if lclim: periodstr = '_{0:4d}-{1:4d}'.format(*period)
  elif lcvdp: periodstr = '{0:4d}-{1:4d}'.format(period[0],period[1]-1)
  else: periodstr = ''
  # N.B.: the period convention in CVDP is that the end year is included
  # generate filelist and attributes based on filetypes and domain
  if filetypes is None: filetypes = ['atm','lnd']
  elif isinstance(filetypes,(list,tuple,set)):
    filetypes = list(filetypes)  
    if 'axes' not in filetypes: filetypes.append('axes')    
  else: raise TypeError  
  atts = dict(); filelist = []; typelist = []
  for filetype in filetypes:
    fileclass = fileclasses[filetype]
    if lclim and fileclass.climfile is not None: filelist.append(fileclass.climfile)
    elif lts and fileclass.tsfile is not None: filelist.append(fileclass.tsfile)
    elif lcvdp and fileclass.cvdpfile is not None: filelist.append(fileclass.cvdpfile)
    elif ldiag and fileclass.diagfile is not None: filelist.append(fileclass.diagfile)
    typelist.append(filetype)
    atts.update(fileclass.atts) 
  # figure out ignore list  
  if ignore_list is None: ignore_list = set(ignore_list_2D)
  elif isinstance(ignore_list,(list,tuple)): ignore_list = set(ignore_list)
  elif not isinstance(ignore_list,set): raise TypeError
  if not load3D: ignore_list.update(ignore_list_3D)
  if lautoregrid is None: lautoregrid = not load3D # don't auto-regrid 3D variables - takes too long!
  # translate varlist
  if varatts is not None: atts.update(varatts)
  if varlist is not None:
    if translateVars is None: varlist = list(varlist) + translateVarNames(varlist, atts) # also aff translations, just in case
    elif translateVars is True: varlist = translateVarNames(varlist, atts) 
    # N.B.: DatasetNetCDF does never apply translation!
  # get grid or station-set name
  if lstation:
    # the station name can be inserted as the grid name
    gridstr = '_'+station.lower(); # only use lower case for filenames
    griddef = None
  elif lshape:
    # the station name can be inserted as the grid name
    gridstr = '_'+shape.lower(); # only use lower case for filenames
    griddef = None
  else:
    if grid is None or grid == experiment.grid: 
      gridstr = ''; griddef = None
    else: 
      gridstr = '_'+grid.lower() # only use lower case for filenames
      griddef = loadPickledGridDef(grid=grid, res=None, filename=None, folder=grid_folder, check=True)
  # insert grid name and period
  filenames = []
  for filetype,fileformat in zip(typelist,filelist):
    if lclim: filename = fileformat.format(gridstr,periodstr) # put together specfic filename for climatology
    elif lts: filename = fileformat.format(gridstr) # or for time-series
    elif lcvdp: filename = fileformat.format(experiment.name if experiment else name,periodstr) # not implemented: gridstr
    elif ldiag: raise NotImplementedError
    else: raise DatasetError
    filenames.append(filename) # append to list (passed to DatasetNetCDF later)
    # check existance
    filepath = '{:s}/{:s}'.format(folder,filename)
    if not os.path.exists(filepath):
      nativename = fileformat.format('',periodstr) # original filename (before regridding)
      nativepath = '{:s}/{:s}'.format(folder,nativename)
      if os.path.exists(nativepath):
        if lautoregrid: 
          from processing.regrid import performRegridding # causes circular reference if imported earlier
          griddef = loadPickledGridDef(grid=grid, res=None, folder=grid_folder)
          dataargs = dict(experiment=experiment, filetypes=[filetype], period=period)
          print("The '{:s}' (CESM) dataset for the grid ('{:s}') is not available:\n Attempting regridding on-the-fly.".format(name,filename,grid))
          if performRegridding('CESM','climatology' if lclim else 'time-series', griddef, dataargs): # default kwargs
            raise IOError, "Automatic regridding failed!"
          print("Output: '{:s}')".format(name,filename,grid,filepath))            
        else: raise IOError, "The '{:s}' (CESM) dataset '{:s}' for the selected grid ('{:s}') is not available - use the regrid module to generate it.".format(name,filename,grid) 
      else: raise IOError, "The '{:s}' (CESM) dataset file '{:s}' does not exits!\n({:s})".format(name,filename,folder)
   
  # load dataset
  #print varlist, filenames
  if experiment: title = experiment.title
  else: title = name
  dataset = DatasetNetCDF(name=name, folder=folder, filelist=filenames, varlist=varlist, axes=None, varatts=atts, 
                          title=title, multifile=False, ignore_list=ignore_list, ncformat='NETCDF4', squeeze=True)
  # replace time axis
  if lreplaceTime and (lts or lcvdp):
    # check time axis and center at 1979-01 (zero-based)
    if experiment is None: ys = period[0]; ms = 1
    else: ys,ms,ds = [int(t) for t in experiment.begindate.split('-')]; assert ds == 1
    if dataset.hasAxis('time'):
      ts = (ys-1979)*12 + (ms-1); te = ts+len(dataset.time) # month since 1979 (Jan 1979 = 0)
      atts = dict(long_name='Month since 1979-01')
      timeAxis = Axis(name='time', units='month', coord=np.arange(ts,te,1, dtype='int16'), atts=atts)
      dataset.replaceAxis(dataset.time, timeAxis, asNC=False, deepcopy=False)
    if dataset.hasAxis('year'):
      ts = ys-1979; te = ts+len(dataset.year) # month since 1979 (Jan 1979 = 0)
      atts = dict(long_name='years since 1979-01')
      yearAxis = Axis(name='year', units='year', coord=np.arange(ts,te,1, dtype='int16'), atts=atts)
      dataset.replaceAxis(dataset.year, yearAxis, asNC=False, deepcopy=False)
  # correct ordinal number of shape (should start at 1, not 0)
  if lshape:
    # mask all shapes that are incomplete in dataset
    if lencl and 'shp_encl' in dataset: dataset.mask(mask='shp_encl', invert=True)   
    if dataset.hasAxis('shapes'): raise AxisError, "Axis 'shapes' should be renamed to 'shape'!"
    if not dataset.hasAxis('shape'): raise AxisError
    if dataset.shape.coord[0] == 0: dataset.shape.coord += 1
  # check
  if len(dataset) == 0: raise DatasetError, 'Dataset is empty - check source file or variable list!'
  # add projection, if applicable
  if not ( lstation or lshape ):
    dataset = addGDALtoDataset(dataset, griddef=griddef, gridfolder=grid_folder, lwrap360=True, geolocator=True)
  # return formatted dataset
  return dataset

# load a pre-processed CESM ensemble and concatenate time-series (also for CVDP) 
def loadCESM_ShpEns(ensemble=None, name=None, shape=None, filetypes=None, years=None,
                    varlist=None, varatts=None, translateVars=None, load3D=False, 
                    ignore_list=None, lcheckExp=True, lencl=False):
  ''' A function to load all datasets in an ensemble and concatenate them along the time axis. '''
  return loadCESM_Ensemble(ensemble=ensemble, name=name, grid=None, station=None, shape=shape, 
                           filetypes=filetypes, years=years, varlist=varlist, varatts=varatts, 
                           translateVars=translateVars, lautoregrid=False, load3D=load3D, 
                           ignore_list=ignore_list, cvdp_mode='ensemble', lcheckExp=lcheckExp, 
                           mode='time-series', lreplaceTime=True, lencl=lencl)

# load a pre-processed CESM ensemble and concatenate time-series (also for CVDP) 
def loadCESM_StnEns(ensemble=None, name=None, station=None, filetypes=None, years=None,
                    varlist=None, varatts=None, translateVars=None, load3D=False, 
                    ignore_list=None, lcheckExp=True):
  ''' A function to load all datasets in an ensemble and concatenate them along the time axis. '''
  return loadCESM_Ensemble(ensemble=ensemble, name=name, grid=None, station=station, shape=None,
                           filetypes=filetypes, years=years, varlist=varlist, varatts=varatts, 
                           translateVars=translateVars, lautoregrid=False, load3D=load3D, 
                           ignore_list=ignore_list, cvdp_mode='ensemble', lcheckExp=lcheckExp, 
                           mode='time-series', lreplaceTime=True)

  
# load a pre-processed CESM ensemble and concatenate time-series (also for CVDP) 
def loadCESM_Ensemble(ensemble=None, name=None, grid=None, station=None, shape=None, filetypes=None, 
                      years=None, varlist=None, varatts=None, translateVars=None, lautoregrid=None, 
                      load3D=False, ignore_list=None, cvdp_mode='ensemble', lcheckExp=True, lencl=False, 
                      mode='time-series', lindices=False, leofs=False, lreplaceTime=True):
  ''' A function to load all datasets in an ensemble and concatenate them along the time axis. '''
  # obviously this only works for modes that produce a time-axis
  if mode.lower() not in ('time-series','timeseries','cvdp'): 
    raise ArgumentError, "Concatenated ensembles can not be constructed in mode '{:s}'".format(mode) 
  # figure out ensemble
  if isinstance(ensemble,Exp): ensemble = ensembles[ensemble.shortname]
  elif isinstance(ensemble,basestring): ensemble = ensembles[ensemble]
  else: raise TypeError    
  if isinstance(ensemble,(tuple,list)):
    if not all([isinstance(exp,(basestring,Exp)) for exp in ensemble]): raise TypeError
  # figure out time period
  if years is None: years =15; yrtpl = (0,15)
  elif isInt(years): yrtpl = (0,years)
  elif isinstance(years,(list,tuple)) and len(years)==2: raise NotImplementedError 
  else: raise TypeError  
  montpl = (0,years*12)
  # load datasets (and load!)
  datasets = []
  if mode.lower() in ('time-series','timeseries'): lts = True; lcvdp = False
  elif mode.lower() == 'cvdp': lts = False; lcvdp = True
  for exp in ensemble:
    if lts:
      ds = loadCESM_All(experiment=exp, name=name, grid=grid, station=station, shape=shape, varlist=varlist, 
                        varatts=varatts, translateVars=translateVars, period=None, lautoregrid=lautoregrid, 
                        load3D=load3D, ignore_list=ignore_list, filetypes=filetypes, lencl=lencl, 
                        mode=mode, cvdp_mode='', lcheckExp=lcheckExp, lreplaceTime=lreplaceTime)
    elif lcvdp:
      ds = loadCVDP(experiment=exp, name=name, varlist=varlist, varatts=varatts, period=years, 
                    translateVars=translateVars, lautoregrid=lautoregrid, lencl=lencl, 
                    ignore_list=ignore_list, cvdp_mode=cvdp_mode, lcheckExp=lcheckExp, 
                    lindices=lindices, leofs=leofs, lreplaceTime=lreplaceTime)
    else: raise NotImplementedError
    datasets.append(ds)
  # concatenate datasets (along 'time' and 'year' axis!)  
  if lts:
    dataset = concatDatasets(datasets, axis='time', coordlim=None, idxlim=montpl, 
                           offset=None, axatts=None, lcpOther=True, lcpAny=False)
  elif lcvdp:
    dataset = concatDatasets(datasets, axis=('time','year'), coordlim=None, idxlim=(montpl,yrtpl), 
                             offset=None, axatts=None, lcpOther=True, lcpAny=False)
  else: raise NotImplementedError
  # return concatenated dataset
  return dataset

## Dataset API

dataset_name = 'CESM' # dataset name
root_folder # root folder of the dataset
avgfolder # root folder for monthly averages
outfolder # root folder for direct WRF output
ts_file_pattern = 'cesm{0:s}{1:s}_monthly.nc' # filename pattern: filetype, grid
clim_file_pattern = 'cesm{0:s}{1:s}_clim{2:s}.nc' # filename pattern: filetype, grid, period
data_folder = root_folder # folder for user data
grid_def = {'':None} # there are too many... 
grid_res = {'':1.} # approximate grid resolution at 45 degrees latitude
default_grid = None 
# functions to access specific datasets
loadLongTermMean = None # WRF doesn't have that...
loadClimatology = loadCESM # pre-processed, standardized climatology
loadTimeSeries = loadCESM_TS # time-series data
loadStationClimatology = loadCESM_Stn # pre-processed, standardized climatology at stations
loadStationTimeSeries = loadCESM_StnTS # time-series data at stations
loadShapeClimatology = loadCESM_Shp # climatologies without associated grid (e.g. provinces or basins) 
loadShapeTimeSeries = loadCESM_ShpTS # time-series without associated grid (e.g. provinces or basins)


## (ab)use main execution for quick test
if __name__ == '__main__':
  
  # set mode/parameters
#   mode = 'test_climatology'
#   mode = 'test_timeseries'
#   mode = 'test_ensemble'
#   mode = 'test_point_climatology'
#   mode = 'test_point_timeseries'
#   mode = 'test_point_ensemble'
  mode = 'test_cvdp'
#   mode = 'pickle_grid'
#     mode = 'shift_lon'
#     experiments = ['Ctrl-1', 'Ctrl-A', 'Ctrl-B', 'Ctrl-C']
#     experiments += ['Ctrl-2050', 'Ctrl-A-2050', 'Ctrl-B-2050', 'Ctrl-C-2050']
  experiments = ('Ctrl-1-2050',)
  periods = (15,)
  filetypes = ('atm',) # ['atm','lnd','ice']
  grids = ('cesm1x1',)*len(experiments) # grb1_d01
  pntset = 'shpavg' # 'ecprecip'

  # pickle grid definition
  if mode == 'pickle_grid':
    
    for grid,experiment in zip(grids,experiments):
      
      print('')
      print('   ***   Pickling Grid Definition for {0:s}   ***   '.format(grid))
      print('')
      
      # load GridDefinition
      dataset = loadCESM(experiment=experiment, grid=None, filetypes=['lnd'], period=(1979,1989))
      griddef = dataset.griddef
      #del griddef.xlon, griddef.ylat      
      print griddef
      griddef.name = grid
      print('   Loading Definition from \'{0:s}\''.format(dataset.name))
      # save pickle
      filename = '{0:s}/{1:s}'.format(grid_folder,griddef_pickle.format(grid))
      if os.path.exists(filename): os.remove(filename) # overwrite
      filehandle = open(filename, 'w')
      pickle.dump(griddef, filehandle)
      filehandle.close()
      
      print('   Saving Pickle to \'{0:s}\''.format(filename))
      print('')
      
      # load pickle to make sure it is right
      del griddef
      griddef = loadPickledGridDef(grid, res=None, folder=grid_folder)
      print(griddef)
      print('')
      
  # load ensemble "time-series"
  elif mode == 'test_ensemble':
    
    print('')
#     dataset = loadCESM_Ensemble(ensemble='Ens-2050', varlist=['precip'], filetypes=['atm'])
    dataset = loadCESM_Ensemble(ensemble='Ens-2050', mode='cvdp')
    print('')
    print(dataset)
    print('')
    print(dataset.year)
    print(dataset.year.coord)
  
  # load station climatology file
  elif mode == 'test_point_climatology':
    
    print('')
    if pntset in ('shpavg',):
      dataset = loadCESM_Shp(experiment='Ctrl-1', shape=pntset, filetypes=['atm'], period=(1979,1994))
      print('')
      print(dataset)
      print('')
      print(dataset.shape)
      print(dataset.shape.coord)
      assert dataset.shape.coord[-1] == len(dataset.shape)  # this is a global model!    
    else:
      dataset = loadCESM_Stn(experiment='Ctrl-1', station=pntset, filetypes=['atm'], period=(1979,1994))
      print('')
      print(dataset)
      print('')
      print(dataset.station)
      print(dataset.station.coord)
      assert dataset.station.coord[-1] == len(dataset.station)  # this is a global model!
    
  # load station time-series file
  elif mode == 'test_point_timeseries':    
    print('')
    if pntset in ('shpavg',):
      dataset = loadCESM_ShpTS(experiment='Ctrl-1', shape=pntset, filetypes=['atm'])
    else:
      dataset = loadCESM_StnTS(experiment='Ctrl-1-2100', station=pntset, filetypes=['atm'])
    print('')
    print(dataset)
    print('')
    print(dataset.time)
    print(dataset.time.coord)
    
  # load station ensemble "time-series"
  elif mode == 'test_point_ensemble':
    
    print('')
    if pntset in ('shpavg',):
      dataset = loadCESM_ShpEns(ensemble='Ens', shape=pntset, filetypes=['atm'])
    else:
      dataset = loadCESM_StnEns(ensemble='Ens', station=pntset, filetypes=['atm'])
    print('')
    print(dataset)
    print('')
    print(dataset.time)
    print(dataset.time.coord)
  
  # load averaged climatology file
  elif mode == 'test_climatology' or mode == 'test_timeseries':
    
    for grid,experiment in zip(grids,experiments):
      
      print('')
      if mode == 'test_timeseries':
        dataset = loadCESM_TS(experiment=experiment, varlist=None, grid=grid, filetypes=filetypes)
      else:
        period = periods[0] # just use first element, no need to loop
        dataset = loadCESM(experiment=experiment, varlist=['precip'], grid=grid, filetypes=filetypes, period=period)
      print(dataset)
      print('')
      print(dataset.geotransform)
      if dataset.isProjected:
        print dataset.x
        print dataset.x.coord
      else:
        print dataset.lon
        print dataset.lon.coord
      if mode == 'test_timeseries':
        print('')      
        print(dataset.time)
        print(dataset.time.coord)
      # show some variables
#       if 'zs' in dataset: var = dataset.zs
#       elif 'hgt' in dataset: var = dataset.hgt
#       else: var = dataset.lon2D
#       var.load()
#       print var
#       var = var.mean(axis='time',checkAxis=False)
      # display
#       import pylab as pyl
#       pyl.pcolormesh(dataset.lon2D.getArray(), dataset.lat2D.getArray(), dataset.precip.getArray().mean(axis=0))
#       pyl.pcolormesh(dataset.lon2D.getArray(), dataset.lat2D.getArray(), dataset.runoff.getArray().mean(axis=0))
#       pyl.pcolormesh(dataset.lon2D.getArray(), dataset.lat2D.getArray(), var.getArray())
#       pyl.colorbar()
#       pyl.show(block=True)
  
  # load CVDP file
  elif mode == 'test_cvdp':
    
    for grid,experiment in zip(grids,experiments):
      
      print('')
      period = periods[0] # just use first element, no need to loop
      dataset = loadCVDP(experiment=experiment, period=period, cvdp_mode='ensemble') # lindices=True
      #dataset = loadCVDP_Obs(name='GPCP')
      print(dataset)
#       print(dataset.geotransform)
      print(dataset.year)
      print(dataset.year.coord)
      # print some variables
#       print('')
#       eof = dataset.pdo_pattern; eof.load()
# #       print eof
#       print('')
#       ts = dataset.pdo_timeseries; ts.load()
# #       print ts
#       print ts.mean()
      # display
#       import pylab as pyl
#       pyl.pcolormesh(dataset.lon2D.getArray(), dataset.lat2D.getArray(), dataset.precip.getArray().mean(axis=0))
#       pyl.pcolormesh(dataset.lon2D.getArray(), dataset.lat2D.getArray(), dataset.runoff.getArray().mean(axis=0))
#       pyl.pcolormesh(dataset.lon2D.getArray(), dataset.lat2D.getArray(), eof.getArray())
#       pyl.colorbar()
#       pyl.show(block=True)
      print('')
  
  # shift dataset from 0-360 to -180-180
  elif mode == 'shift_lon':
   
    # loop over periods
    for prdlen in periods: # (15,): # 
      # loop over experiments
      for experiment in experiments: # ('CESM',): #  
        # loop over filetypes
        for filetype in filetypes: # ('lnd',): #  
          fileclass = fileclasses[filetype]
          
          # load source
          exp = CESM_exps[experiment]
          period = (exp.beginyear, exp.beginyear+prdlen)
          periodstr = '{0:4d}-{1:4d}'.format(*period)
          print('\n')
          print('   ***   Processing Experiment {0:s} for Period {1:s}   ***   '.format(exp.title,periodstr))
          print('\n')
          # prepare file names
          filename = fileclass.climfile.format('','_'+periodstr)
          origname = 'orig'+filename[4:]; tmpname = 'tmp.nc'
          filepath = exp.avgfolder+filename; origpath = exp.avgfolder+origname; tmppath = exp.avgfolder+tmpname
          # load source
          if os.path.exists(origpath) and os.path.exists(filepath): 
            os.remove(filepath) # overwrite old file
            os.rename(origpath,filepath) # get original source
          source = loadCESM(experiment=exp, period=period, filetypes=[filetype])
          print(source)
          print('\n')
          # savety checks
          if os.path.exists(origpath): raise IOError
          if np.max(source.lon.getArray()) < 180.: raise AxisError
          if not os.path.exists(filepath): raise IOError
          # prepare sink
          if os.path.exists(tmppath): os.remove(tmppath)
          sink = DatasetNetCDF(name=None, folder=exp.avgfolder, filelist=[tmpname], atts=source.atts, mode='w')
          sink.atts.period = periodstr 
          sink.atts.name = exp.name
          
          # initialize processing
          CPU = CentralProcessingUnit(source, sink, tmp=False)
          
          # shift longitude axis by 180 degrees left (i.e. 0 - 360 -> -180 - 180)
          CPU.Shift(lon=-180, flush=True)
          
          # sync temporary storage with output
          CPU.sync(flush=True)
              
          # add new variables
          # liquid precip (atmosphere file)
          if sink.hasVariable('precip') and sink.hasVariable('solprec'):
            data = sink.precip.getArray() - sink.solprec.getArray()
            Var = Variable(axes=sink.precip.axes, name='liqprec', data=data, atts=default_varatts['liqprec'])            
            sink.addVariable(Var, asNC=True) # create variable and add to dataset
          # net precip (atmosphere file)
          if sink.hasVariable('precip') and sink.hasVariable('evap'):
            data = sink.precip.getArray() - sink.evap.getArray()
            Var = Variable(axes=sink.precip.axes, name='p-et', data=data, atts=default_varatts['p-et'])
            sink.addVariable(Var, asNC=True) # create variable and add to dataset      
          # underground runoff (land file)
          if sink.hasVariable('runoff') and sink.hasVariable('sfroff'):
            data = sink.runoff.getArray() - sink.sfroff.getArray()
            Var = Variable(axes=sink.runoff.axes, name='ugroff', data=data, atts=default_varatts['ugroff'])
            sink.addVariable(Var, asNC=True) # create variable and add to dataset    
    
          # add length and names of month
          if sink.hasAxis('time', strict=False):
            addLengthAndNamesOfMonth(sink, noleap=True)     
          # close...
          sink.sync()
          sink.close()
          
          # move files
          os.rename(filepath, origpath)
          os.rename(tmppath,filepath)
          
          # print dataset
          print('')
          print(sink)               
