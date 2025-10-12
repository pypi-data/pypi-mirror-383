from orionis.services.environment.contracts.env import IEnv
from orionis.services.environment.core.dot_env import DotEnv
from typing import Any, Dict

class Env(IEnv):

    @staticmethod
    def get(key: str, default: Any = None) -> Any:
        """
        Retrieve the value of an environment variable by its key.

        Parameters
        ----------
        key : str
            The environment variable name to look up.
        default : Any, optional
            Value to return if the key is not found. Defaults to None.

        Returns
        -------
        Any
            The value of the environment variable if present, otherwise `default`.
        """

        # Create a new DotEnv instance to access environment variables
        dotenv = DotEnv()

        # Retrieve the value for the given key, or return default if not found
        return dotenv.get(key, default)

    @staticmethod
    def set(key: str, value: str, type_hint: str = None) -> bool:
        """
        Set or update an environment variable in the .env file.

        Parameters
        ----------
        key : str
            The environment variable name to set.
        value : str
            The value to assign to the environment variable.
        type_hint : str, optional
            Optional type hint for the variable (e.g., 'str', 'int'). Defaults to None.

        Returns
        -------
        bool
            True if the variable was set successfully, False otherwise.
        """

        # Create a new DotEnv instance to modify environment variables
        dotenv = DotEnv()

        # Set the environment variable with the specified key, value, and optional type hint
        return dotenv.set(key, value, type_hint)

    @staticmethod
    def unset(key: str) -> bool:
        """
        Remove an environment variable from the .env file.

        Parameters
        ----------
        key : str
            The environment variable name to remove.

        Returns
        -------
        bool
            True if the variable was removed successfully, False otherwise.
        """

        # Create a new DotEnv instance to remove environment variables
        dotenv = DotEnv()

        # Remove the environment variable with the specified key
        return dotenv.unset(key)

    @staticmethod
    def all() -> Dict[str, Any]:
        """
        Get all environment variables as a dictionary.

        Returns
        -------
        dict of str to Any
            Dictionary containing all environment variables loaded by DotEnv.
        """

        # Create a new DotEnv instance to access all environment variables
        dotenv = DotEnv()

        # Return all environment variables as a dictionary
        return dotenv.all()

    @staticmethod
    def isVirtual() -> bool:
        """
        Determine if the current Python interpreter is running inside a virtual environment.

        Returns
        -------
        bool
            True if running inside a virtual environment, False otherwise.

        Notes
        -----
        This method checks for the presence of common virtual environment indicators:
        - The 'VIRTUAL_ENV' environment variable.
        - The presence of 'pyvenv.cfg' in the parent directories of the Python executable.
        - Differences between sys.prefix and sys.base_prefix (for venv and virtualenv).

        This approach works for most virtual environment tools, including venv and virtualenv.
        """
        import sys
        import os
        from pathlib import Path

        # Check for 'VIRTUAL_ENV' environment variable (set by virtualenv)
        if 'VIRTUAL_ENV' in os.environ:
            return True

        # Check for 'pyvenv.cfg' in the executable's parent directories (set by venv)
        executable = Path(sys.executable).resolve()
        for parent in executable.parents:
            if (parent / 'pyvenv.cfg').exists():
                return True

        # Compare sys.prefix and sys.base_prefix (works for venv and virtualenv)
        if hasattr(sys, 'base_prefix') and sys.prefix != sys.base_prefix:
            return True

        return False