from gen_utils import generate_cherenkov_spectrum
import matplotlib.pyplot as plt
import numpy as np
sample = 100000
fig = plt.figure(figsize=plt.figaspect(0.5))

plt.subplots_adjust(hspace=0.4)
fig.suptitle('Validate Cherenkov spectrum generation', fontsize=14)
l_min = 300
l_max = 650
l = np.linspace(l_min,l_max,100)
y = 1.0/l**2/(1.0/l_min-1.0/l_max)
x = generate_cherenkov_spectrum(l_min,l_max,sample)
plt.hist(x,bins=300, density=True)
plt.plot(l,y)
plt.xlabel("$\lambda,$ nm")
plt.savefig('plots/test_cherenkov_spectrum_generation.pdf')
