import plotly.graph_objs as go
import numpy as np
import ipywidgets as ipw
from pynq.overlays.base import BaseOverlay
import xrfdc

class ComplexFrequencyPlot():

    def __init__(self,
                 configuration={}):

        default_config = {'sampling-freq' : 2048e6,
                          'number-samples' : 256,
                          'centre-freq' : 1024,
                          'height' : None,
                          'width' : None,
                          'data' : 0,
                          'title' : 'Complex Frequency Plot',
                          'x-axis-title' : 'Frequency (Hz)',
                          'y-axis-title' : 'Amplitude'}

        for default_key in default_config.keys():
            if default_key not in configuration:
                configuration[default_key] = default_config[default_key]

        self._config = configuration
        
        data = go.Scatter(
            x=np.arange(-self._config['sampling-freq']/2,
                        self._config['sampling-freq']/2,
                        self._config['sampling-freq']/self._config['number-samples']),
            #+ self._config['centre-freq']*1e6,
            y= self._config['data'])

        self._plot = go.FigureWidget(
            data=data,
            layout={'title' : self._config['title'],
                    'height': self._config['height'],
                    'width' : self._config['width'],
                    'xaxis' : {'title' : self._config['x-axis-title']},
                    'yaxis' : {'title' : self._config['y-axis-title']}})

    @property
    def configuration(self):
        return self._config

    @configuration.setter
    def configuration(self, configuration={}):
        for key in configuration.keys():
            if key not in self._config.keys():
                raise KeyError(''.join(['The key ', key, ' is not found in the class configuration.']))
            else:
                self._config.update({key : configuration[key]})
        self._update_plot()

    def _update_plot(self):
        self._plot.layout.height = self._config['height']
        self._plot.layout.width = self._config['width']
        self._plot.layout.xaxis.title = self._config['x-axis-title']
        self._plot.layout.yaxis.title = self._config['y-axis-title']
        self._plot.layout.title = self._config['title']
        self._plot.data[0].x = np.arange(-self._config['sampling-freq']/2,
                                         self._config['sampling-freq']/2,
                                         self._config['sampling-freq']/self._config['number-samples'])
        + self._config['centre-freq']

    def update_data(self, data):
        if len(data) != self._config['number-samples']:
            raise ValueError('Length of data must be the same as the plot.')
        else:
            self._plot.data[0].y = data

    def get_plot(self):
        return self._plot

class ComplexTimePlot():

    def __init__(self,
                 configuration={}):

        default_config = {'sampling-freq' : 4096e6,
                          'number-samples' : 256,
                          'height' : None,
                          'width' : None,
                          'c_data'  : 0,
                          'title' : 'Complex Time Plot',
                          'x-axis-title' : 'Time (s)',
                          'y-axis-title' : 'Amplitude'}

        for default_key in default_config.keys():
            if default_key not in configuration:
                configuration[default_key] = default_config[default_key]

        self._config = configuration

        data_re = go.Scatter(
            x=np.arange(0, self._config['number-samples']/self._config['sampling-freq'], 1/self._config['sampling-freq']),
            y=np.real(self._config['c_data']),
            name='Real')

        data_im = go.Scatter(
            x=np.arange(0, self._config['number-samples']/self._config['sampling-freq'], 1/self._config['sampling-freq']),
            y=np.imag(self._config['c_data']),
            name='Imag')

        self._plot = go.FigureWidget(
            data=[data_re, data_im],
            layout={'title' : self._config['title'],
                    'height': self._config['height'],
                    'width' : self._config['width'],
                    'xaxis' : {'title' : self._config['x-axis-title']},
                    'yaxis' : {'title' : self._config['y-axis-title']}})
        
    @property
    def configuration(self):
        return self._config

    @configuration.setter
    def configuration(self, configuration={}):
        for key in configuration.keys():
            if key not in self._config.keys():
                raise KeyError(''.join(['The key ', key, ' is not found in the class configuration.']))
            else:
                self._config.update({key : configuration[key]})
        self._update_plot()

    def _update_plot(self):
        self._plot.layout.height = self._config['height']
        self._plot.layout.width = self._config['width']
        self._plot.layout.xaxis.title = self._config['x-axis-title']
        self._plot.layout.yaxis.title = self._config['y-axis-title']
        self._plot.layout.title = self._config['title']
        self._plot.data[0].x = np.arange(0,
                                         self._config['number-samples']/self._config['sampling-freq'],
                                         1/self._config['sampling-freq'])

    def update_data(self, c_data):
        if len(c_data) != self._config['number-samples']:
            raise ValueError('Length of data must be the same as the plot.')
        self._plot.data[0].y = np.real(c_data)
        self._plot.data[1].y = np.imag(c_data)

    def get_plot(self):
        return self._plot
    
