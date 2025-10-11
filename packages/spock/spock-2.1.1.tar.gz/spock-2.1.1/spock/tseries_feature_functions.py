from collections import OrderedDict
import numpy as np
import rebound
from scipy.optimize import brenth
from .feature_functions import find_strongest_MMR
from .simsetup import scale_sim, get_rad, revert_sim_units

# sorts out which pair of planets has a smaller EMcross, labels that pair inner, other adjacent pair outer
# returns a list of two lists, with [label (near or far), i1, i2], where i1 and i2 are the indices, with i1 
# having the smaller semimajor axis
profile = lambda _: _

def get_pairs(sim, indices):
    ps = sim.particles
    sortedindices = sorted(indices, key=lambda i: ps[i].a) # sort from inner to outer
    EMcrossInner = (ps[sortedindices[1]].a-ps[sortedindices[0]].a)/ps[sortedindices[0]].a
    EMcrossOuter = (ps[sortedindices[2]].a-ps[sortedindices[1]].a)/ps[sortedindices[1]].a

    if EMcrossInner < EMcrossOuter:
        return [['near', sortedindices[0], sortedindices[1]], ['far', sortedindices[1], sortedindices[2]]]
    else:
        return [['near', sortedindices[1], sortedindices[2]], ['far', sortedindices[0], sortedindices[1]]]

@profile
def populate_extended_trio(sim, trio, pairs, tseries, i, a10, axis_labels=None, mmr=True, megno=True):
    Ns = 3
    ps = sim.particles
    for q, [label, i1, i2] in enumerate(pairs):
        m1 = ps[i1].m
        m2 = ps[i2].m
        e1x, e1y = ps[i1].e*np.cos(ps[i1].pomega), ps[i1].e*np.sin(ps[i1].pomega)
        e2x, e2y = ps[i2].e*np.cos(ps[i2].pomega), ps[i2].e*np.sin(ps[i2].pomega)
        tseries[i,Ns*q+1] = np.sqrt((e2x-e1x)**2 + (e2y-e1y)**2)
        tseries[i,Ns*q+2] = np.sqrt((m1*e1x + m2*e2x)**2 + (m1*e1y + m2*e2y)**2)/(m1+m2)
        if mmr:
            j, k, tseries[i,Ns*q+3] = find_strongest_MMR(sim, i1, i2) 
        else:
            tseries[i,Ns*q+3] = 0.0

        if axis_labels is not None:
            axis_labels[Ns*q+1] = 'e+_' + label
            axis_labels[Ns*q+2] = 'e-_' + label
            axis_labels[Ns*q+3] = 'max_strength_mmr_' + label


    if axis_labels is not None:
        axis_labels[7] = 'megno'

    if megno:
        tseries[i,7] = sim.megno() # megno
    else:
        tseries[i,7] = 0.0

    orbits = sim.orbits()
    for j, k in enumerate(trio):
        o = orbits[k-1]
        tseries[i, 8+6*j] = o.a/a10
        tseries[i, 9+6*j] = o.e
        tseries[i, 10+6*j] = o.inc
        tseries[i, 11+6*j] = o.Omega
        tseries[i, 12+6*j] = o.pomega
        tseries[i, 13+6*j] = o.theta
        if axis_labels is not None:
            axis_labels[8+6*j] = 'a' + str(j+1)
            axis_labels[9+6*j] = 'e' + str(j+1)
            axis_labels[10+6*j] = 'i' + str(j+1)
            axis_labels[11+6*j] = 'Omega' + str(j+1)
            axis_labels[12+6*j] = 'pomega' + str(j+1)
            axis_labels[13+6*j] = 'theta' + str(j+1)

@profile
def get_extended_tseries(sim, args, mmr=True, megno=True):
    Norbits = args[0]
    Nout = args[1]
    trios = args[2]
   
    a10s = [sim.particles[trio[0]].a for trio in trios]
    minP = np.min([np.abs(p.P) for p in sim.particles[1:sim.N_real]])

    # want hyperbolic case to run so it raises exception
    times = np.linspace(0, Norbits*minP, Nout)
    triopairs, triotseries = [], []
    # axis_labels = ['']*26
    # axis_labels[0] = 'time'
    #7 are same as used for SPOCK (equivalent of old res_tseries), and following 18 are the 6 orbital elements for each of the 3 planets. 
    axis_labels = ['time', 'e+_near', 'e-_near', 'max_strength_mmr_near', 'e+_far', 'e-_far', 'max_strength_mmr_far', 'megno', 'a1', 'e1', 'i1', 'Omega1', 'pomega1', 'theta1', 'a2', 'e2', 'i2', 'Omega2', 'pomega2', 'theta2', 'a3', 'e3', 'i3', 'Omega3', 'pomega3', 'theta3']

    for tr, trio in enumerate(trios): # For each trio there are two adjacent pairs 
        triopairs.append(get_pairs(sim, trio))
        triotseries.append(np.zeros((Nout, 26))*np.nan)
  
    for i, time in enumerate(times):
        try:
            sim.integrate(time, exact_finish_time=0)
        except (rebound.Collision, rebound.Escape):
            stable = False
            return triotseries, sim.t/minP

        for tseries in triotseries:
            tseries[i,0] = sim.t/minP  # time

        for tr, trio in enumerate(trios):
            pairs = triopairs[tr]
            tseries = triotseries[tr] 
            populate_extended_trio(sim, trio, pairs, tseries, i, a10s[tr], mmr=mmr, megno=megno)
            # if i == 0 and tr == 0:
                # populate_extended_trio(sim, trio, pairs, tseries, i, a10s[tr], axis_labels)
            # else:
                # populate_extended_trio(sim, trio, pairs, tseries, i, a10s[tr])
    
    # print(axis_labels)
    #triotseries = pd.DataFrame(data=triotseries, columns=axis_labels)
    stable = True
    return triotseries, stable

