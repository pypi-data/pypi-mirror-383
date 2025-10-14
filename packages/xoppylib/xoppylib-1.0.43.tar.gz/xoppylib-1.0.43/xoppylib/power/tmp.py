#
# import undulator radiation from file
#
import h5py

code = 'SRW'
hf = h5py.File(
    '/nobackup/gurb1/srio/OASYS1.2/modelling_team_scripts_and_workspaces/id18n/DATA/undulator_radiation_7.h5', 'r')
flux3D = hf["/XOPPY_RADIATION/Radiation/stack_data"][:]
energy = hf["/XOPPY_RADIATION/Radiation/axis0"][:]
horizontal = hf["/XOPPY_RADIATION/Radiation/axis1"][:]
vertical = hf["/XOPPY_RADIATION/Radiation/axis2"][:]
hf.close()

# example plot
if 0:
    from srxraylib.plot.gol import plot_image

    plot_image(flux3D[0], horizontal, vertical, title="Flux [photons/s] per 0.1 bw per mm2 at %9.3f eV" % (6000.0),
               xtitle="H [mm]", ytitle="V [mm]")
#
# end script
#


#
# script to make the calculations (created by XOPPY:power3Dcomponent)
#

import numpy
from xoppylib.power.power3d import calculate_component_absorbance_and_transmittance
from xoppylib.power.power3d import apply_transmittance_to_incident_beam

# compute local transmittance and absorbance
e0, h0, v0, f0 = energy, horizontal, vertical, flux3D
transmittance, absorbance, E, H, V, txt = calculate_component_absorbance_and_transmittance(
    e0,  # energy in eV
    h0,  # h in mm
    v0,  # v in mm
    substance='Be',
    thick=0.5,
    angle=6.98,
    defection=0,
    dens='?',
    roughness=0.0,
    flags=2,  # 0=Filter 1=Mirror 2=Aperture 3=magnifier, 4=Screen rotation  5=Thin object  6=Multilayer 7=External file
    hgap=1000.0,
    vgap=1000.0,
    hgapcenter=0.0,
    vgapcenter=0.0,
    hmag=1.0,
    vmag=1.0,
    hrot=0.0,
    vrot=0.0,
    thin_object_file='',
    thin_object_thickness_outside_file_area=0.0,
    thin_object_back_profile_flag=0,
    thin_object_back_profile_file='',
    multilayer_file='',
    external_reflectivity_file='',
)

# apply transmittance to incident beam
f_transmitted, e, h, v = apply_transmittance_to_incident_beam(transmittance, f0, e0, h0, v0,
                                                              flags=2,
                                                              hgap=1000.0,
                                                              vgap=1000.0,
                                                              hgapcenter=0.0,
                                                              vgapcenter=0.0,
                                                              hmag=1.0,
                                                              vmag=1.0,
                                                              interpolation_flag=0,
                                                              interpolation_factor_h=1.0,
                                                              interpolation_factor_v=1.0,
                                                              slit_crop=0,
                                                              )

f_absorbed = f0 * absorbance / (H[0] / h0[0]) / (V[0] / v0[0])

# data to pass
energy, horizontal, vertical, flux3D = e, h, v, f_transmitted

#
# example plots
#
if 0:
    from srxraylib.plot.gol import plot_image
    import scipy.constants as codata
    from xoppylib.power.power3d import integral_2d

    # transmitted/reflected beam

    spectral_power_transmitted = f_transmitted * codata.e * 1e3
    plot_image(spectral_power_transmitted[0, :, :], h, v,
               title="Transmitted Spectral Power Density [W/eV/mm2] at E=%g eV" % (3000.0), xtitle="H [mm]",
               ytitle="V [mm]", aspect='auto')

    power_density_transmitted = numpy.trapz(spectral_power_transmitted, e, axis=0)
    power_density_integral = integral_2d(power_density_transmitted, h, v)
    plot_image(power_density_transmitted, h, v,
               xtitle='H [mm] (normal to beam)',
               ytitle='V [mm] (normal to beam)',
               title='Power Density [W/mm^2]. Integral: %6.3f W' % power_density_integral, aspect='auto')

    # local absorption

    spectral_power_density_absorbed = f_absorbed * codata.e * 1e3

    plot_image(spectral_power_density_absorbed[0, :, :], H, V,
               title="Absorbed Spectral Power Density [W/eV/mm2] at E=%g eV" % (3000.0), xtitle="H [mm]",
               ytitle="V [mm]", aspect='auto')

    power_density_absorbed = numpy.trapz(spectral_power_density_absorbed, E, axis=0)
    power_density_integral = integral_2d(power_density_absorbed, H, V)
    plot_image(power_density_absorbed, H, V,
               xtitle='H [mm] (o.e. coordinates)',
               ytitle='V [mm] (o.e. coordinates)',
               title='Absorbed Power Density [W/mm^2]. Integral: %6.3f W' % power_density_integral, aspect='auto')

