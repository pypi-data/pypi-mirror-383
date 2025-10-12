from seshat_classifier import seshat
import numpy as np
import matplotlib.pyplot as plt

# Specify filters to test
# filters = ['f090w', 'f200w', 'f356w', 'f480m', 'f770w', 'f1500w']
filters = ['f162m', 'f182m', 'f460m', 'f480m', 'f770w', 'f1500w','f2100w']
# filters = ['J','H','Ks','IRAC1', 'IRAC2', 'IRAC3', 'IRAC4','MIPS1']
# Specify classes to search for
classes = ['YSO', 'FS', 'Gal', 'BD', 'WD']

# Specify the limiting and saturating magnitudes of your observations
# limiting_mags = {'J':20, 'H':19, 'Ks':18, 'IRAC1':17, 'IRAC2':16, 'IRAC3':15, 'IRAC4':14,'MIPS1':13}
# saturating_mags = {'J':10, 'H':9, 'Ks':8, 'IRAC1':7, 'IRAC2':6, 'IRAC3':5, 'IRAC4':4,'MIPS1':3}
limiting_mags = {'f162m':28, 'f182m':27, 'f460m':26, 'f480m':25, 'f770w':24, 'f1500w':23,'f2100w':22}
saturating_mags = {'f162m':15, 'f182m':14, 'f460m':13, 'f480m':12, 'f770w':11, 'f1500w':10,'f2100w':9}

# Specify the expected distribution of errors
sig = 0.02
mean = 0.1
errs = [np.random.normal(mean, sig, size=100) for f in filters] # Choose a suitably large size to capture shape of distribution

# Get the performance
test_results = seshat.test_filters(filters = filters, classes=classes, limiting_mags = limiting_mags, saturating_mags = saturating_mags, errs=errs, threads = 8)

# Plot performance
ax = seshat.cm_custom(test_results.Class,test_results.Predicted_Class,cmap='Greys',display_labels=classes)
plt.tight_layout()
plt.savefig("tests/test_filters_cm_test.png")