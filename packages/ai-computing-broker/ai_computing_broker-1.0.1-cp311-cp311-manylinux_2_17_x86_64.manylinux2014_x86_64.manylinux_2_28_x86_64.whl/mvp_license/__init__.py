# Copyright 2025 Fujitsu Research of America, Inc.
#
# This software is licensed under an End User License Agreement (EULA) by Fujitsu
# Research of America, Inc. You are not allowed to use, copy, modify, or distribute
# this software and its documentation without express permission from Fujitsu Research
# of America, Inc. Please refer to the full EULA provided with this software for
# detailed information on permitted uses and restrictions.
#
# The software is provided "as is", without warranty of any kind, express or implied,
# including but not limited to the warranties of merchantability, fitness for a
# particular purpose and noninfringement. In no event shall Fujitsu Research of America,
# Inc. be liable for any claim, damages or other liability, whether in an action of
# contract, tort or otherwise, arising from, out of or in connection with the software
# or the use or other dealings in the software.


from .exceptions import LicenseError, LicenseGenerationError, LicenseValidationError
from .generator import LicenseGenerator
from .validator import LicenseValidator

__all__ = ["LicenseGenerator", "LicenseValidator", "LicenseError", "LicenseValidationError", "LicenseGenerationError"]
