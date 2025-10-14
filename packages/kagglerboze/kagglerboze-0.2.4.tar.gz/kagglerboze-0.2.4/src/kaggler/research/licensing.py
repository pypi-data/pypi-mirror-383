"""
License Management

Manages dataset licenses, enforces terms, and validates compliance.
"""

from typing import Dict, List, Optional, Set
from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class LicenseType(str, Enum):
    """Standard license types"""
    CC0 = "CC0-1.0"
    CC_BY = "CC-BY-4.0"
    CC_BY_SA = "CC-BY-SA-4.0"
    CC_BY_NC = "CC-BY-NC-4.0"
    CC_BY_NC_SA = "CC-BY-NC-SA-4.0"
    MIT = "MIT"
    APACHE_2 = "Apache-2.0"
    GPL_3 = "GPL-3.0"
    PROPRIETARY = "Proprietary"
    CUSTOM = "Custom"


@dataclass
class License:
    """
    License definition

    Attributes:
        license_id: License identifier
        license_type: Type of license
        name: License name
        description: License description
        allows_commercial: Commercial use allowed
        allows_modification: Modifications allowed
        allows_distribution: Distribution allowed
        requires_attribution: Attribution required
        requires_share_alike: Share-alike required
        url: URL to license text
        custom_terms: Custom license terms
    """
    license_id: str
    license_type: LicenseType
    name: str
    description: str
    allows_commercial: bool = True
    allows_modification: bool = True
    allows_distribution: bool = True
    requires_attribution: bool = False
    requires_share_alike: bool = False
    url: Optional[str] = None
    custom_terms: Optional[str] = None

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            "license_id": self.license_id,
            "license_type": self.license_type.value,
            "name": self.name,
            "description": self.description,
            "allows_commercial": self.allows_commercial,
            "allows_modification": self.allows_modification,
            "allows_distribution": self.allows_distribution,
            "requires_attribution": self.requires_attribution,
            "requires_share_alike": self.requires_share_alike,
            "url": self.url,
            "custom_terms": self.custom_terms
        }


