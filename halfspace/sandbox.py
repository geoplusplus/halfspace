from halfspace import load
import numpy as np

try:
    import gdal
except:
    pass


def coord_map_forward_1d(coord, x_step = 1, x_shift = 0, mode = 'linear'):
    """ Maps input coordinate (1D, value) to output coordinate given
        parameters step (m) and shift (b) for linear transformation

        y = m * x + b

        Intended to map meshgrid output arrays back to spatial coordinates.
    """

    x_in = coord

    x_step = float(x_step)

    if mode == 'linear':
        x_map = x_step * x_in + x_shift

    else: raise Exception('Nonlinear maps not yet supported')

    return x_map


def coord_map_inverse_1d(coord, x_step = 1, x_shift = 0, mode = 'linear'):

    """ Maps input coordinate (1D, value) to output coordinate given
        parameters step (m) and shift (b) for inverse linear transformation

        x = (y - b) / m

        Intended to map spatial coordinates to meshgrid output arrays.
    """
    x_in = coord

    x_step = float(x_step)

    if mode == 'linear':
        x_map = (x_in - x_shift) / x_step

    else: raise Exception('Nonlinear maps not yet supported')

    return x_map


def coord_map_inverse_2d(coord, x_step = 1, x_shift = 0, y_step = 1,
    y_shift = 0, mode = 'linear'):

    """ Maps input coordinates to output coordinates given
        parameters step (m) and shift (b) for inverse linear transformation

        x = (y - b) / m

        for each coordinate axis.

        Intended to map spatial coordinates to meshgrid output arrays.
    """
    x_in = coord[0]
    y_in = coord[1]

    # insure that steps are floats, so division works correctly
    x_step = float(x_step)
    y_step = float(y_step)

    if mode == 'linear':
        x_map = (x_in - x_shift) / x_step
        y_map = (y_in - y_shift) / y_step

    else: raise Exception('Nonlinear maps not yet supported')

    coord_map = [x_map, y_map]

    return coord_map


def coord_map_inverse_3d(coord, x_step = 1, x_shift = 0, y_step = 1,
    y_shift = 0, z_step = 1, z_shift = 0, mode = 'linear'):

    """ Maps input coordinates to output coordinates given
        parameters step (m) and shift (b) for inverse linear transformation

        x = (y - b) / m

        for each coordinate axis.

        Intended to map spatial coordinates to meshgrid output arrays.
    """

    x_in = coord[0]
    y_in = coord[1]
    z_in = coord[2]

    # insure that steps are floats, so division works correctly
    x_step = float(x_step)
    y_step = float(y_step)
    z_step = float(z_step)

    if mode == 'linear':
        x_map = (x_in - x_shift) / x_step
        y_map = (y_in - y_shift) / y_step
        z_map = (z_in - z_shift) / z_step

    else: raise Exception('Nonlinear maps not yet supported')

    coord_map = [x_map, y_map, z_map]

    return coord_map


def size_output(a1, a2, mode='full'):
    """ Calculates size of convolution output.  a1, a2 are arrays representing
        dimensions of the matrices being convolved.
    """
    size = a1 + a1 - 1
    if mode == 'full':
        ret_size = size
    elif mode == 'same':
        if np.product(a1, axis=0) > np.product(a2, axis=0):
            ret_size = a1
        else:
            ret_size = a2
    elif mode == 'valid':
        ret_size = abs(a2 - a1) + 1

    return ret_size


def strike_shear(strike=None, dip=None, rho=None, g=None, mxx=None, 
                 myy=None, mxy=None, mzz=None, myz=None, mxz=None,
                 txx=None, txy=None, tyy=None, depth=None):

    strike = np.radians(strike)
    dip = np.radians(dip)
                 
    tau_s = (-np.cos(dip)*(myz*np.cos(strike) + mxz*np.sin(strike)) 
             + np.cos(strike)*np.sin(dip)
             *((mxy + depth*g*txy*rho)*np.cos(strike) 
              + (mxx + depth*g*rho + depth*g*txx*rho)*np.sin(strike))
             -np.sin(dip)*np.sin(strike)
             *((myy + depth*g*rho +depth*g*tyy*rho)*np.cos(strike) 
              + (mxy + depth*g*txy*rho)*np.sin(strike)) )
    
    return tau_s


