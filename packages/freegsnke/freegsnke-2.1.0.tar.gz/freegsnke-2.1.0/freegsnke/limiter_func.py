"""
Defines the functionality related to the implementation of the limiter in FreeGSNKE. 

Copyright 2025 UKAEA, UKRI-STFC, and The Authors, as per the COPYRIGHT and README files.

This file is part of FreeGSNKE.

FreeGSNKE is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU Lesser General Public License for more details.

FreeGSNKE is free software: you can redistribute it and/or modify
it under the terms of the GNU Lesser General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
  
You should have received a copy of the GNU Lesser General Public License
along with FreeGSNKE.  If not, see <http://www.gnu.org/licenses/>.   
"""

import numpy as np
from matplotlib.path import Path


class Limiter_handler:

    def __init__(self, eq, limiter):
        """Object to handle additional calculations due to the limiter.
        This is primarily used by the profile functions.
        Each profile function has its own instance of a Limiter_handler.

        Parameters
        ----------
        eq : FreeGSNKE equilibrium object
            Used as a source of info on the solver's grid.
        limiter : a tokamak.Wall object
            Contains a list of R and Z coordinates (the vertices) which define the region accessible to the plasma.
            The boundary itself is the limiter.
        """

        self.limiter = limiter
        self.eqR = eq.R
        self.eqZ = eq.Z
        self.eqR_1D = self.eqR[:, 0]
        self.eqZ_1D = self.eqZ[0, :]

        self.dR = self.eqR[1, 0] - self.eqR[0, 0]
        self.dZ = self.eqZ[0, 1] - self.eqZ[0, 0]
        self.dRdZ = self.dR * self.dZ
        self.nx, self.ny = np.shape(eq.R)
        self.nxny = self.nx * self.ny
        self.map2d = np.zeros_like(eq.R)
        self.eqRidx = np.tile(np.arange(self.nx)[:, np.newaxis], (1, self.ny))
        self.eqZidx = np.tile(np.arange(self.ny)[:, np.newaxis], (1, self.nx)).T

        self.build_mask_inside_limiter()
        self.limiter_points()
        self.plasma_pts = self.extract_plasma_pts(eq.R, eq.Z, self.mask_inside_limiter)
        self.idxs_mask = self.extract_index_mask(self.mask_inside_limiter)

    def extract_index_mask(self, mask):
        """Extracts the indices of the R and Z coordinates of the grid points in the reduced plasma domain
           i.e. inside the limiter

        Parameters
        ----------
        mask : np.ndarray of bool
            Specifies the mask of the relevant region
        """

        nx, ny = np.shape(mask)
        idxs_mask = np.mgrid[0:nx, 0:ny][np.tile(mask, (2, 1, 1))].reshape(2, -1)

        return idxs_mask

    def extract_plasma_pts(self, R, Z, mask):
        """Extracts R and Z coordinates of the grid points in the reduced plasma domain
           i.e. inside the limiter

        Parameters
        ----------
        R : np.ndarray
            R coordinates on the domain grid, e.g. eq.R
        Z : np.ndarray
            Z coordinates on the domain grid, e.g. eq.Z
        mask : np.ndarray of bool
            Specifies the mask of the relevant region
        """
        plasma_pts = np.concatenate(
            (
                R[mask][:, np.newaxis],
                Z[mask][:, np.newaxis],
            ),
            axis=-1,
        )

        return plasma_pts

    def reduce_rect_domain(self, map):
        """Reduce map from the whole domain to the smallest rectangular domain around limiter mask

        Parameters
        ----------
        map : np.ndarray
            Same dimensions as eq.R
        """

        return map[self.Rrange[0] : self.Rrange[1], self.Zrange[0] : self.Zrange[1]]

    def build_reduced_rect_domain(
        self,
    ):
        """Build smallest rectangular domain around limiter mask"""

        self.Rrange = (min(self.idxs_mask[0]), max(self.idxs_mask[0]) + 1)
        self.Zrange = (min(self.idxs_mask[1]), max(self.idxs_mask[1]) + 1)

        # self.eqR_red = self.reduce_rect_domain(self.eqR)
        # self.eqZ_red = self.reduce_rect_domain(self.eqZ)
        self.mask_inside_limiter_red = self.reduce_rect_domain(self.mask_inside_limiter)

    def build_mask_inside_limiter(
        self,
    ):
        """Uses the coordinates of points along the edge of the limiter region
        to generate the mask of contained domain points.

        Parameters
        ----------
        eq : FreeGSNKE Equilibrium object
            Specifies the domain properties
        limiter : freegs4e.machine.Wall object
            Specifies the limiter contour points
        Returns
        -------
        mask_inside_limiter : np.array
            Mask over the full domain of grid points inside the limiter region.
        """
        verts = np.concatenate(
            (
                np.array(self.limiter.R)[:, np.newaxis],
                np.array(self.limiter.Z)[:, np.newaxis],
            ),
            axis=-1,
        )
        path = Path(verts)

        points = np.concatenate(
            (self.eqR[:, :, np.newaxis], self.eqZ[:, :, np.newaxis]), axis=-1
        )

        mask_inside_limiter = path.contains_points(points.reshape(-1, 2))
        mask_inside_limiter = mask_inside_limiter.reshape(self.nx, self.ny)
        self.mask_inside_limiter = mask_inside_limiter
        self.path = path

    def broaden_mask(self, mask, layer_size=3):
        """Creates a mask that is wider than the input mask, by a width=`layer_size`

        Parameters
        ----------
        layer_size : int, optional
            Width of the layer, by default 3

        Returns
        -------
        layer_mask : np.ndarray
            Broader mask
        """
        nx, ny = np.shape(mask)

        layer_mask = np.zeros(
            np.array([nx, ny]) + 2 * np.array([layer_size, layer_size])
        )

        for i in np.arange(-layer_size, layer_size + 1) + layer_size:
            for j in np.arange(-layer_size, layer_size + 1) + layer_size:
                layer_mask[i : i + nx, j : j + ny] += mask
        layer_mask = layer_mask[
            layer_size : layer_size + nx, layer_size : layer_size + ny
        ]
        layer_mask = (layer_mask > 0).astype(bool)
        return layer_mask

    def make_layer_mask(self, mask, layer_size=3):
        """Creates a mask for the points just outside the input mask, with a width=`layer_size`

        Parameters
        ----------
        layer_size : int, optional
            Width of the layer outside the limiter, by default 3

        Returns
        -------
        layer_mask : np.ndarray
            Mask of the points outside the mask within a distance of `layer_size`
        """

        layer_mask = self.broaden_mask(mask, layer_size=layer_size)
        layer_mask = layer_mask * np.logical_not(mask)
        return layer_mask.astype(bool)

    def limiter_points(self, refine=16):
        """Based on the limiter vertices, it builds the refined list of points on the boundary
        of the region where the plasma is allowed. These refined boundary points are those on which the flux
        function is interpolated to find the value of psi_boundary in the case of a limiter plasma.

        Parameters
        ----------
        refine : int, optional
            the upsampling ratio with respect to the solver's grid, by default 6.

        """
        verts = np.concatenate(
            (
                np.array(self.limiter.R)[:, np.newaxis],
                np.array(self.limiter.Z)[:, np.newaxis],
            ),
            axis=-1,
        )
        dverts = verts[1:] - verts[:-1]
        idxR = (
            np.sum(
                np.tile(self.eqR_1D[np.newaxis], (len(verts), 1)) < verts[:, :1], axis=1
            )
            - 1
        )
        idxZ = (
            np.sum(
                np.tile(self.eqZ_1D[np.newaxis], (len(verts), 1)) < verts[:, 1:], axis=1
            )
            - 1
        )

        all_fine_verts = []
        for i in range(len(verts) - 1):

            if dverts[i, 0] == 0:
                # line is vertical
                # line can only intersect the horizontal grid
                min_Z = min(idxZ[i : i + 2])
                max_Z = max(idxZ[i : i + 2])
                Zvals = self.eqZ_1D[min_Z + 1 : max_Z + 1]
                Rvals = np.array([verts[i, 0]] * len(Zvals))
                fine_verts = np.array([Rvals, Zvals]).T

            elif dverts[i, 1] == 0:
                # line is horizontal
                # line can only intersect the vertical grid
                min_R = min(idxR[i : i + 2])
                max_R = max(idxR[i : i + 2])
                Rvals = self.eqR_1D[min_R + 1 : max_R + 1]
                Zvals = np.array([verts[i, 1]] * len(Rvals))
                fine_verts = np.array([Rvals, Zvals]).T

            else:
                # not vertical
                aa = dverts[i, 1] / dverts[i, 0]
                bb = verts[i, 1] - aa * verts[i, 0]

                # add all intersections with the vertical grid
                min_R = min(idxR[i : i + 2])
                max_R = max(idxR[i : i + 2])
                Rvals = self.eqR_1D[min_R + 1 : max_R + 1]
                Zvals = aa * Rvals + bb
                fine_verts = np.array([Rvals, Zvals]).T
                # add all intersections with the horizontal grid
                min_Z = min(idxZ[i : i + 2])
                max_Z = max(idxZ[i : i + 2])
                Zvals = self.eqZ_1D[min_Z + 1 : max_Z + 1]
                Rvals = (Zvals - bb) / aa
                fine_verts = np.concatenate(
                    (fine_verts, np.array([Rvals, Zvals]).T), axis=0
                )

            # add second vertex
            fine_verts = np.concatenate((fine_verts, verts[i + 1 : i + 2]), axis=0)
            # sort locally
            fine_verts = fine_verts[
                np.argsort(np.linalg.norm(fine_verts - verts[i + 1 : i + 2], axis=1))
            ]

            all_fine_verts.append(fine_verts)

        fine_points = np.concatenate(all_fine_verts, axis=0)

        # refined_ddiag = (self.dR**2 + self.dZ**2) ** 0.5 / refine
        # fine_points = []
        # for i in range(1, len(verts)):
        #     dv = verts[i : i + 1] - verts[i - 1 : i]
        #     ndv = np.linalg.norm(dv)
        #     nn = np.round(ndv // refined_ddiag).astype(int)
        #     if nn:
        #         points = dv * np.arange(nn)[:, np.newaxis] / nn
        #         points += verts[i - 1 : i]
        #         fine_points.append(points)
        # fine_points = np.concatenate(fine_points, axis=0)

        # finds the grid vertex with coords just left-below each of the fine_points along the limiter
        Rvals = self.eqR[:, 0]
        Ridxs = np.sum(Rvals[np.newaxis, :] < fine_points[:, :1], axis=1) - 1
        Zvals = self.eqZ[0, :]
        Zidxs = np.sum(Zvals[np.newaxis, :] < fine_points[:, 1:2], axis=1) - 1
        self.grid_per_limiter_fine_point = np.concatenate(
            (Ridxs[:, np.newaxis], Zidxs[:, np.newaxis]), axis=-1
        )
        # saves the mask of all gridpoints that are just left-below any limiter fine-point
        self.mask_limiter_cells = np.zeros_like(self.eqR)
        self.mask_limiter_cells[
            self.grid_per_limiter_fine_point[:, 0],
            self.grid_per_limiter_fine_point[:, 1],
        ] = 1
        self.mask_limiter_cells = self.mask_limiter_cells.astype(bool)

        self.limiter_mask_out = self.make_layer_mask(
            np.logical_not(self.mask_inside_limiter), 1
        )
        self.offending_mask = np.zeros_like(self.eqR).astype(bool)

        self.fine_point_per_cell = {}
        self.fine_point_per_cell_R = {}
        self.fine_point_per_cell_Z = {}
        for i in range(len(fine_points)):
            if (Ridxs[i], Zidxs[i]) not in self.fine_point_per_cell.keys():
                self.fine_point_per_cell[Ridxs[i], Zidxs[i]] = []
                self.fine_point_per_cell_R[Ridxs[i], Zidxs[i]] = []
                self.fine_point_per_cell_Z[Ridxs[i], Zidxs[i]] = []
            self.fine_point_per_cell[Ridxs[i], Zidxs[i]].append(i)
            self.fine_point_per_cell_R[Ridxs[i], Zidxs[i]].append(
                [
                    self.eqR[Ridxs[i] + 1, Zidxs[i]] - fine_points[i, 0],
                    -(self.eqR[Ridxs[i], Zidxs[i]] - fine_points[i, 0]),
                ]
            )
            self.fine_point_per_cell_Z[Ridxs[i], Zidxs[i]].append(
                [
                    [
                        self.eqZ[Ridxs[i], Zidxs[i] + 1] - fine_points[i, 1],
                        -(self.eqZ[Ridxs[i], Zidxs[i]] - fine_points[i, 1]),
                    ]
                ]
            )
        for key in self.fine_point_per_cell.keys():
            self.fine_point_per_cell_R[key] = np.array(self.fine_point_per_cell_R[key])
            self.fine_point_per_cell_Z[key] = np.array(self.fine_point_per_cell_Z[key])
        self.fine_point = fine_points

    def interp_on_limiter_points_cell(self, id_R, id_Z, psi):
        """Calculates a bilinear interpolation of the flux function psi in the solver's grid
        cell [eq.R[id_R], eq.R[id_R + 1]] x [eq.Z[id_Z], eq.Z[id_Z + 1]]. The interpolation is returned directly for
        the refined points on the limiter boundary that fall in that grid cell, as assigned
        through the self.fine_point_per_cell objects.


        Parameters
        ----------
        id_R : int
            index of the R coordinate for the relevant grid cell
        id_Z : int
            index of the Z coordinate for the relevant grid cell
        psi : np.array on the solver's grid
            Vaules of the total flux function ofn the solver's grid.

        Returns
        -------
        vals : np.array
            Collection of floating point interpolated values of the flux function
            at the self.fine_point_per_cell[id_R, id_Z] locations.
        """
        if (id_R, id_Z) in self.fine_point_per_cell_Z.keys():
            ker = psi[id_R : id_R + 2, id_Z : id_Z + 2][np.newaxis, :, :]
            # ker *= self.ker_signs
            vals = np.sum(ker * self.fine_point_per_cell_Z[id_R, id_Z], axis=-1)
            vals = np.sum(vals * self.fine_point_per_cell_R[id_R, id_Z], axis=-1)
            vals /= self.dRdZ
            idxs = self.fine_point_per_cell[id_R, id_Z]
        else:
            vals = []
            idxs = []
        return vals, idxs

    def interp_on_limiter_points(self, id_R, id_Z, psi):
        """Uses interp_on_limiter_points_cell to interpolate the flux function psi
        on the refined limiter boundary points relevant to the 9 cells
        {id_R-1, id_R, id_R+1} X {id_Z-1, id_Z, id_Z+1}. Interpolated values on the
        boundary points relevant to the cells above are collated and returned.
        This is called by self.core_mask_limiter with id_R, id_Z corresponding to the
        grid cell outside the limiter (but in the diverted core) with the
        highest psi value (referred to as id_psi_max_out in self.core_mask_limiter)


        Parameters
        ----------
        id_R : int
            index of the R coordinate for the relevant grid cell
        id_Z : _type_
            index of the Z coordinate for the relevant grid cell
        psi : _type_
            Vaules of the total flux function ofn the solver's grid.

        Returns
        -------
        vals : np.array
            Collection of floating point interpolated values of the flux function
            at the self.fine_point_per_cell locations relevant to all of the 9 cells
            {id_R-1, id_R, id_R+1} X {id_Z-1, id_Z, id_Z+1}
        """
        vals = []
        idxs = []
        for i in np.arange(-1, 2):
            for j in np.arange(-1, 2):
                vals_, idxs_ = self.interp_on_limiter_points_cell(
                    id_R + i, id_Z + j, psi
                )
                vals = np.concatenate((vals, vals_))
                idxs = np.concatenate((idxs, idxs_))
        # vals = np.concatenate(vals)
        return vals, idxs

    def core_mask_limiter(
        self,
        psi,
        psi_bndry,
        core_mask,
        limiter_mask_out,
        #   limiter_mask_in,
        #   linear_coeff=.5
    ):
        """Checks if plasma is in a limiter configuration rather than a diverted configuration.
        This is obtained by checking whether the core mask deriving from the assumption of a diverted configuration
        implies an overlap with the limiter. If so, an interpolation of psi on the limiter boundary points
        is called to determine the value of psi_boundary and to recalculate the core_mask accordingly.

        Parameters
        ----------
        psi : np.array
            The flux function, including both plasma and metal components.
            np.shape(psi) = (eq.nx, eq.ny)
        psi_bndry : float
            The value of the flux function at the boundary.
            This is xpt[0][2] for a diverted configuration, where xpt is the output of critical.find_critical
        core_mask : np.array
            The mask identifying the plasma region under the assumption of a diverted configuration.
            This is the result of FreeGS4E's critical.core_mask
            Same size as psi.
        limiter_mask_out : np.array
            The mask identifying the border of the limiter, including points just inside it, the 'last' accessible to the plasma.
            Same size as psi.



        Returns
        -------
        psi_bndry : float
            The value of the flux function at the boundary.
        core_mask : np.array
            The core mask after correction
        flag_limiter : bool
            Flag to identify if the plasma is in a diverted or limiter configuration.

        """
        core_mask = core_mask.astype(float)
        # identify the grid points just left-below of points on the limiter that need checking
        offending_mask = (
            core_mask[:-1, :-1]
            + core_mask[1:, :-1]
            + core_mask[:-1, 1:]
            + core_mask[1:, 1:]
        )
        offending_mask = (offending_mask > 0) * (offending_mask < 4)
        self.offending_mask[:-1, :-1] = np.copy(offending_mask)
        self.offending_mask *= self.mask_limiter_cells
        # self.offending_mask = self.offending_mask.astype(bool)

        self.flag_limiter = False

        offending_cells_id_R = self.eqRidx[self.offending_mask]
        offending_cells_id_Z = self.eqZidx[self.offending_mask]

        self.interpolated_on_limiter = []
        for i in range(len(offending_cells_id_R)):
            vals_, idxs_ = self.interp_on_limiter_points_cell(
                offending_cells_id_R[i], offending_cells_id_Z[i], psi
            )
            self.interpolated_on_limiter.append(vals_)

        if len(self.interpolated_on_limiter):
            self.interpolated_on_limiter = np.concatenate(self.interpolated_on_limiter)
            psi_on_limiter = np.amax(self.interpolated_on_limiter)
            if psi_on_limiter > psi_bndry:
                self.flag_limiter = True
                psi_bndry = 1.0 * psi_on_limiter
                core_mask = (psi > psi_bndry) * core_mask

        # if np.any(offending_mask):
        #     # psi_max_out = np.amax(psi[offending_mask])
        #     # psi_max_in = np.amax(psi[(core_mask * limiter_mask_in).astype(bool)])
        #     # psi_bndry = linear_coeff*psi_max_out + (1-linear_coeff)*psi_max_in
        #     # core_mask = (psi > psi_bndry)*core_mask

        #     id_psi_max_out = np.unravel_index(
        #         np.argmax(psi - (10**6) * (1 - offending_mask)), (self.nx, self.ny)
        #     )
        #     self.interpolated_on_limiter, self.interpolated_idxs = self.interp_on_limiter_points(
        #         id_psi_max_out[0], id_psi_max_out[1], psi
        #     )
        #     psi_on_limiter = np.amax(self.interpolated_on_limiter)
        #     if psi_on_limiter > psi_bndry:
        #         self.flag_limiter = True
        #         psi_bndry = 1.0 * psi_on_limiter
        #         core_mask = (psi > psi_bndry) * core_mask

        return psi_bndry, core_mask, self.flag_limiter

    def Iy_from_jtor(self, jtor):
        """Generates 1d vector of plasma current values at the grid points of the reduced plasma domain.

        Parameters
        ----------
        jtor : np.ndarray
            Plasma current distribution on full domain. np.shape(jtor) = np.shape(eq.R)

        Returns
        -------
        Iy : np.ndarray
            Reduced 1d plasma current vector
        """
        Iy = jtor[self.mask_inside_limiter] * self.dRdZ
        return Iy

    def normalize_sum(self, Iy, epsilon=1e-6):
        """Normalises any vector by the linear sum of its elements.

        Parameters
        ----------
        jtor : np.ndarray
            Plasma current distribution on full domain. np.shape(jtor) = np.shape(eq.R)
        epsilon : float, optional
            avoid divergences, by default 1e-6

        Returns
        -------
        _type_
            _description_
        """
        hat_Iy = Iy / (np.sum(Iy) + epsilon)
        return hat_Iy

    def hat_Iy_from_jtor(self, jtor):
        """Generates 1d vector on reduced plasma domain for the normalised vector
        $$ Jtor*dR*dZ/I_p $$.


        Parameters
        ----------
        jtor : np.ndarray
            Plasma current distribution on full domain. np.shape(jtor) = np.shape(eq.R)
        epsilon : float, optional
            avoid divergences, by default 1e-6

        Returns
        -------
        hat_Iy : np.ndarray
            Reduced 1d plasma current vector, normalized to total plasma current

        """
        hat_Iy = jtor[self.mask_inside_limiter]
        hat_Iy = self.normalize_sum(hat_Iy)
        return hat_Iy

    def rebuild_map2d(self, reduced_vector, map_dummy, idxs_mask):
        """Rebuilds 2d map on full domain corresponding to 1d vector
        reduced_vector on smaller plasma domain

        Parameters
        ----------
        reduced_vector : np.ndarray
            1d vector on reduced plasma domain
        map_dummy : np.ndarray
            Specifies the size of the desired rectangular map
        idxs_mask : np.ndarray
            Specifies the location of the pixels of the reduced vector in the rectangular domain
            Note this is specific to map_dummy, e.g. use self.extract_index_mask

        Returns
        -------
        self.map2d : np.ndarray
            2d map on domain as map_dummy. Values on gridpoints outside the
            reduced plasma domain are set to zero.
        """

        map2d = np.zeros_like(map_dummy.astype(reduced_vector.dtype))
        map2d[idxs_mask[0], idxs_mask[1]] = reduced_vector
        return map2d
