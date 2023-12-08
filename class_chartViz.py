"""
Created by:      Bryce Chung
Last modified:   January 4, 2016
Translated in Python 3.8 Jan 2023 (D. Cattaert)
"""

import matplotlib.pyplot as plt


plt.ion()

global verbose
verbose = 3

class chartViz(object):
    """
    This class is used to visualize chartData objects.
    """
    
    def __init__(self):
        self.data = {}
        self.fig = None
        self.axes = {}
        self.arrange = None
        self.chartFormat = None
        self.title = ''
        self.titleFormat = {}
        
        
    def add_data(self, name, objChartData):
        if objChartData not in self.data:
            self.data[name] = objChartData.data
            
    
    def set_arrange(self, arrange):
        self.arrange = arrange    
        
    def set_format(self, chartFormat):
        self.chartFormat = chartFormat
        
    def set_title(self, title, titleFormat = {}):
        self.title = title
        self.titleFormat = titleFormat
    
    
    def make_chart(self, hide=['Time']):
        self.fig = plt.figure(figsize=(24,18))
        self.fig.suptitle(self.title, **self.titleFormat)
                
        axShare = None        
        
        if self.arrange is None:
            axLen = 1
            for dAxis in self.data:
                axLen += len(np.where(np.array(list(self.data[dAxis].keys())) != 'Time')[0])           
                
            i=1        
            for dAxis in self.data:
                print("\n")
                for d in list(dAxis.keys()):
                    if d in hide:
                        continue
                    
                    if verbose > 1:
                        print("Charting: %s" % d)
                        print("Shared:")
                        print(axShare)
                        
                    if len(self.axes) > 0:
                        ax = self.fig.add_subplot(axLen, 1, i, sharex=axShare)
                    else:
                        ax = self.fig.add_subplot(axLen, 1, i)
                        axShare = ax
                        
                    if dAxis[d].datatype == 'analog':
                        ax.plot(dAxis['Time'].data, dAxis[d].data, 'b-')
                    elif dAxis[d].datatype == 'spike':
                        for spike in dAxis[d].data:
                            ax.axvline(spike, color='g')
                            ax.yaxis.set_ticklabels([])
                        
                    if i < axLen:
                        ax.xaxis.set_ticklabels([])
                        
                    self.axes[d] = ax
                        
                    i += 1
        else:
            for ix, axis in enumerate(self.arrange):                
                print("\n")
                if len(self.axes) > 0:
                    ax = self.fig.add_subplot(len(self.arrange), 1, ix+1, sharex=axShare)
                    print("Sharing axis: %s" % str(axShare))
                else:
                    ax = self.fig.add_subplot(len(self.arrange), 1, ix+1)
                    print("No shared axis")
                    axShare = ax
                    
                for ix, chart in enumerate(self.arrange[axis]['charts']):
                    if chart.split('.')[1:] in hide:
                        continue

                    if verbose > 1:
                        print("Charting: %s" % chart)
                        #print "Shared:"
                        #print axShare                    
                    
                    color = 'k'                                        
                    kwargs = {}
                    
                    if chart in list(self.chartFormat.keys()):
                        formatting = self.chartFormat[chart]
                        if 'color' in list(formatting.keys()):
                            kwargs['color'] = self.chartFormat[chart]['color']
                    
                    if verbose > 1:
                        print("Charting: %s" % chart)
                        print(kwargs)
                    
                    strDataObj = chart.split('.')[0]
                    strChart = ''.join(chart.split('.')[1:])
                    data = self.data[strDataObj]
                    
                    if data[strChart]['datatype'] == 'analog':
                        ax.plot(data['Time']['data'], data[strChart]['data'], **kwargs)
                    elif data[strChart]['datatype'] == 'spike':
                        if len(self.arrange[axis]['charts']) > 1:
                            height = 1./len(self.arrange[axis]['charts'])
                        else:
                            height = 1
                        
                        for spike in data[strChart]['data']:
                            ax.axvline(spike, ymin=ix*height, ymax=(ix+1)*height-height*0.1, **kwargs)
                            ax.yaxis.set_ticklabels([])
                            
                ax.set_ylabel(self.arrange[axis]['name'])
                            
                if ix+1 < len(self.arrange):
                    ax.xaxis.set_ticklabels([])
                    
                self.axes[axis] = ax