def populate_trio(sim, trio, pairs, tseries, i):
    Ns = 3
    ps = sim.particles
    for q, [label, i1, i2] in enumerate(pairs):
        m1 = ps[i1].m
        m2 = ps[i2].m
        e1x, e1y = ps[i1].e*np.cos(ps[i1].pomega), ps[i1].e*np.sin(ps[i1].pomega)
        e2x, e2y = ps[i2].e*np.cos(ps[i2].pomega), ps[i2].e*np.sin(ps[i2].pomega)
        tseries[i,Ns*q+1] = np.sqrt((e2x-e1x)**2 + (e2y-e1y)**2)
        tseries[i,Ns*q+2] = np.sqrt((m1*e1x + m2*e2x)**2 + (m1*e1y + m2*e2y)**2)/(m1+m2)
        j, k, tseries[i,Ns*q+3] = find_strongest_MMR(sim, i1, i2) 

    tseries[i,7] = sim.megno() # megno

def get_tseries(sim, args):
    Norbits = args[0]
    Nout = args[1]
    trios = args[2]
    
    minP = np.min([p.P for p in sim.particles[1:sim.N_real]])

    # want hyperbolic case to run so it raises exception
    times = np.linspace(0, Norbits*np.abs(minP), Nout)
    
    triopairs, triotseries = [], []

    for tr, trio in enumerate(trios): # For each trio there are two adjacent pairs 
        triopairs.append(get_pairs(sim, trio))
        triotseries.append(np.zeros((Nout, 8))*np.nan)
  
    for i, time in enumerate(times):
        try:
            sim.integrate(time, exact_finish_time=0)
        except rebound.Collision:
            stable = False
            return triotseries, stable

        for tseries in triotseries:
            tseries[i,0] = sim.t/minP  # time

        for tr, trio in enumerate(trios):
            pairs = triopairs[tr]
            tseries = triotseries[tr] 
            populate_trio(sim, trio, pairs, tseries, i)
    
    stable = True
    return triotseries, stable
    
def features(sim, args):
    Norbits = args[0]
    Nout = args[1]
    trios = args[2]
    
    ps  = sim.particles
    triofeatures = []
    for tr, trio in enumerate(trios):
        features = OrderedDict()
        pairs = get_pairs(sim, trio)
        for i, [label, i1, i2] in enumerate(pairs):
            features['EMcross'+label] = (ps[i2].a-ps[i1].a)/ps[i1].a
            features['EMfracstd'+label] = np.nan
            features['EPstd'+label] = np.nan
            features['MMRstrength'+label] = np.nan

        features['MEGNO'] = np.nan
        features['MEGNOstd'] = np.nan
        triofeatures.append(features)
    
    triotseries, stable = get_tseries(sim, args)
    if stable == False:
        return triofeatures, stable

    for features, tseries in zip(triofeatures, triotseries):
        EMnear = tseries[:, 1]
        EPnear = tseries[:, 2]
        # cut out first value (init cond) to avoid cases
        # where user sets exactly b*n2 - a*n1 & strength is inf
        MMRstrengthnear = tseries[1:,3]
        EMfar = tseries[:, 4]
        EPfar = tseries[:, 5]
        MMRstrengthfar = tseries[1:,6]
        MEGNO = tseries[:, 7]

        if not np.isnan(MEGNO).any(): # no nans
            features['MEGNO'] = np.median(MEGNO[-int(Nout/10):]) # smooth last 10% to remove oscillations around 2
            features['MEGNOstd'] = MEGNO[int(Nout/5):].std()
        features['MMRstrengthnear'] = np.median(MMRstrengthnear)
        features['MMRstrengthfar'] = np.median(MMRstrengthfar)
        features['EMfracstdnear'] = EMnear.std() / features['EMcrossnear']
        features['EMfracstdfar'] = EMfar.std() / features['EMcrossfar']
        features['EPstdnear'] = EPnear.std() 
        features['EPstdfar'] = EPfar.std() 
    
    return triofeatures, stable

