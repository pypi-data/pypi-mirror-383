import unittest
import os
import rebound
import pandas as pd
import numpy as np
from sklearn import metrics
from sklearn.metrics import roc_curve, confusion_matrix, auc
from spock import FeatureClassifier, NbodyRegressor
from spock.feature_functions import get_tseries
from spock.simsetup import setup_sim 
from spock.features import Trio

def get_sim(row, dataset):
    '''Given a row number, and a data sheet containing initial conditions, returns a corresponding simulation

        Arguments:
            row: what row the simulation you would like to create is on
                format of row is in order:
                [index, 'p0m', 'p0x', 'p0y', 'p0z', 'p0vx', 'p0vy', 'p0vz', 'p1m', 'p1x', 'p1y',
                'p1z', 'p1vx', 'p1vy', 'p1vz', 'p2m', 'p2x', 'p2y', 'p2z', 'p2vx',
                'p2vy', 'p2vz', 'p3m', 'p3x', 'p3y', 'p3z', 'p3vx', 'p3vy', 'p3vz']

            dataset: what dataset contains your initial conditions

        return: returns a rebound simulation with the specified initial conditions'''
    try:
        data = dataset.iloc[row]
        sim = rebound.Simulation()
        sim.G=4*np.pi**2
        sim.add(m=data['p0m'], x=data['p0x'], y=data['p0y'], z=data['p0z'], vx=data['p0vx'], vy=data['p0vy'], vz=data['p0vz'])
        sim.add(m=data['p1m'], x=data['p1x'], y=data['p1y'], z=data['p1z'], vx=data['p1vx'], vy=data['p1vy'], vz=data['p1vz'])
        sim.add(m=data['p2m'], x=data['p2x'], y=data['p2y'], z=data['p2z'], vx=data['p2vx'], vy=data['p2vy'], vz=data['p2vz'])
        sim.add(m=data['p3m'], x=data['p3x'], y=data['p3y'], z=data['p3z'], vx=data['p3vx'], vy=data['p3vy'], vz=data['p3vz'])
        return sim
    except:
        print("Error reading initial condition {0}".format(row))
        return None


def ROC_curve( preds,y):
    '''given predictions and the true value, returns AUC information'''
    fpr, tpr, ROCthresholds = roc_curve(y, preds)
    roc_auc = metrics.roc_auc_score(y, preds)
    return roc_auc, fpr, tpr, ROCthresholds

def unstable2psim():
    sim = rebound.Simulation()
    sim.add(m=1.)
    sim.add(m=1.e-4, P=1)
    sim.add(m=1.e-4, P=1.01, f=np.pi)
    return sim

def unstable2psimhyperbolic():
    sim = rebound.Simulation()
    sim.add(m=1.)
    sim.add(m=1.e-4, a=-1, e=1.01)
    sim.add(m=1.e-4, a=-1.05, e=1.01, f=np.pi/6)
    return sim

def unstable2psimhighe():
    sim = rebound.Simulation()
    sim.add(m=1.)
    sim.add(m=1.e-4, a=1, e=.99)
    sim.add(m=1.e-4, a=1.05, e=0.99, f=np.pi/6)
    return sim

def stable2psim():
    sim = rebound.Simulation()
    sim.add(m=1.)
    sim.add(m=1.e-4, P=1)
    sim.add(m=1.e-4, P=2.3, f=np.pi)
    return sim

def singlesim():
    sim = rebound.Simulation()
    sim.add(m=1.)
    sim.add(m=1.e-4, P=1)
    return sim

def unstablesim():
    sim = rebound.Simulation()
    sim.add(m=1.)
    sim.add(m=1.e-4, P=1)
    sim.add(m=1.e-4, P=1.3)
    sim.add(m=1.e-4, P=1.6)
    for p in sim.particles[1:]:
        p.r = p.a*(p.m/3)**(1/3)
    sim.move_to_com()
    sim.collision='line'
    sim.integrator="whfast"
    sim.dt = 0.05
    return sim

