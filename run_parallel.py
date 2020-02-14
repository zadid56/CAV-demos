import os                                                                       
from multiprocessing import Pool 

processes = ('controller_rcv_hetnet.py', 'controller_rcv_wlan.py')

def run_process(process):
    os.system('python {}'.format(process))

pool = Pool(processes=2)
pool.map(run_process, processes)
