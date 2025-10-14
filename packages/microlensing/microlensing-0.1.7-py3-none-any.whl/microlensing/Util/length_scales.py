import numpy as np
from astropy.cosmology import Planck18
from astropy import units as u
from astropy import constants


def theta_star_physical(z_lens: float, z_src: float, m: float = 1,
                        cosmo=Planck18):
    '''
    Calculate the size of the Einstein radius of a point mass lens in the
    lens and source planes, in meters

    :param z_lens: lens redshift
    :param z_src: source redshift
    :param m: point mass lens mass in solar mass units
    :param cosmo: an astropy.cosmology instance. default is Planck18

    :return theta_star_lens: theta_star in the lens plane in meters
    :return theta_star_src: theta_star in the source plane in meters
    '''
    microlens_mass = m * u.M_sun

    D_d = cosmo.angular_diameter_distance(z_lens)
    D_s = cosmo.angular_diameter_distance(z_src)
    D_ds = cosmo.angular_diameter_distance_z1z2(z_lens, z_src)

    theta_star_lens = np.sqrt(4 * constants.G * microlens_mass / constants.c**2
                              * D_d * D_ds / D_s)
    theta_star_src = theta_star_lens * D_s / D_d

    return theta_star_lens.to(u.m), theta_star_src.to(u.m)

def sn_expansion_rate(z_lens: float, z_src: float, m: float = 1,
                      cosmo=Planck18, v: float = 10**4):
    '''
    Calculate the expansion rate of a supernova in the source plane
    in units of the microlens Einstein radius / day

    :param z_lens: lens redshift
    :param z_src: source redshift
    :param m: point mass lens mass in solar mass units
    :param cosmo: an astropy.cosmology instance. default is Planck18
    :param v: supernova expansion velocity in kilometers / second. default is 10^4 km/s

    :return v / theta_star_src: supernova expansion velocity in units
                                of the microlens Einstein radius / day
    '''
    v = v * u.km / u.s
    return (v * u.day / theta_star_physical(z_lens, z_src, m, cosmo)[1]).to(u.dimensionless_unscaled)
