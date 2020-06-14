# This file is part of PyCI.
#
# PyCI is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your
# option) any later version.
#
# PyCI is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License
# for more details.
#
# You should have received a copy of the GNU General Public License
# along with PyCI. If not, see <http://www.gnu.org/licenses/>.

from nose.tools import assert_raises

import numpy as np
import numpy.testing as npt

from pyci import doci
from pyci.utils import comb

from pyci.test import datafile


class TestRoutines:

    CASES = {
        'he_ccpvqz': (1, -2.886809115915473),
        'be_ccpvdz': (2, -14.60055699423718),
        'li2_ccpvdz': (3, -14.878455348858425),
        'h2o_ccpvdz': (5, -75.63458842226694),
        }

    def test_solve_ci_sparse(self):
        for filename in self.CASES.keys():
            yield self.run_solve_ci_sparse, filename

    def test_compute_rdms(self):
        for filename in self.CASES.keys():
            yield self.run_compute_rdms, filename

    def test_compute_energy(self):
        for filename in self.CASES.keys():
            yield self.run_compute_energy, filename

    def test_run_hci(self):
        nocc, energy = self.CASES['h2o_ccpvdz']
        ham = doci.ham.from_file(datafile('h2o_ccpvdz.fcidump'))
        wfn = doci.wfn(ham.nbasis, nocc)
        wfn.reserve(comb(wfn.nbasis, wfn.nocc))
        wfn.add_hartreefock_det()
        op = doci.sparse_op(ham, wfn)
        es, cs = op.solve(n=1, ncv=30, tol=1.0e-6)
        dets_added = 1
        niter = 0
        while dets_added:
            dets_added = doci.run_hci(ham, wfn, cs[0], eps=1.0e-5)
            op = doci.sparse_op(ham, wfn)
            es, cs = op.solve(n=1, ncv=30, tol=1.0e-6)
            niter += 1
        assert niter > 1
        assert len(wfn) < comb(wfn.nbasis, wfn.nocc)
        npt.assert_allclose(es[0], energy, rtol=0.0, atol=1.0e-6)
        dets_added = 1
        while dets_added:
            dets_added = doci.run_hci(ham, wfn, cs[0], eps=0.0)
            op = doci.sparse_op(ham, wfn)
            es, cs = op.solve(n=1, ncv=30, tol=1.0e-6)
        assert len(wfn) == comb(wfn.nbasis, wfn.nocc)
        npt.assert_allclose(es[0], energy, rtol=0.0, atol=1.0e-9)

    def run_solve_ci_sparse(self, filename):
        nocc, energy = self.CASES[filename]
        ham = doci.ham.from_file(datafile('{0:s}.fcidump'.format(filename)))
        wfn = doci.wfn(ham.nbasis, nocc)
        wfn.add_all_dets()
        op = doci.sparse_op(ham, wfn)
        es, cs = op.solve(n=1, ncv=30, tol=1.0e-6)
        npt.assert_allclose(es[0], energy, rtol=0.0, atol=1.0e-9)

    def run_compute_rdms(self, filename):
        nocc, energy = self.CASES[filename]
        ham = doci.ham.from_file(datafile('{0:s}.fcidump'.format(filename)))
        wfn = doci.wfn(ham.nbasis, nocc)
        wfn.add_all_dets()
        op = doci.sparse_op(ham, wfn)
        es, cs = op.solve(n=1, ncv=30, tol=1.0e-6)
        d0, d2 = doci.compute_rdms(wfn, cs[0])
        npt.assert_allclose(np.trace(d0), wfn.nocc, rtol=0, atol=1.0e-9)
        npt.assert_allclose(np.sum(d2), wfn.nocc * (wfn.nocc - 1), rtol=0, atol=1.0e-9)
        k0 = ham.reduced_v(nocc)
        k2 = ham.reduced_w(nocc)
        energy = ham.ecore
        energy += np.einsum('ij,ij', k0, d0)
        energy += np.einsum('ij,ij', k2, d2)
        npt.assert_allclose(energy, es[0], rtol=0.0, atol=1.0e-9)
        rdm1, rdm2 = doci.generate_rdms(d0, d2)
        with np.load(datafile('{0:s}_spinres.npz'.format(filename))) as f:
            one_mo = f['one_mo']
            two_mo = f['two_mo']
        energy = ham.ecore
        energy += np.einsum('ij,ij', one_mo, rdm1)
        energy += 0.25 * np.einsum('ijkl,ijkl', two_mo, rdm2)
        npt.assert_allclose(energy, es[0], rtol=0.0, atol=1.0e-9)

    def run_compute_energy(self, filename):
        nocc, energy = self.CASES[filename]
        ham = doci.ham.from_file(datafile('{0:s}.fcidump'.format(filename)))
        wfn = doci.wfn(ham.nbasis, nocc)
        wfn.add_all_dets()
        op = doci.sparse_op(ham, wfn)
        es, cs = op.solve(n=1, ncv=30, tol=1.0e-6)
        npt.assert_allclose(doci.compute_energy(ham, wfn, cs[0]), energy, rtol=0.0, atol=1.0e-9)