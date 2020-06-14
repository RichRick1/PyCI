/* This file is part of PyCI.
 *
 * PyCI is free software: you can redistribute it and/or modify it under
 * the terms of the GNU General Public License as published by the Free
 * Software Foundation, either version 3 of the License, or (at your
 * option) any later version.
 *
 * PyCI is distributed in the hope that it will be useful, but WITHOUT
 * ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
 * FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License
 * for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with PyCI. If not, see <http://www.gnu.org/licenses/>. */

#pragma once

#include <vector>

#include <parallel_hashmap/phmap.h>

#include <pyci/common.h>


namespace pyci {


struct DOCIWfn;


struct DOCIWfn
{
    typedef hashmap<int_t, int_t> hashmap_type;

    int_t nword, nbasis, nocc, nvir, ndet;
    std::vector<uint_t> dets;
    hashmap_type dict;

    DOCIWfn();
    DOCIWfn(const int_t, const int_t);
    DOCIWfn(const DOCIWfn &);
    DOCIWfn(const char *);
    DOCIWfn(const int_t, const int_t, const int_t, const uint_t *);
    DOCIWfn(const int_t, const int_t, const int_t, const int_t *);
    ~DOCIWfn();

    void init(const int_t, const int_t);
    void from_dociwfn(const DOCIWfn &);
    void from_file(const char *);
    void from_det_array(const int_t, const int_t, const int_t, const uint_t *);
    void from_occs_array(const int_t, const int_t, const int_t, const int_t *);
    void to_file(const char *) const;
    void to_occs_array(const int_t, const int_t, int_t *) const;
    int_t index_det(const uint_t *) const;
    void copy_det(const int_t, uint_t *) const;
    int_t add_det(const uint_t *);
    int_t add_det_from_occs(const int_t *);
    void add_all_dets();
    void add_excited_dets(const uint_t *, const int_t);
    void reserve(const int_t);
    void squeeze();
};


void compute_rdms(const DOCIWfn &, const double *, double *, double *);


double compute_energy(const DOCIWfn &, const double *, const double *, const double *, const double *);


int_t run_hci(DOCIWfn &, const double *, const double *, const double);


} // namespace pyci