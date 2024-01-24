import numpy as np
import scipy.signal as sig
import matplotlib.pyplot as plt

def bandpass_filter(samps, fcenter, fpass, srate, order=5):
    '''
    samps: The iq samples
    fcenter: The center frequency of your signal, which is shifted down to DC
    fpass: The bandwidth of your filter
    srate: The sample rate
    '''
    nyq = 0.5*srate
    shift_seq = np.exp(-2j * np.pi * fcenter / srate * np.arange(len(samps)))
    shift_samps = samps * shift_seq
    b, a = sig.butter(order, fpass/nyq, btype='low')
    fsamps =  sig.lfilter(b,a, shift_samps)
    return fsamps / shift_seq


data = np.load('/data/samples_20240123-163653/20240123-163654.832801-IQrate220000.000000_nsamples131072.npy')
data = data[0]

tx_separation = 27.5e3 + 13.75e3  # From Serhat's slides

transmitter_frequencies = [tx_separation*-2, tx_separation*-1, 0, tx_separation*1, tx_separation*2]
# print(transmitter_frequencies)

# EBC dense node was replaced with the USTAR rooftop node due to interference starting on Wed 28th
names = ['ebc', 'guesthouse', 'mario', 'moran', 'ustar']
sines = {}
filter_width = 7e3
shift_fudge = 5e3

for name, fcenter in zip(names, transmitter_frequencies):
    sines[name] = bandpass_filter(data, fcenter+shift_fudge, filter_width, 220e3, order=7)

## To compare the PSD (in other words, see the filtered signals)
## Decreasing Filter width will give you a cleaner signal, at risk of missing your actual signal if the fudge factor or center freq is off.
## Fudge factor may not be constant for all data?
for label in sines:
    sine = sines[label]
    plt.plot(np.fft.fftshift(np.fft.fftfreq(len(data), 1/220e3)), 10.0 * np.log10(abs(np.fft.fftshift(np.fft.fft(sine)))), label=label)
    plt.xlabel("Frequency + 3.5 GHz")
plt.legend()
plt.show()

##  To see the filtered sinusoids:
# for label in sines:
#     sine = sines[label]
#     plt.plot(abs(sine), label=label)
#     plt.xlabel("Time")
# plt.legend()
# plt.show()
