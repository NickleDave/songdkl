import dataclasses


# format for timestamps
STRFTIME_TIMESTAMP = "%y%m%d_%H%M%S"


@dataclasses.dataclass
class DefaultGaussianMixtureKwargs:
    max_iter: int = 100000
    n_init: int = 5
    covariance_type: str = 'full'
    random_state: int = 42


DEFAULT_GMM_KWARGS = DefaultGaussianMixtureKwargs()
