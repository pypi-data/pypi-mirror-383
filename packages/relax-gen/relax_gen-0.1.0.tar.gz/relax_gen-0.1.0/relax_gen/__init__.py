from .gen import GEN
from .algorithms.alg_bin import cl_alg_stn_bin_rank
from .algorithms.alg_quantum import cl_alg_quantum

class RelaxGEN(GEN):
    def alg_stn_bin_rank(self, *args, **kwargs):
        algoritmo = cl_alg_stn_bin_rank(*args, **kwargs)
        return algoritmo.run()

    def alg_quantum(self, *args, **kwargs):
        algoritmo = cl_alg_quantum(*args, **kwargs)
        return algoritmo.run()