class DAC_ToneGenerator():

    def __init__(self,
                 channel,
                 centre_frequency=0):
        
        self._channel = channel
        #To do DAC block check
        self.centre_frequency = centre_frequency
        
    @property
    def centre_frequency(self):
        return abs(self._channel.dac_block.MixerSettings['Freq'])
    
    @centre_frequency.setter
    def centre_frequency(self, centre_frequency):
        block = self._channel.dac_block
        if (centre_frequency > block.BlockStatus['SamplingFreq']*1e3) \
            or (centre_frequency < 1):
            raise ValueError ('Centre frequency out of range')
        zone = block.NyquistZone
        even = True if ((zone % 2) == 0) else False
        req_zone = int(np.ceil(abs(centre_frequency)/((block.BlockStatus['SamplingFreq']*1e3)/2)))
        if req_zone != zone:
            block.NyquistZone = req_zone
        if even:
            block.MixerSettings['Freq'] = -centre_frequency
        else:
            block.MixerSettings['Freq'] = centre_frequency
            
            
class ADC_ToneGenerator():

    def __init__(self,
                 channel,
                 adc_centre_frequency=0):
        
        self._channel = channel
        #To do ADC block check
        self.centre_frequency = adc_centre_frequency
        
    @property
    def adc_centre_frequency(self):
        return abs(self._channel.adc_block.MixerSettings['Freq'])
    
    @adc_centre_frequency.setter
    def adc_centre_frequency(self, adc_centre_frequency):
        block = self._channel.adc_block
        #if (adc_centre_frequency == 0):
            #adc_centre_frequency = 1
        if (adc_centre_frequency < -block.BlockStatus['SamplingFreq']*1e3) \
            or (adc_centre_frequency > block.BlockStatus['SamplingFreq']*1e3):
            raise ValueError ('ADC Centre frequency out of range')
        if (adc_centre_frequency == 0): 
            zone = 1
            even = True if ((zone % 2) == 0) else False
        else:
            zone = block.NyquistZone
            req_zone = int(np.ceil(abs(adc_centre_frequency)/((block.BlockStatus['SamplingFreq']*1e3)/2)))
            if req_zone != zone:
                block.NyquistZone = req_zone
        even = True if ((zone % 2) == 0) else False       
        if even:
            block.MixerSettings['Freq'] = adc_centre_frequency
        else:
            block.MixerSettings['Freq'] = -adc_centre_frequency
        block.UpdateEvent(1)


class FrequencyProcessor():

    def __init__(self,
                 configuration={}):

        default_config = {'sampling-freq' : 2048e6,
                          'window' : 'blackman'}

        for default_key in default_config.keys():
            if default_key not in configuration:
                configuration[default_key] = default_config[default_key]

        self._config = configuration

    def _window(self, data):
        return data * getattr(np, self._config['window'])(len(data))

    def _fft(self, data):
        return np.fft.fftshift(np.fft.fft(data))

    def _psd(self, data):
        return (abs(data)**2)/(self._config['sampling-freq']*np.sum(getattr(np, self._config['window'])(len(data))**2))

    def _decibel(self, data):
        return 10*np.where(data > 0, np.log10(data), 0)

    def convert_to_freq(self, data):
        data = self._window(data)
        data = self._fft(data)
        data = self._psd(data)
        return self._decibel(data)
    