class LicenseManager:
    """
    Manager for dataset licenses

    Handles license assignment, validation, and compliance checking.
    """

    # Standard license definitions
    STANDARD_LICENSES = {
        LicenseType.CC0: License(
            license_id="cc0",
            license_type=LicenseType.CC0,
            name="Creative Commons Zero v1.0 Universal",
            description="Public domain dedication",
            allows_commercial=True,
            allows_modification=True,
            allows_distribution=True,
            requires_attribution=False,
            url="https://creativecommons.org/publicdomain/zero/1.0/"
        ),
        LicenseType.CC_BY: License(
            license_id="cc-by",
            license_type=LicenseType.CC_BY,
            name="Creative Commons Attribution 4.0",
            description="Permits almost any use subject to attribution",
            allows_commercial=True,
            allows_modification=True,
            allows_distribution=True,
            requires_attribution=True,
            url="https://creativecommons.org/licenses/by/4.0/"
        ),
        LicenseType.CC_BY_SA: License(
            license_id="cc-by-sa",
            license_type=LicenseType.CC_BY_SA,
            name="Creative Commons Attribution-ShareAlike 4.0",
            description="Requires attribution and share-alike",
            allows_commercial=True,
            allows_modification=True,
            allows_distribution=True,
            requires_attribution=True,
            requires_share_alike=True,
            url="https://creativecommons.org/licenses/by-sa/4.0/"
        ),
        LicenseType.CC_BY_NC: License(
            license_id="cc-by-nc",
            license_type=LicenseType.CC_BY_NC,
            name="Creative Commons Attribution-NonCommercial 4.0",
            description="Non-commercial use with attribution",
            allows_commercial=False,
            allows_modification=True,
            allows_distribution=True,
            requires_attribution=True,
            url="https://creativecommons.org/licenses/by-nc/4.0/"
        ),
        LicenseType.MIT: License(
            license_id="mit",
            license_type=LicenseType.MIT,
            name="MIT License",
            description="Permissive license with attribution",
            allows_commercial=True,
            allows_modification=True,
            allows_distribution=True,
            requires_attribution=True,
            url="https://opensource.org/licenses/MIT"
        )
    }

    def __init__(self):
        self._dataset_licenses: Dict[str, License] = {}
        self._custom_licenses: Dict[str, License] = {}

    def assign_license(self, dataset_id: str, license_type: LicenseType) -> License:
        """Assign standard license to dataset"""
        license_obj = self.STANDARD_LICENSES.get(license_type)
        if not license_obj:
            raise ValueError(f"Unknown license type: {license_type}")

        self._dataset_licenses[dataset_id] = license_obj
        return license_obj

    def assign_custom_license(
        self,
        dataset_id: str,
        name: str,
        description: str,
        allows_commercial: bool = False,
        allows_modification: bool = False,
        allows_distribution: bool = False,
        requires_attribution: bool = True,
        custom_terms: Optional[str] = None
    ) -> License:
        """Assign custom license to dataset"""
        import hashlib

        license_id = hashlib.md5(f"{dataset_id}_{name}".encode()).hexdigest()[:16]

        license_obj = License(
            license_id=license_id,
            license_type=LicenseType.CUSTOM,
            name=name,
            description=description,
            allows_commercial=allows_commercial,
            allows_modification=allows_modification,
            allows_distribution=allows_distribution,
            requires_attribution=requires_attribution,
            custom_terms=custom_terms
        )

        self._custom_licenses[license_id] = license_obj
        self._dataset_licenses[dataset_id] = license_obj
        return license_obj

    def get_license(self, dataset_id: str) -> Optional[License]:
        """Get license for dataset"""
        return self._dataset_licenses.get(dataset_id)

    def check_commercial_use(self, dataset_id: str) -> bool:
        """Check if commercial use is allowed"""
        license_obj = self._dataset_licenses.get(dataset_id)
        return license_obj.allows_commercial if license_obj else False

    def check_modification(self, dataset_id: str) -> bool:
        """Check if modification is allowed"""
        license_obj = self._dataset_licenses.get(dataset_id)
        return license_obj.allows_modification if license_obj else False

    def check_distribution(self, dataset_id: str) -> bool:
        """Check if distribution is allowed"""
        license_obj = self._dataset_licenses.get(dataset_id)
        return license_obj.allows_distribution if license_obj else False

    def validate_usage(
        self,
        dataset_id: str,
        commercial: bool = False,
        modification: bool = False,
        distribution: bool = False
    ) -> Dict[str, bool]:
        """
        Validate if usage is allowed under license

        Args:
            dataset_id: Dataset identifier
            commercial: Is this commercial use
            modification: Will data be modified
            distribution: Will data be distributed

        Returns:
            Dictionary with validation results
        """
        license_obj = self._dataset_licenses.get(dataset_id)
        if not license_obj:
            return {
                "valid": False,
                "reason": "No license assigned"
            }

        violations = []

        if commercial and not license_obj.allows_commercial:
            violations.append("Commercial use not allowed")

        if modification and not license_obj.allows_modification:
            violations.append("Modification not allowed")

        if distribution and not license_obj.allows_distribution:
            violations.append("Distribution not allowed")

        return {
            "valid": len(violations) == 0,
            "violations": violations,
            "requires_attribution": license_obj.requires_attribution,
            "requires_share_alike": license_obj.requires_share_alike
        }

    def generate_attribution_text(self, dataset_id: str, dataset_name: str) -> str:
        """Generate attribution text for dataset"""
        license_obj = self._dataset_licenses.get(dataset_id)
        if not license_obj:
            return ""

        if not license_obj.requires_attribution:
            return "No attribution required"

        return (
            f"This work uses data from '{dataset_name}' "
            f"licensed under {license_obj.name}. "
            f"See {license_obj.url if license_obj.url else 'license documentation'} "
            f"for details."
        )

    def list_compatible_licenses(
        self,
        commercial: bool = False,
        modification: bool = False
    ) -> List[License]:
        """
        List licenses compatible with usage requirements

        Args:
            commercial: Need commercial use
            modification: Need modification rights

        Returns:
            List of compatible licenses
        """
        compatible = []

        for license_obj in self.STANDARD_LICENSES.values():
            if commercial and not license_obj.allows_commercial:
                continue
            if modification and not license_obj.allows_modification:
                continue
            compatible.append(license_obj)

        return compatible

    def get_license_summary(self, dataset_id: str) -> Optional[Dict]:
        """Get license summary for dataset"""
        license_obj = self._dataset_licenses.get(dataset_id)
        if not license_obj:
            return None

        return {
            "name": license_obj.name,
            "type": license_obj.license_type.value,
            "description": license_obj.description,
            "permissions": {
                "commercial_use": license_obj.allows_commercial,
                "modification": license_obj.allows_modification,
                "distribution": license_obj.allows_distribution
            },
            "requirements": {
                "attribution": license_obj.requires_attribution,
                "share_alike": license_obj.requires_share_alike
            },
            "url": license_obj.url
        }
