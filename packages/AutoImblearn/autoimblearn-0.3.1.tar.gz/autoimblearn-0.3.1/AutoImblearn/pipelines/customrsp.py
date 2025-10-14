from AutoImblearn.components.resamplers import RunSmoteSampler, RunImblearnSampler

import logging
import numpy as np
import pandas as pd

# Docker-based resamplers - factory functions similar to imputers
rsps = {
    'rus': lambda **kw: RunImblearnSampler(model='rus', **kw),
    'ros': lambda **kw: RunImblearnSampler(model='ros', **kw),
    'smote': lambda **kw: RunImblearnSampler(model='smote', **kw),
    'mwmote': lambda **kw: RunSmoteSampler(model='mwmote', **kw),
}

def value_counter(Y: np.ndarray):
    values, counts = np.unique(Y, return_counts=True)
    for value, count in zip(values, counts):
        dist = count / Y.shape[0] * 100
        logging.info("\t\t Class={}, n={},\t ({:.2f}%)".format(value, count, dist))


class CustomResamplar:
    """ Resamplar oject to re-sample imbalanced data
        Args:
            X (np.ndarray):
            Y (np.ndarray):
    """

    def __init__(self, X: np.ndarray, Y: np.ndarray):

        self.X = X
        self.Y = Y

    def need_resample(self, samratio=None):
        """ Test if need re-sample
        """
        # If nothing is given, use default settings in the models
        if samratio is None:
            return True

        _, counts = np.unique(self.Y, return_counts=True)
        ratio = counts[1] / counts[0]

        return ratio < samratio

    def resample(self, args,  rsp=None, ratio=None):
        logging.info("\t Before Re-Sampling")
        value_counter(self.Y)
        if rsp in rsps.keys():
            # Instantiate resampler with data_folder
            factory = rsps[rsp]
            resampler = factory(data_folder=args.path)
            if ratio is None:
                pass
            elif ratio is not None and hasattr(resampler, 'set_params'):
                resampler.set_params(**{"sampling_strategy": ratio})
            else:
                raise ValueError("can't set resampling ratio for {}".format(rsp))
        else:
            raise ValueError("Re-sampling method {} is not defined".format(rsp))

        self.X, self.Y = resampler.fit_resample(self.X, self.Y)
        logging.info("\t After Re-Sampling")
        value_counter(self.Y)

        return self.X, self.Y
