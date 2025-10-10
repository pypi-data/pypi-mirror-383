# Example Gum H1 - End-gauge calibration
# Michael Wollensack METAS - 12.02.2019 - 25.05.2023

print('Example Gum H1 - End-gauge calibration')
print('Begin')

from metas_unclib import *
use_linprop()

# Calibration of standard end gauge
l_s = ufloatfromdistribution(StudentTDistribution(50.000623e-3, 25e-9, 18.), desc='Calibration of standard end gauge')

# Measured difference between end gauges
# repeated observations
d1 = ufloatfromdistribution(StudentTDistribution(215e-9, 5.8e-9, 24.), desc='Measured difference between end gauges\trepeated observations')
# random effects of comparator
d2 = ufloatfromdistribution(StudentTDistribution(0, 3.9e-9, 5.), desc='Measured difference between end gauges\trandom effects of comparator')
# systematic effects of comparator
d3 = ufloatfromdistribution(StudentTDistribution(0, 6.7e-9, 8.), desc='Measured difference between end gauges\tsystematic effects of comparator')
d = d1 + d2 + d3
print('d       = %0.6e m' % get_value(d))
print('u(d)    = %0.6e m' % get_stdunc(d))
print('dof(d)  = %0.2f' % (1./get_idof(d)))

# Thermal expansion coefficient of standard end gauge (uniform)
alpha_s = ufloatfromdistribution(UniformDistribution(11.5e-6 - 2e-6, 11.5e-6 + 2e-6), desc='Thermal expansion coefficient of standard end gauge')

# Temperature of test bed
# mean temperature of bed
theta_1 = ufloatfromdistribution(NormalDistribution(-0.1, 0.2), desc='Temperature of test bed\tmean temperature of bed')
# cyclic variation of temperature of room (arcsine)
theta_2 = ufloatfromdistribution(ArcSineDistribution(-0.5, 0.5), desc='Temperature of test bed\tcyclic variation of temperature of room')
theta = theta_1 + theta_2

# Difference in expansion coefficients of end gauges (uniform)
delta_alpha = ufloatfromdistribution(StudentTDistribution(0, 1e-6/np.sqrt(3.), 50.), desc='Difference in expansion coefficients of end gauges')

# Difference in temperatures of end gauges (uniform)
delta_theta = ufloatfromdistribution(StudentTDistribution(0, 0.05/np.sqrt(3.), 2.), desc='Difference in temperatures of end gauges')

# Mathematical model 1
alpha = delta_alpha + alpha_s
theta_s = theta - delta_theta
l1 = (l_s * (1 + alpha_s * theta_s) + d) / (1 + alpha * theta)
print('Final result:')
print('l1      = %0.6e m' % get_value(l1))
print('u(l1)   = %0.6e m' % get_stdunc(l1))
print('dof(l1) = %0.2f' % (1./get_idof(l1)))

# Mathematical model 2
tmp1 = -l_s * delta_alpha * theta
tmp2 = -l_s * alpha_s * delta_theta
l2 = l_s + d + tmp1 + tmp2
print('Final result:')
print('l2      = %0.6e m' % get_value(l2))
print('u(l2)   = %0.6e m' % get_stdunc(l2))
print('dof(l2) = %0.2f' % (1./get_idof(l2)))

# Other
#print(get_correlation([l1, l2]))
#print(get_unc_component(l1, [l_s, d, alpha_s, theta, delta_alpha, delta_theta]))

print('End')