class CoarseMixerApplication():

    def __init__(self,
                 tx_channel,
                 rx_channel,
                 sample_frequency=4096e6,
                 number_samples=2048,
                 centre_frequency=1024,
                 window='blackman',
                 height=None,
                 width=None):
        
        tx_channel.dac_block.MixerSettings.update({
                'MixerType': xrfdc.MIXER_TYPE_FINE,
                'FineMixerScale': xrfdc.MIXER_SCALE_0P7,
                'Freq': 1024,
            })
        rx_channel.adc_block.MixerSettings.update({
                'CoarseMixFreq' : xrfdc.COARSE_MIX_SAMPLE_FREQ_BY_FOUR,
                'MixerType': xrfdc.MIXER_TYPE_COARSE,
            })
        
        tx_channel.control.gain = 0.5
        tx_channel.control.enable = True
        
        def set_CoarseMixFreq(widget):
            desired_CoarseMixFreq = widget['new']
            rx_channel.adc_block.MixerSettings.update({
                'CoarseMixFreq' : desired_CoarseMixFreq,
                'MixerType': xrfdc.MIXER_TYPE_COARSE,
            })
            c_data = rx_channel.transfer(packetsize = number_samples)
            self.time_plot.update_data(c_data)
            freq = self.frequency_processor.convert_to_freq(c_data)
            self.frequency_plot.update_data(freq)
            
        def set_desired_freq(widget):
            centre_frequency = widget['new']
            self.dac_tone_generator.centre_frequency = centre_frequency
            c_data = rx_channel.transfer(packetsize = number_samples)
            self.time_plot.update_data(c_data)
            freq = self.frequency_processor.convert_to_freq(c_data)
            self.frequency_plot.update_data(freq)

        self.dac_tone_generator = DAC_ToneGenerator(tx_channel, centre_frequency)

        self.frequency_processor = FrequencyProcessor(configuration={
            'sampling-freq'  : sample_frequency/2,
            'window'         : window})
        
        c_data = rx_channel.transfer(packetsize=number_samples)
        freq = self.frequency_processor.convert_to_freq(c_data)

        self.time_plot = ComplexTimePlot({
            'sampling-freq'  : sample_frequency,
            'number-samples' : number_samples,
            'height'         : height,
            'width'          : width,
            'c_data'         : c_data,
            'title'          : 'Receiver: Complex Time Plot',
            'x-axis-title'   : 'Time (s)',
            'y-axis-title'   : 'Amplitude'})

        self.frequency_plot = ComplexFrequencyPlot({
            'sampling-freq'  : sample_frequency/2,
            'number-samples' : number_samples,
            'centre-freq'    : centre_frequency,
            'height'         : height,
            'width'          : width,
            'data'           : freq,
            'title'          : 'Receiver: Complex Frequency Plot',
            'x-axis-title'   : 'Frequency (Hz)',
            'y-axis-title'   : 'Power Spectral Density (dB)'})

        self.desired_freq_slider = ipw.FloatSlider(
            value=(centre_frequency),
            min=1,
            max=(sample_frequency/2)*1e-6,
            step=1,
            description='Transmitter Frequency:',
            disabled=False,
            continuous_update=True,
            orientation='horizontal',
            readout=True,
            style = {'description_width': 'initial'})
        
        self.desired_coarse_mix_freq_dropdown = ipw.Dropdown(
            options=[('fs/2', xrfdc.COARSE_MIX_SAMPLE_FREQ_BY_TWO), 
                     ('fs/4', xrfdc.COARSE_MIX_SAMPLE_FREQ_BY_FOUR), 
                     ('-fs/4', xrfdc.COARSE_MIX_MIN_SAMPLE_FREQ_BY_FOUR)],
            value=xrfdc.COARSE_MIX_SAMPLE_FREQ_BY_FOUR,
            description='Mix Freq:',
            disabled=False,
            continuous_update=False,
            readout=True,
            )

        self.desired_freq_slider.observe(set_desired_freq, 'value')
        self.desired_coarse_mix_freq_dropdown.observe(set_CoarseMixFreq, 'value')

    def display(self):
        return ipw.VBox([self.time_plot.get_plot(),
                         self.frequency_plot.get_plot(),
                         self.desired_freq_slider, self.desired_coarse_mix_freq_dropdown])
    
    
