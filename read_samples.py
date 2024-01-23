import numpy as np
import scipy.signal as sig
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import os

def bandpass_filter(samps, fcenter, fpass, srate, order=5):
    '''
    samps: The iq samples
    fcenter: The center frequency of your signal, which is shifted down to DC
    fpass: The bandwidth of your filter
    srate: The sample rate
    '''
    nyq = 0.5*srate
    shift_seq = np.exp(-2j * np.pi * fcenter / srate * np.arange(len(samps)))  # multiple e^(-j*2*pi*fc*Ts*n) in time = frequency shift
    shift_samps = samps * shift_seq
    b, a = sig.butter(N=order, Wn=fpass/nyq, btype='low')
    fsamps = sig.lfilter(b, a, shift_samps)
    return fsamps / shift_seq


# folders = ['data/stat_rot_29jun_serhat/'+name for name in os.listdir('data/stat_rot_29jun_serhat/') if name.startswith('samples_20')]
# folders = ['data/xin_yanyu_serhat_walking_28jun/'+name for name in os.listdir('data/xin_yanyu_serhat_walking_28jun/') if name.startswith('samples_20')]
folders = ['data/xin_yanyu_serhat_driving_28jun/'+name for name in os.listdir('data/xin_yanyu_serhat_driving_28jun/') if name.startswith('samples_20')]

# gps_files = [name for name in os.listdir('gps_data/stat_rot_29jun_serhat/dummy/') if name.endswith('.txt')]
gps_files = [name for name in os.listdir('gps_data/xin_yanyu_serhat_driving_28jun/') if name.endswith('.txt')]
gps_datas = []
for gps_file in gps_files:
    # gps_datas.append(pd.read_csv(os.path.join('gps_data/stat_rot_29jun_serhat/dummy/', gps_file)))
    gps_datas.append(pd.read_csv(os.path.join('gps_data/xin_yanyu_serhat_driving_28jun/', gps_file)))
gps_data = pd.concat(gps_datas, axis=0)

gps_times = np.array(pd.to_datetime(gps_data['date time']) - np.timedelta64(6, 'h'), dtype='datetime64[s]')
latitude = np.array(gps_data['latitude'])
longitude = np.array(gps_data['longitude'])

coords = {gps_times[i]: np.array([longitude[i], latitude[i]]) for i in range(len(gps_times))}

tx_separation = 27.5e3 + 13.75e3  # From Serhat's slides

transmitter_frequencies = [tx_separation*-2, tx_separation*-1, 0, tx_separation*1, tx_separation*2]
# EBC dense node was replaced with the USTAR rooftop node due to interference starting on Wed 28th
names = ['ebc', 'guesthouse', 'mario', 'moran', 'wasatch']
filter_width = 7e3
shift_fudge = 5e3

target_name = 'wasatch'

data = {}
for folder in folders:
    for file in os.listdir(folder):
        time = pd.to_datetime(file.split('-IQ')[0].split('.')[0])
        time = np.datetime64(time).astype('datetime64[s]')
        data[time] = np.load(os.path.join(folder, file))[0]
        sines = {}
        for name, fcenter in zip(names, transmitter_frequencies):
            sines[name] = bandpass_filter(data[time], fcenter + shift_fudge, filter_width, 220e3, order=7)
        data[time] = sines[target_name]
times = sorted(list(data.keys()))
print(data, '\n')
# print(times)
# fig, axs = plt.subplots(1, 2)
#
# def animate(i):
#     print(times[i], "%i/%i" % (i, len(times)), end='\r')
#     axs[0].clear()
#     axs[0].plot(3.534e9 + np.fft.fftshift(np.fft.fftfreq(len(data[times[i]]), 1/0.22e6)), 10.0 * np.log10(abs(np.fft.fftshift(np.fft.fft(data[times[i]])))))
#     axs[0].set_ylim(-20, 40)
#
#     axs[1].clear()
#     axs[1].scatter(longitude, latitude, marker='.', )
#     if times[i] in coords:
#         axs[1].scatter(*coords[times[i]], marker='*', s=100)
#
#
# ani = FuncAnimation(fig, animate, frames=len(times), interval=1, repeat=True)
# plt.show()