# perfect inelastic merger (taken from REBOUND)
def perfect_merge(sim_pointer, collided_particles_index):
    sim = sim_pointer.contents
    ps = sim.particles

    # note that p1 < p2 is not guaranteed
    i = collided_particles_index.p1
    j = collided_particles_index.p2
    
    # record which pair of planets collide
    global global_col_probs
    if (i == 1 and j == 2) or (i == 2 and j == 1):
        global_col_probs = np.array([1.0, 0.0, 0.0])
    elif (i == 2 and j == 3) or (i == 3 and j == 2):
        global_col_probs = np.array([0.0, 1.0, 0.0])
    elif (i == 1 and j == 3) or (i == 3 and j == 1):
        global_col_probs = np.array([0.0, 0.0, 1.0])

    total_mass = ps[i].m + ps[j].m
    merged_planet = (ps[i]*ps[i].m + ps[j]*ps[j].m)/total_mass # conservation of momentum
    merged_radius = (ps[i].r**3 + ps[j].r**3)**(1/3) # merge radius assuming a uniform density

    ps[i] = merged_planet   # update p1's state vector (mass and radius will need to be changed)
    ps[i].m = total_mass    # update to total mass
    ps[i].r = merged_radius # update to joined radius

    sim.stop() # stop sim
    return 2 # remove particle with index j

# run short sim to get input for MLP model (returns a sim if merger/ejection occurs)
def get_collision_tseries(sim, trio_inds, seed=None):
    # get three-planet sim
    trio_sim = scale_sim(sim, trio_inds)
    ps = trio_sim.particles

    # align z-axis with direction of angular momentum
    rot = rebound.Rotation.to_new_axes(newz=trio_sim.angular_momentum())
    trio_sim.rotate(rot)
    # assign planet radii
    for i in range(1, len(ps)):
        ps[i].r = get_rad(ps[i].m)

    # set integration settings
    trio_sim.integrator = 'mercurius'
    trio_sim.collision = 'direct'
    if not seed is None:
        trio_sim.rand_seed = seed
    trio_sim.collision_resolve = perfect_merge
    Ps = np.array([p.P for p in ps[1:len(ps)]])
    es = np.array([p.e for p in ps[1:len(ps)]])
    minTperi = np.min(Ps*(1 - es)**1.5/np.sqrt(1 + es))
    trio_sim.dt = 0.05*minTperi

    global global_col_probs
    global_col_probs = np.array([-1.0, -1.0, -1.0]) # default
    times = np.linspace(trio_sim.t, trio_sim.t + 1e4, 100)
    states = [np.log10(ps[1].m), np.log10(ps[2].m), np.log10(ps[3].m)]

    for t in times:
        trio_sim.integrate(t, exact_finish_time=0)
        # check for ejected planets
        to_remove = []
        for j, p in enumerate(ps[1:]):
            if p.d > 50.:
                to_remove.append(j+1)
                global_col_probs = np.array([0., 0., 0.])
        for j in to_remove:
            trio_sim.remove(j) 
        # if there was no merger/ejection, record states
        if len(ps) == 4:
            if ps[1].inc == 0.0 or ps[2].inc == 0.0 or ps[3].inc == 0.0:
                # use very small inclinations to avoid -infs
                states.extend([ps[1].a, ps[2].a, ps[3].a,
                               np.log10(ps[1].e), np.log10(ps[2].e), np.log10(ps[3].e),
                               -3.0, -3.0, -3.0,
                               np.sin(ps[1].pomega), np.sin(ps[2].pomega), np.sin(ps[3].pomega),
                               np.cos(ps[1].pomega), np.cos(ps[2].pomega), np.cos(ps[3].pomega),
                               np.sin(ps[1].Omega), np.sin(ps[2].Omega), np.sin(ps[3].Omega),
                               np.cos(ps[1].Omega), np.cos(ps[2].Omega), np.cos(ps[3].Omega)])
            else:
                states.extend([ps[1].a, ps[2].a, ps[3].a,
                               np.log10(ps[1].e), np.log10(ps[2].e), np.log10(ps[3].e),
                               np.log10(ps[1].inc), np.log10(ps[2].inc), np.log10(ps[3].inc),
                               np.sin(ps[1].pomega), np.sin(ps[2].pomega), np.sin(ps[3].pomega),
                               np.cos(ps[1].pomega), np.cos(ps[2].pomega), np.cos(ps[3].pomega),
                               np.sin(ps[1].Omega), np.sin(ps[2].Omega), np.sin(ps[3].Omega),
                               np.cos(ps[1].Omega), np.cos(ps[2].Omega), np.cos(ps[3].Omega)])
   
    # change axis orientation back to original sim here
    trio_sim.rotate(rot.inverse())
    
    trio_sim = revert_sim_units([trio_sim])[0]            # revert returns a list of length 1 when we pass 1 sim
    trio_sim.rot = rot                                    # store rotation object into invariant plane if needed
    return np.array(states), trio_sim, global_col_probs
