# Copyright 2024 BDP Ecosystem Limited. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================


__version__ = "0.0.6"
__version_info__ = (0, 0, 6)

from . import channel
from . import ion
from . import neuron
from ._base import (
    HHTypedNeuron,
    IonChannel,
    Ion,
    Channel,
    MixIons,
    mix_ions,
    IonInfo,
)
from ._integrator import *
from ._integrator_protocol import (
    DiffEqState,
    DiffEqModule,
    IndependentIntegration,
)
from ._morphology import (
    Segment,
    Section,
    CylinderSection,
    PointSection,
    Morphology,
)
from ._morphology_from_asc import from_asc
from ._morphology_from_swc import from_swc
from ._multi_compartment import (
    MultiCompartment,
)
from ._single_compartment import (
    SingleCompartment,
)

_deprecations = {
    'SingleCompartment': (
        f"braincell.neuron.SingleCompartment has been moved "
        f"into braincell.SingleCompartment",
        SingleCompartment
    ),
    'MultiCompartment': (
        f"braincell.neuron.MultiCompartment has been moved "
        f"into braincell.MultiCompartment",
        MultiCompartment
    ),
}

from braincell._misc import deprecation_getattr
neuron.__getattr__ = deprecation_getattr(__name__, _deprecations)
del deprecation_getattr
