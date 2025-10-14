######################################################################################################
#                                 Auto-generated Metaflow stub file                                  #
# MF version: 2.18.11.1+obcheckpoint(0.2.8);ob(v1)                                                   #
# Generated on 2025-10-13T07:07:26.897420                                                            #
######################################################################################################

from __future__ import annotations

import typing
if typing.TYPE_CHECKING:
    import typing


class SerializationHandler(object, metaclass=type):
    def serialze(self, *args, **kwargs) -> typing.Union[str, bytes]:
        ...
    def deserialize(self, *args, **kwargs) -> typing.Any:
        ...
    ...

