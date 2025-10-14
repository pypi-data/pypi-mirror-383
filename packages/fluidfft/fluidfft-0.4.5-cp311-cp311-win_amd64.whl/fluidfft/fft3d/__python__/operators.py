import numpy as np


def vector_product(ax, ay, az, bx, by, bz):
    """Compute the vector product.

    Warning: the arrays bx, by, bz are overwritten.

    """
    n0, n1, n2 = ax.shape
    for i0 in range(n0):
        for i1 in range(n1):
            for i2 in range(n2):
                elem_ax = ax[i0, i1, i2]
                elem_ay = ay[i0, i1, i2]
                elem_az = az[i0, i1, i2]
                elem_bx = bx[i0, i1, i2]
                elem_by = by[i0, i1, i2]
                elem_bz = bz[i0, i1, i2]
                bx[i0, i1, i2] = elem_ay * elem_bz - elem_az * elem_by
                by[i0, i1, i2] = elem_az * elem_bx - elem_ax * elem_bz
                bz[i0, i1, i2] = elem_ax * elem_by - elem_ay * elem_bx
    return (bx, by, bz)


def loop_spectra3d(spectrum_k0k1k2, ks, K2):
    """Compute the 3d spectrum."""
    deltak = ks[1]
    nk = len(ks)
    spectrum3d = np.zeros(nk)
    nk0, nk1, nk2 = spectrum_k0k1k2.shape
    for ik0 in range(nk0):
        for ik1 in range(nk1):
            for ik2 in range(nk2):
                value = spectrum_k0k1k2[ik0, ik1, ik2]
                kappa = np.sqrt(K2[ik0, ik1, ik2])
                ik = int(kappa / deltak)
                if ik >= nk - 1:
                    ik = nk - 1
                    spectrum3d[ik] += value
                else:
                    coef_share = (kappa - ks[ik]) / deltak
                    spectrum3d[ik] += (1 - coef_share) * value
                    spectrum3d[ik + 1] += coef_share * value
    return spectrum3d


def loop_spectra_kzkh(spectrum_k0k1k2, khs, KH, kzs, KZ):
    """Compute the kz-kh spectrum."""
    deltakh = khs[1]
    deltakz = kzs[1]
    nkh = len(khs)
    nkz = len(kzs)
    spectrum_kzkh = np.zeros((nkz, nkh))
    nk0, nk1, nk2 = spectrum_k0k1k2.shape
    for ik0 in range(nk0):
        for ik1 in range(nk1):
            for ik2 in range(nk2):
                value = spectrum_k0k1k2[ik0, ik1, ik2]
                kappa = KH[ik0, ik1, ik2]
                ikh = int(kappa / deltakh)
                kz = abs(KZ[ik0, ik1, ik2])
                ikz = int(round(kz / deltakz))
                if ikz >= nkz - 1:
                    ikz = nkz - 1
                if ikh >= nkh - 1:
                    ikh = nkh - 1
                    spectrum_kzkh[ikz, ikh] += value
                else:
                    coef_share = (kappa - khs[ikh]) / deltakh
                    spectrum_kzkh[ikz, ikh] += (1 - coef_share) * value
                    spectrum_kzkh[ikz, ikh + 1] += coef_share * value
    return spectrum_kzkh


def __for_method__OperatorsPseudoSpectral3D__project_perpk3d_noloop(self_Kx, self_Ky, self_Kz, self_inv_K_square_nozero, vx_fft, vy_fft, vz_fft):
    """Project (inplace) a vector perpendicular to the wavevector.

        The resulting vector is divergence-free.

        """
    # function important for the performance of 3d fluidsim solvers
    tmp = (self_Kx * vx_fft + self_Ky * vy_fft +
           self_Kz * vz_fft)*self_inv_K_square_nozero
    vx_fft -= self_Kx * tmp
    vy_fft -= self_Ky * tmp
    vz_fft -= self_Kz * tmp


def __code_new_method__OperatorsPseudoSpectral3D__project_perpk3d_noloop(): return """

def new_method(self, vx_fft, vy_fft, vz_fft):
    return backend_func(self.Kx, self.Ky, self.Kz, self.inv_K_square_nozero, vx_fft, vy_fft, vz_fft)

"""


