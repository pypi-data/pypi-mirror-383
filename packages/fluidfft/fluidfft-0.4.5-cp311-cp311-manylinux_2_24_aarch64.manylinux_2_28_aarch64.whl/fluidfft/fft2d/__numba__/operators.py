
from numba import njit


@njit(cache=True, fastmath=True)
def __for_method__OperatorsPseudoSpectral2D__rotfft_from_vecfft(self_KX, self_KY, vecx_fft, vecy_fft):
    """Return the rotational of a vector in spectral space."""
    return 1j * (self_KX * vecy_fft - self_KY * vecx_fft)


def __code_new_method__OperatorsPseudoSpectral2D__rotfft_from_vecfft():
    return '\n\ndef new_method(self, vecx_fft, vecy_fft):\n    return backend_func(self.KX, self.KY, vecx_fft, vecy_fft)\n\n'


@njit(cache=True, fastmath=True)
def __for_method__OperatorsPseudoSpectral2D__divfft_from_vecfft(self_KX, self_KY, vecx_fft, vecy_fft):
    """Return the divergence of a vector in spectral space."""
    return 1j * (self_KX * vecx_fft + self_KY * vecy_fft)


def __code_new_method__OperatorsPseudoSpectral2D__divfft_from_vecfft():
    return '\n\ndef new_method(self, vecx_fft, vecy_fft):\n    return backend_func(self.KX, self.KY, vecx_fft, vecy_fft)\n\n'


@njit(cache=True, fastmath=True)
def __for_method__OperatorsPseudoSpectral2D__vecfft_from_rotfft(self_KX_over_K2, self_KY_over_K2, rot_fft):
    """Return the velocity in spectral space computed from the
        rotational."""
    ux_fft = 1j * self_KY_over_K2 * rot_fft
    uy_fft = -1j * self_KX_over_K2 * rot_fft
    return (ux_fft, uy_fft)


def __code_new_method__OperatorsPseudoSpectral2D__vecfft_from_rotfft():
    return '\n\ndef new_method(self, rot_fft):\n    return backend_func(self.KX_over_K2, self.KY_over_K2, rot_fft)\n\n'


@njit(cache=True, fastmath=True)
def __for_method__OperatorsPseudoSpectral2D__vecfft_from_divfft(self_KX_over_K2, self_KY_over_K2, div_fft):
    """Return the velocity in spectral space computed from the
        divergence."""
    ux_fft = -1j * self_KX_over_K2 * div_fft
    uy_fft = -1j * self_KY_over_K2 * div_fft
    return (ux_fft, uy_fft)


def __code_new_method__OperatorsPseudoSpectral2D__vecfft_from_divfft():
    return '\n\ndef new_method(self, div_fft):\n    return backend_func(self.KX_over_K2, self.KY_over_K2, div_fft)\n\n'


@njit(cache=True, fastmath=True)
def __for_method__OperatorsPseudoSpectral2D__gradfft_from_fft(self_KX, self_KY, f_fft):
    """Return the gradient of f_fft in spectral space."""
    px_f_fft = 1j * self_KX * f_fft
    py_f_fft = 1j * self_KY * f_fft
    return (px_f_fft, py_f_fft)


def __code_new_method__OperatorsPseudoSpectral2D__gradfft_from_fft():
    return '\n\ndef new_method(self, f_fft):\n    return backend_func(self.KX, self.KY, f_fft)\n\n'


@njit(cache=True, fastmath=True)
def __for_method__OperatorsPseudoSpectral2D__dealiasing_variable(self__has_to_dealiase, self_nK0_loc, self_nK1_loc, self_where_dealiased, f_fft):
    """Dealiasing a variable."""
    if self__has_to_dealiase:
        for iK0 in range(self_nK0_loc):
            for iK1 in range(self_nK1_loc):
                if self_where_dealiased[iK0, iK1]:
                    f_fft[iK0, iK1] = 0.0


def __code_new_method__OperatorsPseudoSpectral2D__dealiasing_variable():
    return '\n\ndef new_method(self, f_fft):\n    return backend_func(self._has_to_dealiase, self.nK0_loc, self.nK1_loc, self.where_dealiased, f_fft)\n\n'


def __transonic__():
    return '0.8.0'
