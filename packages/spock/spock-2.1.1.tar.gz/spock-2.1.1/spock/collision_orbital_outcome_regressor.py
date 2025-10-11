import numpy as np
import os
import torch
import warnings
import rebound as rb
from .simsetup import scale_sim, get_rad, revert_sim_units, replace_p, replace_trio
from .tseries_feature_functions import get_collision_tseries

# pytorch MLP
class reg_MLP(torch.nn.Module):

    # initialize pytorch MLP with specified number of input/hidden/output nodes
    def __init__(self, n_feature, n_hidden, n_output, num_hidden_layers):
        super(reg_MLP, self).__init__()
        self.input = torch.nn.Linear(n_feature, n_hidden).to("cpu")
        self.predict = torch.nn.Linear(n_hidden, n_output).to("cpu")

        self.hiddens = []
        for i in range(num_hidden_layers-1):
            self.hiddens.append(torch.nn.Linear(n_hidden, n_hidden).to("cpu"))

        # means and standard deviations for re-scaling inputs
        self.mass_means = np.array([-5.47074599, -5.50485362, -5.55107994])
        self.mass_stds = np.array([0.86575343, 0.86634857, 0.80166568])
        self.orb_means = np.array([1.10103604e+00, 1.34531896e+00, 1.25862804e+00, -1.44014696e+00,
                                   -1.44382469e+00, -1.48199204e+00, -1.58037780e+00, -1.59658646e+00,
                                   -1.46025210e+00, 5.35126034e-04, 2.93399827e-04, -2.07964769e-04,
                                   1.84826520e-04, 2.00942518e-04, 1.34561831e-03, -3.81075318e-02,
                                   -4.50480364e-02, -8.37049604e-02, 4.20809298e-02, 4.89242546e-02,
                                   7.81205381e-02])
        self.orb_stds = np.array([0.17770125, 0.27459303, 0.30934483, 0.60370379, 0.5976446, 0.59195887,
                                  0.68390679, 0.70470389, 0.62941292, 0.70706072, 0.70825354, 0.7082275,
                                  0.70715261, 0.70595807, 0.70598297, 0.68020376, 0.67983686, 0.66536654,
                                  0.73082135, 0.73034166, 0.73768424])

        self.output_means = np.array([1.20088092, 1.31667089, -1.4599554, -1.16721504, -2.10491322, -1.3807749])
        self.output_stds = np.array([0.23123815, 0.63026354, 0.51926874, 0.49942197, 0.74455827, 0.58098256])
        self.output_maxes = (np.array([50.0, 50.0, 0.0, 0.0, np.log10(np.pi), np.log10(np.pi)]) - self.output_means)/self.output_stds

        self.input_means = np.concatenate((self.mass_means, np.tile(self.orb_means, 100)))
        self.input_stds = np.concatenate((self.mass_stds, np.tile(self.orb_stds, 100)))

    # function to compute output pytorch tensors from input
    def forward(self, x):
        x = torch.relu(self.input(x))

        for hidden_layer in self.hiddens:
             x = torch.relu(hidden_layer(x))

        x = self.predict(x)
        return x

    # function to get means and stds from time series inputs
    def get_means_stds(self, inputs, min_nt=5):
        masses = inputs[:,:3]
        orb_elements = inputs[:,3:].reshape((len(inputs), 100, 21))
        means = torch.mean(orb_elements, dim=1)
        stds = torch.std(orb_elements, dim=1)
        pooled_inputs = torch.concatenate((masses, means, stds), dim=1)

        return pooled_inputs

    # function to make predictions with trained model (takes and return numpy array)
    def make_pred(self, Xs):
        self.eval()
        Xs = (Xs - self.input_means)/self.input_stds
        pooled_Xs = self.get_means_stds(torch.tensor(Xs, dtype=torch.float32))
        Ys = self(pooled_Xs).detach().numpy()
        Ys = Ys*self.output_stds + self.output_means

        return Ys

