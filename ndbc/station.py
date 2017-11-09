"""
station.py
"""
from datetime import datetime, timedelta
import gzip
import numpy as np
import requests
import urllib

_BASEURL = 'http://www.ndbc.noaa.gov/data'
_SENSOR_URL = _BASEURL+'/stations/buoyht.txt'
_REALTIME_URL = _BASEURL+'/realtime2/'
_RECENT_URL = _BASEURL+'/stdmet/'
_HISTORICAL_URL = _BASEURL+'/historical/stdmet/'
_STATION_URL = _BASEURL+'/stations/station_table.txt'

class Station(object):
    """NDBC Station class."""
    def __init__(self, station_id, starttime=None, endtime=None):
        self.id = str(station_id)
        self.time = []; self.wspd = []; self.wdir = []; self.gst  = []
        self.wvht = []; self.dpd  = []; self.apd  = []; self.mwd  = []
        self.pres = []; self.atmp = []; self.wtmp = []; self.dewp = []
        self.vis  = []; self.ptdy = []; self.tide = []
        self._get_info()
        if starttime and endtime:
            self.get_stdmet(starttime, endtime)

    def _get_info(self):
        """Collects station metadata."""
        r = requests.get(_STATION_URL)
        if not r.status_code == 200:
            raise RuntimeError('Received response status '
                +str(r.status_code)+' from '+_STATION_URL)
        lines = r.text.split('\n')
        try:
            data = [line for line in lines if self.id == line[:5]].pop()
        except IndexError:
            raise ValueError('Station '+self.id+' not found in '+_STATION_URL)
        station_id, self.owner, self.ttype, self.hull, self.name, self.payload,\
            self.location, self.timezone, self.forecast, self.note = data.split('|')
        loc = self.location.split()
        self.lat, self.lon = float(loc[0]), float(loc[2])
        if loc[1] == 'S':
            self.lat = -self.lat
        if loc[3] == 'W':
            self.lon = -self.lon

    def get_stdmet(self, starttime, endtime):
        """Gets the standard meteorological data given start and end times."""
        # re-initialize if we are to overwrite data
        if self.time:
            self.__init__(self.id)

        if starttime.year < datetime.utcnow().year:
            datatype = 'historical'
        elif starttime > datetime.utcnow() - timedelta(days=45):
            self._get_stdmet_realtime()
            return
        elif starttime.year == datetime.utcnow().year:
            datatype = 'recent'
        else:
            raise ValueError('starttime cannot be in the future')

        time = starttime
        while True:

            if datatype == 'historical':
                filename = self.id+'h'+str(time.year)+'.txt.gz'
                fileurl = _HISTORICAL_URL+filename

            elif datatype == 'recent':
                filename = self.id+str(time.month)+str(time.year)+'.txt.gz'
                fileurl = _RECENT_URL+time.strftime('%b')+'/'+filename

            f = gzip.open(urllib.request.urlopen(fileurl))

            if time.year >= 2007:
                datastart = 2
            else:
                datastart = 1

            lines = [line.decode().strip() for line in f.readlines()]

            for line in lines[datastart:]:
                line = line.split()
                try:
                    self.time.append(datetime.strptime(''.join(line[:5]), '%Y%m%d%H%M'))
                    nn = 5
                except ValueError:
                    self.time.append(datetime.strptime(''.join(line[:4]), '%Y%m%d%H'))
                    nn = 4
                self.wdir.append(np.nan if line[nn] == '999' else float(line[nn]))
                self.wspd.append(np.nan if line[nn+1] == '99.0' else float(line[nn+1]))
                self.gst.append(np.nan if line[nn+2] == '99.0' else float(line[nn+2]))
                self.wvht.append(np.nan if line[nn+3] == '99.0' else float(line[nn+3]))
                self.dpd.append(np.nan if line[nn+4] == '99.0' else float(line[nn+4]))
                self.apd.append(np.nan if line[nn+5] == '99.0' else float(line[nn+5]))
                self.mwd.append(np.nan if line[nn+6] == '999' else float(line[nn+6]))
                self.pres.append(np.nan if line[nn+7] == '9999.0' else float(line[nn+7]))
                self.atmp.append(np.nan if line[nn+8] == '99.0' else float(line[nn+8]))
                self.wtmp.append(np.nan if line[nn+9] == '99.0' else float(line[nn+9]))
                self.dewp.append(np.nan if line[nn+10] == '99.0' else float(line[nn+10]))

            if self.time[-1] > endtime:
                break

            year = time.year
            month = time.month
            if datatype == 'historical':
                year += 1
                time = datetime(year, month, 1)
                continue
            elif datatype == 'recent':
                month += 1
                if month > 12:
                    break
                else:
                    continue

        self.time = np.array(self.time)
        self.wdir = np.array(self.wdir)
        self.wspd = np.array(self.wspd)
        self.gst = np.array(self.gst)
        self.wvht = np.array(self.wvht)
        self.dpd = np.array(self.dpd)
        self.apd = np.array(self.apd)
        self.mwd = np.array(self.mwd)
        self.pres = np.array(self.pres)
        self.atmp = np.array(self.atmp)
        self.wtmp = np.array(self.wtmp)
        self.dewp = np.array(self.dewp)

    def _get_stdmet_realtime(self):
        """
        Reads the full realtime data feed (last 45 days) from the NDBC server.
        """
        fileurl = _REALTIME_URL+self.id+'.txt'
        r = requests.get(fileurl)
        if not r.status_code == 200:
            raise RuntimeError('Received response status '
            +str(r.status_code)+' from '+fileurl)

        lines = r.text.split('\n')

        for line in lines[-2:1:-1]:
            line = line.split()
            self.time.append(datetime.strptime(''.join(line[:5]), '%Y%m%d%H%M'))
            self.wdir.append(np.nan if line[5] == 'MM' else float(line[5]))
            self.wspd.append(np.nan if line[6] == 'MM' else float(line[6]))
            self.gst.append(np.nan if line[7] == 'MM' else float(line[7]))
            self.wvht.append(np.nan if line[8] == 'MM' else float(line[8]))
            self.dpd.append(np.nan if line[9] == 'MM' else float(line[9]))
            self.apd.append(np.nan if line[10] == 'MM' else float(line[10]))
            self.mwd.append(np.nan if line[11] == 'MM' else float(line[11]))
            self.pres.append(np.nan if line[12] == 'MM' else float(line[12]))
            self.atmp.append(np.nan if line[13] == 'MM' else float(line[13]))
            self.wtmp.append(np.nan if line[14] == 'MM' else float(line[14]))
            self.dewp.append(np.nan if line[15] == 'MM' else float(line[15]))
            self.vis.append(np.nan if line[16] == 'MM' else float(line[16]))
            self.ptdy.append(np.nan if line[17] == 'MM' else float(line[17]))
            self.tide.append(np.nan if line[18] == 'MM' else float(line[18]))

        self.time = np.array(self.time)
        self.wdir = np.array(self.wdir)
        self.wspd = np.array(self.wspd)
        self.gst = np.array(self.gst)
        self.wvht = np.array(self.wvht)
        self.dpd = np.array(self.dpd)
        self.apd = np.array(self.apd)
        self.mwd = np.array(self.mwd)
        self.pres = np.array(self.pres)
        self.atmp = np.array(self.atmp)
        self.wtmp = np.array(self.wtmp)
        self.dewp = np.array(self.dewp)
        self.vis = np.array(self.vis)
        self.ptdy = np.array(self.ptdy)
        self.tide = np.array(self.tide)