def longstablesim():
    sim = rebound.Simulation()
    sim.add(m=1.)
    sim.add(m=1.e-7, P=1)
    sim.add(m=1.e-7, P=2.1)
    sim.add(m=1.e-7, P=4.5)
    for p in sim.particles[1:]:
        p.r = p.a*(p.m/3)**(1/3)
    sim.move_to_com()
    sim.collision='line'
    sim.integrator="whfast"
    sim.dt = 0.05
    return sim

def solarsystemsim():
    sim = rebound.Simulation()
    sim.add(m=1.)
    sim.add(m=1.7e-7, a=0.39, e=0.21)
    sim.add(m=2.4e-6, a=0.72, e=0.007)
    sim.add(m=3.e-6, a=1, e=0.017)
    sim.add(m=3.2e-7, a=1.52, e=0.09)
    sim.add(m=1.e-3, a=5.2, e=0.049)
    sim.add(m=2.9e-4, a=9.54, e=0.055)
    sim.add(m=4.4e-5, a=19.2, e=0.047)
    sim.add(m=5.2e-5, a=30.1, e=0.009)
    for p in sim.particles[1:]:
        p.r = p.a*(p.m/3)**(1/3)
    sim.move_to_com()
    sim.collision='line'
    sim.integrator="whfast"
    sim.dt = 0.05
    return sim

def hyperbolicsim():
    sim = rebound.Simulation()
    sim.add(m=1.)
    sim.add(m=1.e-5, a=-1., e=1.2)
    sim.add(m=1.e-5, a=2.)
    sim.add(m=1.e-5, a=3.)
    return sim

def escapesim():
    sim = rebound.Simulation()
    sim.add(m=1.)
    sim.add(m=1.e-12, P=3.14, e=0.03, l=0.5)
    sim.add(m=1.e-12, P=4.396, e=0.03, l=4.8)
    sim.add(m=1.e-12, a=100, e=0.999)
    return sim

def rescale(sim, dscale, tscale, mscale):
    simr = rebound.Simulation()
    vscale = dscale/tscale
    simr.G *= mscale*tscale**2/dscale**3

    for p in sim.particles:
        simr.add(m=p.m/mscale, x=p.x/dscale, y=p.y/dscale, z=p.z/dscale, vx=p.vx/vscale, vy=p.vy/vscale, vz=p.vz/vscale, r=p.r/dscale)

    return simr

