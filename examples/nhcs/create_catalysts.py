#as far as i can see, this piece of code is to generate a large library of NHCs which can be used as possible catalysts. It would be unwise to calculate reaction energy as the reaction energy of the NHC is somewhat irrelevant to the 
#effectiveness of the catalyst.

from pathlib import Path
from threading import Thread
import numpy as np

from morpheus.molecule import Smiles
from morpheus.reaction import Reaction, ReactionTemplate

NUM_THREADS = 12

carbonyls = [Smiles(smiles) for smiles in open(Path(f"data/carbonyls.smiles")).read().splitlines()]
amines = [Smiles(smiles) for smiles in open(Path(f"data/amines.smiles")).read().splitlines()]

summary = open(Path(f"data/nhc.smiles"), "a+")
summary.truncate(0)

ALL = False

reactions = []
for c in range(len(carbonyls)):
  for a in range(len(amines)):
      reactions.append((c, a))

carbonyl_amine_condensation = ReactionTemplate(
    r"[#6:1]~[#7;H0&D2:2]~[#6:3]-[#6;!R&v4:4](=[#8;!R&v2])-[#1,#6:5].[$([#7&H2]),$([#7+&H3]):6]~[#6:7]>>[#6:1]-[#7:2]([C-]=[#7+:6]([#6:7])[#6:4]([#1,#6:5])=2)[#6:3]2"
)

thread_outputs = [[] for _ in range(NUM_THREADS)]
def write(thread_idx, data):
  thread_outputs[thread_idx].append(data)

def chunk_into_n(lst, n):
  return list(map(lambda x: list(x), np.array_split(lst, n)))

def start_thread(*args) -> Thread:
  thread = Thread(target=process_chunk, args=args)
  thread.start()
  return thread

def process_chunk(thread_idx, chunk):
  outfile = open(Path(f"data/nhc.smiles{thread_idx}"), "a+")
  outfile.truncate(0)

  idx = 0

  for (c, a) in chunk:
    idx += 1

    if idx % 100000 == 0:
      outfile.close()
      outfile = open(Path(f"data/nhc.smiles{thread_idx}"), "a+")

    amine = amines[a]
    carbonyl = carbonyls[c]
    
    reaction = Reaction(carbonyl_amine_condensation)
    reaction.add_reactants([carbonyl, amine])
    reaction.run_reaction()
    if reaction.products:
      outfile.write(reaction.products[0].products[0])
      write(thread_idx, reaction.products[0].products[0])

chunks = chunk_into_n(reactions, NUM_THREADS)

threads = []
for thread_idx in range(NUM_THREADS):
  threads.append(start_thread(thread_idx, chunks[thread_idx]))
  
for thread in threads:
  thread.join()
  
for nhc in sum(thread_outputs,[]):
  summary.write(f"{nhc}\n")