class FineMixerApplication():

    def __init__(self,
                 tx_channel,
                 rx_channel,
                 sample_frequency=4096e6,
                 number_samples=2048,
                 centre_frequency=1024,
                 adc_centre_frequency = 1024,
                 window='blackman',
                 height=None,
                 width=None):
        
        tx_channel.dac_block.MixerSettings.update({
                'MixerType': xrfdc.MIXER_TYPE_FINE,
                'FineMixerScale': xrfdc.MIXER_SCALE_0P7,
                'Freq': 1024,
            })
        
        rx_channel.adc_block.MixerSettings.update({
                'MixerType': xrfdc.MIXER_TYPE_FINE,
                'FineMixerScale': xrfdc.MIXER_SCALE_1P0,
                'Freq': -1024
            })
        
        tx_channel.control.gain = 0.5
        tx_channel.control.enable = True
            
        def set_desired_freq(widget):
            centre_frequency = widget['new']
            self.dac_tone_generator.centre_frequency = centre_frequency
            c_data = rx_channel.transfer(packetsize = number_samples)
            self.time_plot.update_data(c_data)
            freq = self.frequency_processor.convert_to_freq(c_data)
            self.frequency_plot.update_data(freq)
            
        def set_adc_desired_freq(widget):
            adc_centre_frequency = widget['new']
            self.adc_tone_generator.adc_centre_frequency = adc_centre_frequency
            c_data = rx_channel.transfer(packetsize = number_samples)
            self.time_plot.update_data(c_data)
            freq = self.frequency_processor.convert_to_freq(c_data)
            self.frequency_plot.update_data(freq)

        self.dac_tone_generator = DAC_ToneGenerator(tx_channel, centre_frequency)
        
        self.adc_tone_generator = ADC_ToneGenerator(rx_channel, centre_frequency)

        self.frequency_processor = FrequencyProcessor(configuration={
            'sampling-freq'  : sample_frequency/2,
            'window'         : window})
        
        c_data = rx_channel.transfer(packetsize=number_samples)
        freq = self.frequency_processor.convert_to_freq(c_data)

        self.time_plot = ComplexTimePlot({
            'sampling-freq'  : sample_frequency,
            'number-samples' : number_samples,
            'height'         : height,
            'width'          : width,
            'c_data'         : c_data,
            'title'          : 'Receiver: Complex Time Plot',
            'x-axis-title'   : 'Time (s)',
            'y-axis-title'   : 'Amplitude'})

        self.frequency_plot = ComplexFrequencyPlot({
            'sampling-freq'  : sample_frequency/2,
            'number-samples' : number_samples,
            'centre-freq'    : centre_frequency,
            'height'         : height,
            'width'          : width,
            'data'           : freq,
            'title'          : 'Receiver: Complex Frequency Plot',
            'x-axis-title'   : 'Frequency (Hz)',
            'y-axis-title'   : 'Power Spectral Density (dB)'})

        self.desired_freq_slider = ipw.FloatSlider(
            value=(centre_frequency),
            min=1,
            max=(sample_frequency/2)*1e-6,
            step=1,
            description='Transmitter Frequency:',
            disabled=False,
            continuous_update=True,
            orientation='horizontal',
            readout=True,
            style = {'description_width': 'initial'})
        
        self.desired_adc_freq_slider = ipw.FloatSlider(
            value=(adc_centre_frequency),
            min=-(sample_frequency/2)*1e-6,
            max=(sample_frequency/2)*1e-6,
            step=1,
            description='Receiver Frequency:',
            disabled=False,
            continuous_update=True,
            orientation='horizontal',
            readout=True,
            style = {'description_width': 'initial'})

        self.desired_freq_slider.observe(set_desired_freq, 'value')
        self.desired_adc_freq_slider.observe(set_adc_desired_freq, 'value')

    def display(self):
        return ipw.VBox([self.time_plot.get_plot(),
                         self.frequency_plot.get_plot(),
                         self.desired_freq_slider, self.desired_adc_freq_slider])
    
    

