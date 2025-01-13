from morpheus.utils.information import print_information, print_logo

from rdkit import RDLogger

def disable_rdkit_logging():
  RDLogger.DisableLog("rdApp.*")
  
def enable_rdkit_logging():
  RDLogger.EnableLog("rdApp.*")

print_logo()
print_information()
disable_rdkit_logging()