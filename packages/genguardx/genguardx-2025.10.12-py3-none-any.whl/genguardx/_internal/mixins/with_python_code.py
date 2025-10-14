from __future__ import annotations

import typing as t

from genguardx._internal.util import utils
from genguardx._internal.util.networking import api


class WithPythonCode:
    """
    Represents a class to access the Note Attachemnts which are tagged to an object.
    """

    def __call__(self, *args, **kwargs) -> t.Any:  # noqa: ANN401 -- Return type can vary based on the GF definition
        """
        Used to execute the definition mentioned while defining the object

        :param *args:      The parameters defined in the object given as args
        :param **kwargs:   The parameters defined in object given as kwargs

        :returns:          The result when the definition of the object
                           is executed with the necessary params
        """
        py_func = self.get_python_function()
        return py_func(*args, **kwargs)

    def get_python_function(self) -> t.Callable:
        """
        Convert the object to a python function that can be used with python.

        :returns:               A python function which takes in the same arguments as object
                                and returns the same value as the object
        """
        code_body = api.response(utils.ujoin(self._LIST_URL, f"{self.id}/export_python"), out="text")
        scope = {}
        utils.do_exec(code_body, scope)
        return scope[self.alias]