def __for_method__OperatorsPseudoSpectral3D__project_perpk3d(self_Kx, self_Ky, self_Kz, self_inv_K_square_nozero, vx_fft, vy_fft, vz_fft):
    """Project (inplace) a vector perpendicular to the wavevector.

        The resulting vector is divergence-free.

        """
    # function important for the performance of 3d fluidsim solvers
    # this version with loop is really faster than `project_perpk3d_noloop`
    n0, n1, n2 = vx_fft .shape
    for i0 in range(n0):
        for i1 in range(n1):
            for i2 in range(n2):
                tmp = (self_Kx[i0, i1, i2]*vx_fft[i0, i1, i2]+self_Ky[i0, i1, i2]*vy_fft[i0, i1,
                                                                                         i2]+self_Kz[i0, i1, i2]*vz_fft[i0, i1, i2])*self_inv_K_square_nozero[i0, i1, i2]
                vx_fft[i0, i1, i2] -= self_Kx[i0, i1, i2]*tmp
                vy_fft[i0, i1, i2] -= self_Ky[i0, i1, i2]*tmp
                vz_fft[i0, i1, i2] -= self_Kz[i0, i1, i2]*tmp


def __code_new_method__OperatorsPseudoSpectral3D__project_perpk3d(): return """

def new_method(self, vx_fft, vy_fft, vz_fft):
    return backend_func(self.Kx, self.Ky, self.Kz, self.inv_K_square_nozero, vx_fft, vy_fft, vz_fft)

"""


def __for_method__OperatorsPseudoSpectral3D__divfft_from_vecfft(self_Kx, self_Ky, self_Kz, vx_fft, vy_fft, vz_fft):
    """Return the divergence of a vector in spectral space."""
    return 1j * (self_Kx * vx_fft + self_Ky * vy_fft + self_Kz * vz_fft)


def __code_new_method__OperatorsPseudoSpectral3D__divfft_from_vecfft(): return """

def new_method(self, vx_fft, vy_fft, vz_fft):
    return backend_func(self.Kx, self.Ky, self.Kz, vx_fft, vy_fft, vz_fft)

"""


def __for_method__OperatorsPseudoSpectral3D__rotfft_from_vecfft(self_Kx, self_Ky, self_Kz, vx_fft, vy_fft, vz_fft):
    """Return the curl of a vector in spectral space."""
    return (1j * (self_Ky * vz_fft - self_Kz * vy_fft), 1j * (self_Kz * vx_fft - self_Kx * vz_fft), 1j * (self_Kx * vy_fft - self_Ky * vx_fft))


def __code_new_method__OperatorsPseudoSpectral3D__rotfft_from_vecfft(): return """

def new_method(self, vx_fft, vy_fft, vz_fft):
    return backend_func(self.Kx, self.Ky, self.Kz, vx_fft, vy_fft, vz_fft)

"""


def __for_method__OperatorsPseudoSpectral3D__rotfft_from_vecfft_outin(self_Kx, self_Ky, self_Kz, vx_fft, vy_fft, vz_fft, rotxfft, rotyfft, rotzfft):
    """Return the curl of a vector in spectral space."""
    # function important for the performance of 3d fluidsim solvers
    # cleaner but slightly slower
    # rotxfft[:] = 1j * (self.Ky * vz_fft - self.Kz * vy_fft)
    # rotyfft[:] = 1j * (self.Kz * vx_fft - self.Kx * vz_fft)
    # rotzfft[:] = 1j * (self.Kx * vy_fft - self.Ky * vx_fft)
    # seems faster (at least for small cases)
    n0, n1, n2 = vx_fft .shape
    for i0 in range(n0):
        for i1 in range(n1):
            for i2 in range(n2):
                rotxfft[i0, i1, i2] = 1j * (self_Ky[i0, i1, i2]*vz_fft[i0,
                                                                       i1, i2]-self_Kz[i0, i1, i2]*vy_fft[i0, i1, i2])
                rotyfft[i0, i1, i2] = 1j * (self_Kz[i0, i1, i2]*vx_fft[i0,
                                                                       i1, i2]-self_Kx[i0, i1, i2]*vz_fft[i0, i1, i2])
                rotzfft[i0, i1, i2] = 1j * (self_Kx[i0, i1, i2]*vy_fft[i0,
                                                                       i1, i2]-self_Ky[i0, i1, i2]*vx_fft[i0, i1, i2])


def __code_new_method__OperatorsPseudoSpectral3D__rotfft_from_vecfft_outin(): return """

def new_method(self, vx_fft, vy_fft, vz_fft, rotxfft, rotyfft, rotzfft):
    return backend_func(self.Kx, self.Ky, self.Kz, vx_fft, vy_fft, vz_fft, rotxfft, rotyfft, rotzfft)

"""


def __for_method__OperatorsPseudoSpectral3D__rotzfft_from_vxvyfft(self_Kx, self_Ky, vx_fft, vy_fft):
    """Compute the z component of the curl in spectral space."""
    return 1j * (self_Kx * vy_fft - self_Ky * vx_fft)


def __code_new_method__OperatorsPseudoSpectral3D__rotzfft_from_vxvyfft(): return """

def new_method(self, vx_fft, vy_fft):
    return backend_func(self.Kx, self.Ky, vx_fft, vy_fft)

"""


def __transonic__(): return "0.8.0"
