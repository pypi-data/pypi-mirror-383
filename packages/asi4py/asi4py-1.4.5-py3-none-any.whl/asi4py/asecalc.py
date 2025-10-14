from ase.calculators.calculator import Calculator, all_changes, PropertyNotImplementedError
from .pyasi import ASIlib
from ase import units
from ase.parallel import parprint
from ase.stress import full_3x3_to_voigt_6_stress
"""
# FHI-AIMS conversion constants
bohr    = 0.52917721
hartree = 27.2113845
hartree_over_bohr = 51.42206426
bohr_over_hartree = 0.019446905
"""
bohr    = units.Bohr
hartree = units.Hartree


class ASI_ASE_calculator(Calculator):
  '''
    ASI ASI calc
  '''
  implemented_properties = ['energy', 'free_energy', 'forces', 'charges', 'stress']
  supported_changes = {'positions', 'cell'}

  def __init__(self, asi_lib, init_func=None, mpi_comm=None, atoms=None, work_dir='asi.temp', logfile='asi.log'):
    try:
      Calculator.__init__(self)
      self.callback = None
      #!! self.atoms = atoms.copy()
      if isinstance(asi_lib, ASIlib):
        self.asi = asi_lib
      else:
        self.asi = ASIlib(asi_lib, init_func, mpi_comm, atoms, work_dir, logfile)
        self.asi.init()
      self.DM_init_callback = None
    except Exception  as err:
      print ("Error in init",err)
      raise err

  def todict(self):
      d = {'type': 'calculator',
           'name': 'ASI wrapper'}
      return d

  def calculate(self, atoms=None, properties=['energy'],
                system_changes=supported_changes):
      bad = [change for change in system_changes
             if change not in self.supported_changes] # TODO now is ignored
      
      #parprint("calculate", properties, system_changes, bad, atoms, self.atoms, self.asi.atoms)

      # First time calculate() is called, system_changes will be
      # all_changes.  After that, only positions and cell may change.
      if self.atoms is not None and any(bad):
          raise PropertyNotImplementedError(
              'Cannot change {} through ASI API.  '
              .format(bad if len(bad) > 1 else bad[0]))

      if len(system_changes) > 0:
        self.atoms = atoms.copy()
        self.asi.atoms = atoms
        self.asi.set_geometry()
        self.asi.run()

      results = {}
      results['free_energy'] = results['energy'] = self.asi.total_energy * hartree
      
      if 'forces' in properties:
        if self.asi.total_forces is not None:
          results['forces'] = self.asi.total_forces * (hartree / bohr)

      if 'stress' in properties:
        if self.asi.stress is not None:
          stress_3x3 = self.asi.stress * (hartree / (bohr**3))
          results['stress'] = full_3x3_to_voigt_6_stress(stress_3x3)

      # Charges computation breaks total_energy on subsequent SCF calculations in AIMS:  results['charges'] = self.asi.atomic_charges

      if self.callback is not None:
        self.callback(self, system_changes, results)
      self.results.update(results)

  def close(self):
      if hasattr(self, 'asi'):
        self.asi.close()
  
  def attach(self, callback):
    self.callback = callback

  def __del__(self):
      self.close()