# collision outcome model class
class CollisionOrbitalOutcomeRegressor():
    # load regression model
    def __init__(self, model_file='collision_orbital_outcome_regressor.torch', seed=None):
        self.reg_model = reg_MLP(45, 60, 6, 1)
        pwd = os.path.dirname(__file__)
        self.reg_model.load_state_dict(torch.load(pwd + '/models/' + model_file))

        self.seed = seed

    def predict_collision_outcome(self, sims, collision_inds, trio_inds=None):
        """
        Predict outcome of a planet-planet collision in system(s) of three (or more) planets.

        Parameters:

        sims (rebound.Simulation or list): Initial state of the multiplanet system(s).
        collision_inds (list): Indices of the planets that are involved in the collision (e.g., [1, 2] for a collision between planet 1 and planet 2).
        trio_inds (list): Indices of the three planets that make up the three-planet subset of the full system (e.g., [1, 2, 3] for the innermost three planets). Post-collision orbital elements will be predicted for the newly-merged planet and the planet in the trio that was not involved in the collision.

        Returns:

        rebound.Simulation or list: Predicted state of the post-collision system(s).
        """
        single_sim = False
        if isinstance(sims, rb.Simulation): # passed a single sim
            sims = [sims]
            collision_inds = [collision_inds]
            single_sim = True

        # if trio_inds was not provided, assume first three planets (doesn't need to be passed for three-planet systems)
        if trio_inds is None:
            trio_inds = []
            for i in range(len(sims)):
                trio_inds.append([1, 2, 3])

        sims = [scale_sim(sim, np.arange(1, sim.N)) for sim in sims] # re-scale input sims and convert units
        done_sims = []
        trio_sims = []
        mlp_inputs = []
        done_inds = []
        for i, sim in enumerate(sims):
            out, trio_sim, _ = get_collision_tseries(sim, trio_inds[i], seed=self.seed)

            if len(trio_sim.particles) == 4:
                # no merger (or ejection)
                mlp_inputs.append(out)
                trio_sims.append(trio_sim)
            else:
                # if merger/ejection occurred, save sim
                done_sims.append(replace_trio(sim, trio_inds[i], trio_sim))
                done_inds.append(i)

        # get collision_inds for sims that did not experience a merger
        if 0 < len(done_inds):
            mask = np.ones(len(collision_inds), dtype=bool)
            mask[np.array(done_inds)] = False
            subset_collision_inds = list(np.array(collision_inds)[mask])
        else:
            subset_collision_inds = collision_inds

        return self._predict_collision_probs_from_inputs(sims, subset_collision_inds, trio_inds, trio_sims, mlp_inputs, done_sims, done_inds, single_sim)

    # function to predict collision outcomes provided all inputs (useful if re-using inputs for the class and reg models)
    def _predict_collision_probs_from_inputs(self, sims, collision_inds, trio_inds, trio_sims, mlp_inputs, done_sims, done_inds, single_sim=False):
        if 0 < len(mlp_inputs):
            # re-order input array based on input collision_inds
            reg_inputs = []
            for i, col_ind in enumerate(collision_inds):
                masses = mlp_inputs[i][:3]
                orb_elements = mlp_inputs[i][3:]

                if (col_ind[0] == 1 and col_ind[1] == 2) or (col_ind[0] == 2 and col_ind[1] == 1): # merge planets 1 and 2
                    ordered_masses = masses
                    ordered_orb_elements = orb_elements
                elif (col_ind[0] == 2 and col_ind[1] == 3) or (col_ind[0] == 3 and col_ind[1] == 2): # merge planets 2 and 3
                    ordered_masses = np.array([masses[1], masses[2], masses[0]])
                    ordered_orb_elements = np.column_stack((orb_elements[1::3], orb_elements[2::3], orb_elements[0::3])).flatten()
                elif (col_ind[0] == 1 and col_ind[1] == 3) or (col_ind[0] == 3 and col_ind[1] == 1): # merge planets 1 and 3
                    ordered_masses = np.array([masses[0], masses[2], masses[1]])
                    ordered_orb_elements = np.column_stack((orb_elements[0::3], orb_elements[2::3], orb_elements[1::3])).flatten()
                else:
                    warnings.warn('Invalid collision_inds')

                reg_inputs.append(np.concatenate((ordered_masses, ordered_orb_elements)))

            # predict orbital elements with regression model
            reg_inputs = np.array(reg_inputs)
            reg_outputs = self.reg_model.make_pred(reg_inputs)

            m1s = 10**reg_inputs[:,0] + 10**reg_inputs[:,1] # new planet
            m2s = 10**reg_inputs[:,2] # surviving planet
            a1s = reg_outputs[:,0]
            a2s = reg_outputs[:,1]
            e1s = 10**reg_outputs[:,2]
            e2s = 10**reg_outputs[:,3]
            inc1s = 10**reg_outputs[:,4]
            inc2s = 10**reg_outputs[:,5]

        new_sims = []
        j = 0 # index for new sims array
        k = 0 # index for mlp prediction arrays
        for i in range(len(sims)):
            if i in done_inds:
                new_sims.append(done_sims[j])
                j += 1
            else:
                # create sim that contains state of two predicted planets
                new_state_sim = rb.Simulation()
                new_state_sim.G = 4*np.pi**2 # units in which a1=1.0 and P1=1.0
                new_state_sim.add(m=1.00)

                try:
                    if (0.0 < a1s[k] < 50.0) and (0.0 <= e1s[k] < 1.0):
                        new_state_sim.add(m=m1s[k], a=a1s[k], e=e1s[k], inc=inc1s[k], pomega=np.random.uniform(0.0, 2*np.pi), Omega=np.random.uniform(0.0, 2*np.pi), l=np.random.uniform(0.0, 2*np.pi))
                    else:
                        warnings.warn('Removing ejected planet')
                except Exception as e:
                    warnings.warn('Removing planet with unphysical orbital elements')
                try:
                    if (0.0 < a2s[k] < 50.0) and (0.0 <= e2s[k] < 1.0):
                        new_state_sim.add(m=m2s[k], a=a2s[k], e=e2s[k], inc=inc2s[k], pomega=np.random.uniform(0.0, 2*np.pi), Omega=np.random.uniform(0.0, 2*np.pi), l=np.random.uniform(0.0, 2*np.pi))
                    else:
                        warnings.warn('Removing ejected planet')
                except Exception as e:
                    warnings.warn('Removing planet with unphysical orbital elements')
                new_state_sim.move_to_com()

                new_state_sim.rotate(trio_sims[k].rot.inverse()) # rotate back to original orientation

                # replace trio with predicted duo (or single/zero if planets have unphysical orbital elements)
                new_sims.append(replace_trio(sims[i], trio_inds[i], new_state_sim))
                k += 1

        # convert sims back to original units
        new_sims = revert_sim_units(new_sims)

        if single_sim:
            new_sims = new_sims[0]

        return new_sims

    def cite(self):
        """
        Print citations to papers relevant to this model.
        """

        txt = r"""This paper made use of stability predictions from the Stability of Planetary Orbital Configurations Klassifier (SPOCK) package \\citep{spock}. Predictions for the orbital outcomes from dynamical instabilities were made with the CollisionOrbitalOutcomeRegressor, a multilayer perceptron model (MLP), which, when given an unstable pair of planets to merge in an adjacent trio of planets, predicts the resulting orbits of the two remaining planets \citep{giantimpact}."""
        bib = """
@ARTICLE{spock,
   author = {{Tamayo}, Daniel and {Cranmer}, Miles and {Hadden}, Samuel and {Rein}, Hanno and {Battaglia}, Peter and {Obertas}, Alysa and {Armitage}, Philip J. and {Ho}, Shirley and {Spergel}, David N. and {Gilbertson}, Christian and {Hussain}, Naireen and {Silburt}, Ari and {Jontof-Hutter}, Daniel and {Menou}, Kristen},
    title = "{Predicting the long-term stability of compact multiplanet systems}",
  journal = {Proceedings of the National Academy of Science},
 keywords = {machine learning, dynamical systems, UAT:498, orbital dynamics, UAT:222, Astrophysics - Earth and Planetary Astrophysics},
     year = 2020,
    month = aug,
   volume = {117},
   number = {31},
    pages = {18194-18205},
      doi = {10.1073/pnas.2001258117},
archivePrefix = {arXiv},
   eprint = {2007.06521},
primaryClass = {astro-ph.EP},
   adsurl = {https://ui.adsabs.harvard.edu/abs/2020PNAS..11718194T},
  adsnote = {Provided by the SAO/NASA Astrophysics Data System}
}

@ARTICLE{giantimpact,
}
"""
        print(txt + "\n\n\n" + bib)

