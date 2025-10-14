######################################################################################################
#                                 Auto-generated Metaflow stub file                                  #
# MF version: 2.18.11.1+obcheckpoint(0.2.8);ob(v1)                                                   #
# Generated on 2025-10-13T21:06:57.888830                                                            #
######################################################################################################

from __future__ import annotations

import metaflow
import typing
if typing.TYPE_CHECKING:
    import metaflow.exception

from ......exception import MetaflowException as MetaflowException

class LoadingException(metaflow.exception.MetaflowException, metaclass=type):
    def __init__(self, message):
        ...
    ...

class ModelException(metaflow.exception.MetaflowException, metaclass=type):
    def __init__(self, message):
        ...
    ...