#
# end script
#


#
# script to make the calculations (created by XOPPY:power3Dcomponent)
#

import numpy
from xoppylib.power.power3d import calculate_component_absorbance_and_transmittance
from xoppylib.power.power3d import apply_transmittance_to_incident_beam

# compute local transmittance and absorbance
e0, h0, v0, f0 = energy, horizontal, vertical, flux3D
transmittance, absorbance, E, H, V, txt = calculate_component_absorbance_and_transmittance(
    e0,  # energy in eV
    h0,  # h in mm
    v0,  # v in mm
    substance='Be',
    thick=0.5,
    angle=6.98,
    defection=0,
    dens='?',
    roughness=0.0,
    flags=7,  # 0=Filter 1=Mirror 2=Aperture 3=magnifier, 4=Screen rotation  5=Thin object  6=Multilayer 7=External file
    hgap=1000.0,
    vgap=1000.0,
    hgapcenter=0.0,
    vgapcenter=0.0,
    hmag=1.0,
    vmag=1.0,
    hrot=0.0,
    vrot=89.6,
    thin_object_file='',
    thin_object_thickness_outside_file_area=0.0,
    thin_object_back_profile_flag=0,
    thin_object_back_profile_file='',
    multilayer_file='',
    external_reflectivity_file='/users/srio/Oasys/xoppy_reflectivity_140185913400848.dat',
)

# apply transmittance to incident beam
f_transmitted, e, h, v = apply_transmittance_to_incident_beam(transmittance, f0, e0, h0, v0,
                                                              flags=7,
                                                              hgap=1000.0,
                                                              vgap=1000.0,
                                                              hgapcenter=0.0,
                                                              vgapcenter=0.0,
                                                              hmag=1.0,
                                                              vmag=1.0,
                                                              interpolation_flag=0,
                                                              interpolation_factor_h=1.0,
                                                              interpolation_factor_v=1.0,
                                                              slit_crop=0,
                                                              )

f_absorbed = f0 * absorbance / (H[0] / h0[0]) / (V[0] / v0[0])

# data to pass
energy, horizontal, vertical, flux3D = e, h, v, f_transmitted

#
# example plots
#
if 1:
    from srxraylib.plot.gol import plot_image
    import scipy.constants as codata
    from xoppylib.power.power3d import integral_2d

    # transmitted/reflected beam

    spectral_power_transmitted = f_transmitted * codata.e * 1e3
    plot_image(spectral_power_transmitted[0, :, :], h, v,
               title="Transmitted Spectral Power Density [W/eV/mm2] at E=%g eV" % (3000.0), xtitle="H [mm]",
               ytitle="V [mm]", aspect='auto')

    power_density_transmitted = numpy.trapz(spectral_power_transmitted, e, axis=0)
    power_density_integral = integral_2d(power_density_transmitted, h, v)
    plot_image(power_density_transmitted, h, v,
               xtitle='H [mm] (normal to beam)',
               ytitle='V [mm] (normal to beam)',
               title='Power Density [W/mm^2]. Integral: %6.3f W' % power_density_integral, aspect='auto')

    # local absorption

    spectral_power_density_absorbed = f_absorbed * codata.e * 1e3

    plot_image(spectral_power_density_absorbed[0, :, :], H, V,
               title="Absorbed Spectral Power Density [W/eV/mm2] at E=%g eV" % (3000.0), xtitle="H [mm]",
               ytitle="V [mm]", aspect='auto')

    power_density_absorbed = numpy.trapz(spectral_power_density_absorbed, E, axis=0)
    power_density_integral = integral_2d(power_density_absorbed, H, V)
    plot_image(power_density_absorbed, H, V,
               xtitle='H [mm] (o.e. coordinates)',
               ytitle='V [mm] (o.e. coordinates)',
               title='Absorbed Power Density [W/mm^2]. Integral: %6.3f W' % power_density_integral, aspect='auto')

#
# end script
#
