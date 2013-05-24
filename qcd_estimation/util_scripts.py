from Dataset import *
from DatasetGroup import *
from ROOT import *
from copy import copy

def open_all_data_files(data_group, mc_groups, QCD_group, paths):
    files = {}
    all_groups = copy(mc_groups)
    all_groups.append(data_group)
    if QCD_group is not None:
        all_groups.append(QCD_group)
    for group in all_groups:
        for ds in group.getDatasets():
            for iso in paths:
                for syst in paths[iso]:
                   f = TFile(paths[iso][syst]+ds.getFileName())
                   files[ds.getName()+"_"+iso+syst]=f
                   count_hist = f.Get("trees").Get("count_hist")
                   if not count_hist:
                      raise TObjectOpenException("Failed to open count histogram")
                   ds.setOriginalEventCount(count_hist.GetBinContent(1))
                   ds.addFile(syst, iso, files[ds.getName()+"_"+iso+syst])
                   #print "after adding ",ds._files
    return files

def generate_paths(systematics, base_path):
    isos = ["iso", "antiiso"]
    paths = {}
    for iso in isos:
        paths[iso] = {}
        for syst in systematics:
            path = base_path + "/" + iso + "/" + syst
            paths[iso][syst] = path
    return paths

def clear_histos(data_group, mc_groups):
   all_groups = mc_groups
   all_groups.append(data_group)
   for group in all_groups:
      group.cleanHistograms()
   
"""def open_all_data_files_old(data_group, mc_groups, isos, systematics, path):
   files = {}
   all_groups = copy(mc_groups)
   all_groups.append(data_group)
   for group in all_groups:
      for ds in group.getDatasets():
         for iso in isos:
            for syst in systematics:
               f = TFile(path+iso+"/nominal/"+ds.getFileName())
               #print path+iso+"/"+ds.getFileName()+syst
               files[ds.getName()+"_"+iso+syst]=f
               #print ds._files
               #print "add ", ds.getName(), syst, iso
               count_hist = f.Get("trees").Get("count_hist")
               if not count_hist:
                  raise TObjectOpenException("Failed to open count histogram")
               ds.setOriginalEventCount(count_hist.GetBinContent(1))
               ds.addFile(syst, iso, files[ds.getName()+"_"+iso+syst])
               #print "after adding ",ds._files
   return files
"""
