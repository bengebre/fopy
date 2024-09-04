import numpy as np
import re
import subprocess
import json
from astropy.coordinates import SkyCoord

class Fopy:

    def __init__(self,solve_dir,reset):

        self.solve_dir = solve_dir.rstrip('/')
        self.solve_id = 0

        mkdir_str = "mkdir -p {:s}".format(solve_dir)
        result = subprocess.run(mkdir_str, shell=True, capture_output=True, text=True)

        if reset:
            self.reset()

    #returns a date string in MPC format
    def mpc_date(self,date): #date is jdate float
            from astropy.time import Time
    
            t = Time(date,format='jd')
            tdate = t.datetime
            y = tdate.year
            m = tdate.month
            d = tdate.day
            dd = (tdate.hour + tdate.minute/60.0 + tdate.second/3600.0)/24.0
            df = float(d) + float(dd)
            date_str = "{:d} {:02d} {:08.5f}".format(y,m,df)
    
            return date_str

    #returns a radec string in MPC format
    def mpc_radec(self,coord): #(ra,dec) tuple deg
            mpc_coord = SkyCoord(coord[0],coord[1],unit="deg")
            hmsdms3 = SkyCoord.to_string(mpc_coord,style='hmsdms',precision=3,pad=True)
            hmsdms2 = SkyCoord.to_string(mpc_coord,style='hmsdms',precision=2,pad=True)
            hmsdms = hmsdms3.split(' ')[0] + ' ' + hmsdms2.split(' ')[1] #should be len() == 24
            hmsdms = re.sub("[a-z]"," ",hmsdms)
            hmsdms = re.sub("  "," ",hmsdms)
            hmsdms = re.sub(" \+","+",hmsdms)
            hmsdms = re.sub(" \-","-",hmsdms)
            hmsdms = re.sub("\s+$","",hmsdms)

            return hmsdms

    #returns an 80-column MPC formatted line for an optical observation
    def mpc_line(self,obs,jd,radec,mag,obs_code,obs_vec=False):
    
            if obs_vec:
                    obs_code = 'C57'
    
            if np.isnan(mag):
                    line_end = "                     {:s}".format(obs_code)
            else:  
                    line_end = "         {:.1f} i      {:s}".format(mag,obs_code)
    
            date_str = self.mpc_date(jd)
            hmsdms = self.mpc_radec(radec)
            mpc_str = "{:s}{:s} {:s}{:s}".format(obs,date_str,hmsdms,line_end)

            #for creation of vector pointing to observer
            if obs_vec:
                    mpc_str = mpc_str[:14] + 'S' + mpc_str[15:]
                    obs_line_start = obs
                    obs_line_end = '       C57'
                    p = obs_vec
                    vec_str = ' 2 '
                    for x in ['x','y','z']:
                            x = p[x]
                            if x > 0:
                                    x = "+{:.8f} ".format(x)
                            else:
                                    x = "{:.8f} ".format(x)
                            vec_str = vec_str + x
    
                    obs_str = "{:s}{:s}{:s}{:s}".format(obs_line_start,date_str,vec_str,obs_line_end)
                    obs_str = obs_str[:14] + 's' + obs_str[15:]
                    return mpc_str + "\n" + obs_str
    
            return mpc_str

    #reset the solve dir (remove mpc and json files)
    def reset(self):
        rm_str = "rm -f {:s}/S*.{{mpc,json}}".format(self.solve_dir)
        result = subprocess.run(rm_str, shell=True, capture_output=True, text=True)

    #write mpc file for observations
    def write(self,radecs,times,locs,idx=None):
        increment=True

        if idx==None:
            idx=self.solve_id
            increment=False
        
        fn = self.solve_dir + "/S{:06d}.mpc".format(idx)
        
        f = open(fn,'w')
        obs_str = "     S{:06d}  C".format(idx)
        for i in range(0,len(times)):
            f.write(self.mpc_line(obs_str,times[i],(radecs[i,0],radecs[i,1]),np.nan,locs[i]))
            f.write("\n")
        f.close()

        if increment:
            self.solve_id += 1

        return fn

    #solve mpc file with Find_Orb
    def solve(self,fname):

        fo_str = "fo {:s}".format(fname)
        result = subprocess.run(fo_str, shell=True, capture_output=True, text=True)

        file_idx = fname.split('/')[-1].split('.')[0]
        mv_str = "rm -f {:s}/{:s}.json; mv ~/.find_orb/jsons/{:s}.json {:s}".format(self.solve_dir,file_idx,file_idx,self.solve_dir)
        result = subprocess.run(mv_str, shell=True, capture_output=True, text=True)

        return "{:s}/{:s}.json".format(self.solve_dir,file_idx)

    #parse json produced by Find_Orb
    def load_json(self,fname):
        with open(fname,'r') as file: 
            data = json.load(file)

        return data
