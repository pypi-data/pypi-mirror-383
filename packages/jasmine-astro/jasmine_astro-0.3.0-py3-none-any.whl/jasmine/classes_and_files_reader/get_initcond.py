import pandas as pd
import numpy as np

esh = ['0_756_2411', '0_42_1353', '0_913_1596', '0_718_988', '0_87_3097',
'0_876_158','0_722_3302','0_130_1677']
DST = '/Users/stela/Documents/teste/ICGS_on_failures_v24_v31_done'

columns_names = ['log(s)', 'log(q)', 'u0', 'alpha', 'log(rho)', 'log(tE)', 't0', 'fs0', 'fb0', 'fs1', 'fb1', 'fs2', 'fb2', 'chi20', 'chi21', 'chi22', 'chi2sum', 'delta_pspl_chi2']
i=0
for event in esh:
    init_conds = pd.read_csv(f'{DST}/event_{event}/Data/ICGS_initconds_chi2.txt', sep='\s+',
                             names=columns_names, usecols=[0, 1, 2, 3, 4, 5, 6, 16, 17])
    init_conds['event']= event
    init_conds['sep'] = np.exp(init_conds['log(s)'])
    init_conds['q'] = np.exp(init_conds['log(q)'])
    init_conds['rho'] = np.exp(init_conds['log(rho)'])
    init_conds['tE'] = np.exp(init_conds['log(tE)'])
    init_conds = init_conds.iloc[:,[9,10,11,2,3,12,13,6,7,8]]
    if i ==0:
        init_conds.to_csv('/Users/stela/Documents/Scripts/orbital_task/RTModel_runs/154_failures_v24_v31/initial_conditions_8_events.txt',index=None,sep=' ',mode='w')
    else:init_conds.to_csv('/Users/stela/Documents/Scripts/orbital_task/RTModel_runs/154_failures_v24_v31/initial_conditions_8_events.txt',index=None,sep=' ',mode='a',header=False)
    i+=1
    

                