def dip_shear(strike=None, dip=None, rho=None, g=None, mxx=None, 
                 myy=None, mxy=None, mzz=None, myz=None, mxz=None,
                 txx=None, txy=None, tyy=None, depth=None):

    strike = np.radians(strike)
    dip = np.radians(dip)
    
    tau_d = (np.cos(strike) * np.sin(dip)
         * ((mxx + depth * g * rho + depth * g * txx * rho)
           * np.cos(dip) * np.cos(strike) 
           - (mxy + depth * g * txy * rho) * np.cos(dip) 
           * np.sin(strike) + mxz * (np.cos(strike)**2 * np.sin(dip) 
            + np.sin(dip)* np.sin(strike)**2)) 
 
         - np.sin(dip) * np.sin(strike) 
         * ((mxy + depth * g * txy * rho)
            * np.cos(dip) * np.cos(strike) 
            - (myy + depth * g * rho + depth * g * tyy * rho)
            * np.cos(dip) * np.sin(strike) + myz 
            * (np.cos(strike)**2 * np.sin(dip) + np.sin(dip) 
               * np.sin(strike)**2)) 
          -   np.cos(dip) * (mxz * np.cos(dip) * np.cos(strike) 
            - myz * np.cos(dip) * np.sin(strike) 
            + (mzz + depth * g * rho) * (np.cos(strike)**2 
                * np.sin(dip) + np.sin(dip) * np.sin(strike)**2)) )
    
    return tau_d


def eff_normal_stress(strike=None, dip=None, rho=None, g=None, mxx=None, 
                 myy=None, mxy=None, mzz=None, myz=None, mxz=None,
                 txx=None, txy=None, tyy=None, depth=None, phi=0):

    strike = np.radians(strike)
    dip = np.radians(dip)
    
    p = rho * g * depth 
    
    s_xx = mxx + p + p * txx
    s_yy = myy + p + p * tyy
    s_zz = mzz + p
           
    p_fluid = phi * (s_xx + s_yy + s_zz) / 3.
    
    s_xx += - p_fluid
    s_yy += - p_fluid
    s_zz += - p_fluid
    
    
    sigma_n = (-np.cos(dip) 
                 * (-s_zz * np.cos(dip) 
                    + mxz * np.cos(strike) * np.sin(dip) 
                    - myz * np.sin(dip) * np.sin(strike)) 
                 
                + np.cos(strike) * np.sin(dip) 
                 * (-mxz * np.cos(dip) + s_xx 
                    * np.cos(strike) * np.sin(dip) 
                    - (mxy + p * txy) * np.sin(dip) * np.sin(strike)) 
                 
                - np.sin(dip) * np.sin(strike) 
                * (-myz * np.cos(dip) + (mxy + p * txy) 
                   * np.cos(strike) * np.sin(dip) 
                   - s_yy * np.sin(dip) * np.sin(strike))
                )
    
    return sigma_n


def xx_stress_from_s1_s3_theta(s1=0, s3=0, theta=0):
    '''
    takes horizontal principle stress magnitudes and (unit circle) angle
    of s1 and returns xx stress component
    '''

    return (s1 * np.cos(theta)**2 + s3 * np.sin(theta)**2)


def yy_stress_from_s1_s3_theta(s1=0, s3=0, theta=0):
    '''
    takes horizontal principle stress magnitudes and (unit circle) angle
    of s1 and returns yy stress component
    '''

    return (s1 * np.sin(theta)**2 + s3 * np.cos(theta)**2)


def xy_stress_from_s1_s3_theta(s1=0, s3=0, theta=0):
    '''
    takes horizontal principle stress magnitudes and (unit circle) angle
    of s1 and returns xy stress component
    '''

    return (s1 - s3) * np.sin(theta) * np.cos(theta)


def angle_difference(angle1, angle2, return_abs = False):
    if np.isscalar(angle1) and np.isscalar(angle2):
        diff = angle_difference_scalar(angle1, angle2)
    else:
        diff = angle_difference_vector(angle1, angle2)

    return diff if return_abs == False else np.abs(diff)


def angle_difference_scalar(angle1, angle2):
    difference = angle2 - angle1
    while difference < -180:
        difference += 360
    while difference > 180:
        difference -= 360
    return difference


def angle_difference_vector(angle1_vec, angle2_vec):
    angle1_vec = np.array(angle1_vec)
    angle2_vec = np.array(angle2_vec)
    difference = angle2_vec - angle1_vec
    difference[difference < -180] += 360
    difference[difference > 180] -= 360
    
    return difference