class TestClassifier(unittest.TestCase):
    def setUp(self):
        self.model = FeatureClassifier()

    def test_list(self):
        stable_target = [0, 0, 0, 0.7]
        stable = self.model.predict_stable([hyperbolicsim(), escapesim(), unstablesim(), longstablesim()])
        self.assertEqual(stable[0], 0)
        self.assertEqual(stable[1], 0)
        self.assertEqual(stable[2], 0)
        self.assertGreater(stable[3], 0.7)

    def test_sim_unchanged(self):
        sim = rebound.Simulation()
        sim.add(m=1.)
        sim.add(m=1.e-5, P=1.)
        sim.add(m=1.e-5, P=2.)
        sim.add(m=1.e-5, P=3.)
        sim.integrate(1.2)
        x0 = sim.particles[1].x
        p1 = self.model.predict_stable(sim)
        self.assertEqual(sim.particles[1].x, x0)

    def test_repeat(self):
        sim = rebound.Simulation()
        sim.add(m=1.)
        sim.add(m=1.e-5, P=1.)
        sim.add(m=1.e-5, P=2.)
        sim.add(m=1.e-5, P=3.)
        p1 = self.model.predict_stable(sim)
        p2 = self.model.predict_stable(sim)
        self.assertEqual(p1, p2)

    def test_same_trajectory(self):
        sim = longstablesim()
        sim = setup_sim(sim)
        testClass = FeatureClassifier()
        trios = [Trio(trio_indices=[1,2,3], sim=sim, Nout=80)]
        _, _ = testClass.get_tseries(sim, trios, Norbits=1e4, Nout=80)
        x1 = sim.particles[1].x

        sim = longstablesim()
        nbody = NbodyRegressor()
        nbody.predict_stable(sim, tmax=1e4, archive_filename='temp.bin', archive_interval=1.e4)
        sa = rebound.Simulationarchive('temp.bin')
        sim = sa[-1]
        x2 = sim.particles[1].x
        self.assertAlmostEqual(x1, x2, delta=1.e-5)

    def test_single(self):
        sim = singlesim()
        prob = self.model.predict_stable(sim)
        self.assertEqual(prob, 1)

    def test_single_list(self):
        sims = [singlesim(), singlesim()]
        probs = self.model.predict_stable(sims)
        self.assertTrue(all(prob == 1 for prob in probs))

    def test_stable2p(self):
        sim = stable2psim()
        prob = self.model.predict_stable(sim)
        self.assertEqual(prob, 1)

    def test_unstable2p(self):
        sim = unstable2psim()
        prob = self.model.predict_stable(sim)
        self.assertEqual(prob, 0)

    def test_unstable2phyperbolic(self):
        sim = unstable2psimhyperbolic()
        prob = self.model.predict_stable(sim)
        self.assertEqual(prob, 0)

    def test_unstable2phighe(self):
        sim = unstable2psimhighe()
        prob = self.model.predict_stable(sim)
        self.assertEqual(prob, 0)

    def test_stable2p_list(self):
        sims = [stable2psim(), stable2psim()]
        probs = self.model.predict_stable(sims)
        self.assertTrue(all(prob == 1 for prob in probs))
 
    def test_unstable2p_list(self):
        sims = [unstable2psim(), unstable2psim()]
        probs = self.model.predict_stable(sims)
        self.assertTrue(all(prob == 0 for prob in probs))

    # when chaotic realization matters, probs will vary more (eg t_inst=2e4)
    def test_galilean_transformation(self):
        sim = longstablesim()
        sim.move_to_com()
        p_com = self.model.predict_stable(sim)

        sim = longstablesim()
        for p in sim.particles:
            p.vx += 1000
        p_moving = self.model.predict_stable(sim)
        self.assertAlmostEqual(p_com, p_moving, delta=1.e-2)
   
    def test_rescale_distances(self):
        sim = longstablesim()
        p0 = self.model.predict_stable(sim)

        sim = longstablesim()
        sim = rescale(sim, dscale=1e10, tscale=1, mscale=1)
        p1 = self.model.predict_stable(sim)
        self.assertAlmostEqual(p0, p1, delta=1.e-2)
    
    def test_rescale_times(self):
        sim = longstablesim()
        p0 = self.model.predict_stable(sim)

        sim = longstablesim()
        sim = rescale(sim, dscale=1, tscale=1e10, mscale=1)
        p1 = self.model.predict_stable(sim)
        self.assertAlmostEqual(p0, p1, delta=1.e-1)

    def test_rescale_masses(self):
        sim = longstablesim()
        p0 = self.model.predict_stable(sim)

        sim = longstablesim()
        sim = rescale(sim, dscale=1, tscale=1, mscale=1e10)
        p1 = self.model.predict_stable(sim)
        self.assertAlmostEqual(p0, p1, delta=1.e-2)
    
    def test_hyperbolic(self):
        sim = hyperbolicsim()
        self.assertEqual(self.model.predict_stable(sim), 0)
    
    def test_escape(self):
        sim = escapesim()
        self.assertEqual(self.model.predict_stable(sim), 0)
    
    def test_unstable_in_short_integration(self):
        sim = unstablesim()
        self.assertEqual(self.model.predict_stable(sim), 0)
    
    def test_solarsystem(self):
        sim = solarsystemsim()
        self.assertGreater(self.model.predict_stable(sim), 0.7)
    
    def test_stable(self):
        sim = longstablesim()
        self.assertGreater(self.model.predict_stable(sim), 0.7)

    def test_auc(self):
        '''Tests to ensure that the models stability prediction has a high enough AUC'''
        path = os.path.abspath(os.path.dirname(__file__))
        conditions = pd.read_csv(path+'/test100ResTest.csv')
        simlist = []
        for x in range (conditions.shape[0]):
            simlist.append(get_sim(x,conditions))
        roc_auc, fpr, tpr, ROCthresholds = ROC_curve(self.model.predict_stable(simlist),conditions['Stable'])
        self.assertGreater(roc_auc,0.93)
    
if __name__ == '__main__':
    unittest.main()
