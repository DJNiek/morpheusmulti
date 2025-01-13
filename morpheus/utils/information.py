import random
from colored import Fore
import rdkit
from pathlib import Path
import tempfile

MORPHEUS = """
  . ✦  .˳ · ˖  ✶  ⋆  .˳    *      ⋆    ˖  ˚ .  ✦ ˳     *    ✶   ˖     . ✦
      ✦   _.._    *   ___  ___          · ⋆    _   ⋆   ✶        .             
   ˚    .' .-'`˚   ˖  |  \/  |  ˚ .  ✦        | |         ˖  .     ✦   ˚  
     . /  / ✶       ✦ | .  . | ___  _ __ _⋆__ | |__✦  ___ _   _ ___      
 *     |  |       ˖   | |\/| |/ _ \| '__| '_ \| '_ \ / _ \ | | / __| *   
   ⋆   \  \  .  ˚   ⋆ | |  | | (_) | |  | |_) | | | |  __/ |_| \__ \   ⋆ 
    .˳  '._'-._   ˳  .\_|  |_/\___/|_|  | .__/|_| |_|\___|\__,_|___/    .
           ```      ˖                   | |   ˚  *       ✦     ˖             
 ˚ .  ✦  ˳ ˖  *  ·  ⋆  * ·   ✶   ·  .   |_| .     ✦    ˳         *   ˚ .     
. ✦  .˳ · ˖  ✶  ⋆  .˳    *      ⋆    ˖   .  ✦ ˳     *    ✶   ˖      . ✦  
"""

NAMESPACE = "morpheus"

TMP_DIR = Path(f"{tempfile.gettempdir()}/{NAMESPACE}/")
if not TMP_DIR.exists():
    TMP_DIR.mkdir(exist_ok=True, parents=True)


def print_logo():
  m = ""

  for c in MORPHEUS:
      if "˚. ✦.˳·˖✶ ⋆.✧˚.".__contains__(c):
          if random.random() < 0.6:
              m += Fore.yellow if random.random() < 0.5 else Fore.magenta
      m += c
      m += Fore.white
      
  print(m)

def print_information():
  print("-------------------------------------------------------------------------")
  print("| Version 0.1.0.TEST                            Programmer: Elias Rusch |")
  print("-------------------------------------------------------------------------")
  print(f"| Using rdKit version {rdkit.__version__}                 Using xtb version 6.7.0 |")
  print("-------------------------------------------------------------------------")
