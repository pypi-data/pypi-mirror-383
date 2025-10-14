"""
Medical Data Validators

Validates extracted medical data for correctness and completeness
"""

from typing import Dict, List, Any, Tuple
import re


class MedicalValidator:
    """
    Validate medical extraction results

    Ensures data meets medical standards and competition requirements
    """

    @staticmethod
    def validate_temperature(temp_data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validate temperature data

        Returns:
            (is_valid, list of error messages)
        """
        errors = []

        if temp_data is None:
            return True, []  # null is valid (not mentioned)

        # Check value range
        value = temp_data.get("value")
        if value is not None:
            if not isinstance(value, (int, float)):
                errors.append(f"Temperature value must be numeric, got {type(value)}")
            elif value < 35.0 or value > 42.0:
                errors.append(f"Temperature {value}°C is out of valid range (35-42°C)")

        # Check classification consistency
        classification = temp_data.get("classification")
        if value is not None and classification is not None:
            expected = MedicalValidator._expected_classification(value)
            if classification != expected:
                errors.append(
                    f"Classification '{classification}' doesn't match value {value}°C "
                    f"(expected '{expected}')"
                )

        return len(errors) == 0, errors

    @staticmethod
    def _expected_classification(temp: float) -> str:
        """Get expected classification for temperature value"""
        if temp < 37.0:
            return "normal"
        elif 37.0 <= temp < 37.5:
            return "low-grade"
        elif 37.5 <= temp < 38.0:
            return "fever"
        else:
            return "high-fever"

    @staticmethod
    def validate_symptoms(symptoms: List[Dict[str, Any]]) -> Tuple[bool, List[str]]:
        """
        Validate symptom data

        Returns:
            (is_valid, list of error messages)
        """
        errors = []

        if symptoms is None:
            return True, []  # null is valid

        if not isinstance(symptoms, list):
            errors.append(f"Symptoms must be a list, got {type(symptoms)}")
            return False, errors

        # Validate each symptom
        for i, symptom in enumerate(symptoms):
            if not isinstance(symptom, dict):
                errors.append(f"Symptom {i} must be a dict, got {type(symptom)}")
                continue

            # Required field
            if "symptom" not in symptom:
                errors.append(f"Symptom {i} missing required field 'symptom'")

            # Validate severity if present
            severity = symptom.get("severity")
            if severity is not None:
                valid_severities = ["mild", "moderate", "severe"]
                if severity not in valid_severities:
                    errors.append(
                        f"Symptom {i} has invalid severity '{severity}' "
                        f"(must be one of {valid_severities})"
                    )

            # Validate duration if present
            duration = symptom.get("duration_days")
            if duration is not None:
                if not isinstance(duration, (int, float)) or duration < 0:
                    errors.append(
                        f"Symptom {i} has invalid duration {duration} "
                        f"(must be non-negative number)"
                    )

        return len(errors) == 0, errors

    @staticmethod
    def validate_medications(medications: List[Dict[str, Any]]) -> Tuple[bool, List[str]]:
        """
        Validate medication data

        Returns:
            (is_valid, list of error messages)
        """
        errors = []

        if medications is None:
            return True, []  # null is valid

        if not isinstance(medications, list):
            errors.append(f"Medications must be a list, got {type(medications)}")
            return False, errors

        # Validate each medication
        for i, med in enumerate(medications):
            if not isinstance(med, dict):
                errors.append(f"Medication {i} must be a dict, got {type(med)}")
                continue

            # Required fields
            required_fields = ["name"]
            for field in required_fields:
                if field not in med or med[field] is None:
                    errors.append(f"Medication {i} missing required field '{field}'")

            # Validate dosage
            dosage = med.get("dosage")
            if dosage is not None:
                if not isinstance(dosage, (int, float)) or dosage <= 0:
                    errors.append(
                        f"Medication {i} has invalid dosage {dosage} "
                        f"(must be positive number)"
                    )

            # Validate frequency
            frequency = med.get("frequency")
            if frequency is not None:
                if not isinstance(frequency, (int, float)) or frequency <= 0:
                    errors.append(
                        f"Medication {i} has invalid frequency {frequency} "
                        f"(must be positive number)"
                    )

        return len(errors) == 0, errors

    @staticmethod
    def validate_extraction(extraction: Dict[str, Any]) -> Tuple[bool, Dict[str, List[str]]]:
        """
        Validate complete extraction result

        Returns:
            (is_valid, dict of errors by field)
        """
        all_errors = {}

        # Validate temperature
        temp_valid, temp_errors = MedicalValidator.validate_temperature(
            extraction.get("temperature")
        )
        if temp_errors:
            all_errors["temperature"] = temp_errors

        # Validate symptoms
        symptoms_valid, symptoms_errors = MedicalValidator.validate_symptoms(
            extraction.get("symptoms")
        )
        if symptoms_errors:
            all_errors["symptoms"] = symptoms_errors

        # Validate medications
        meds_valid, meds_errors = MedicalValidator.validate_medications(
            extraction.get("medications")
        )
        if meds_errors:
            all_errors["medications"] = meds_errors

        is_valid = len(all_errors) == 0
        return is_valid, all_errors

    @staticmethod
    def check_completeness(extraction: Dict[str, Any]) -> Dict[str, bool]:
        """
        Check which fields are present in extraction

        Returns dict of {field: is_present}
        """
        return {
            "temperature": extraction.get("temperature") is not None,
            "symptoms": extraction.get("symptoms") is not None,
            "medications": extraction.get("medications") is not None,
        }

    @staticmethod
    def sanitize_extraction(extraction: Dict[str, Any]) -> Dict[str, Any]:
        """
        Clean and sanitize extraction result

        Removes invalid data, fixes common issues
        """
        sanitized = {}

        # Sanitize temperature
        temp = extraction.get("temperature")
        if temp and isinstance(temp, dict):
            value = temp.get("value")
            if value and 35.0 <= value <= 42.0:
                sanitized["temperature"] = {
                    "value": round(value, 1),
                    "classification": MedicalValidator._expected_classification(value),
                    "unit": "celsius"
                }

        # Sanitize symptoms
        symptoms = extraction.get("symptoms")
        if symptoms and isinstance(symptoms, list):
            sanitized_symptoms = []
            for symptom in symptoms:
                if isinstance(symptom, dict) and "symptom" in symptom:
                    sanitized_symptoms.append({
                        "symptom": symptom["symptom"],
                        "severity": symptom.get("severity"),
                        "duration_days": symptom.get("duration_days"),
                        "notes": symptom.get("notes", "")
                    })
            if sanitized_symptoms:
                sanitized["symptoms"] = sanitized_symptoms

        # Sanitize medications
        medications = extraction.get("medications")
        if medications and isinstance(medications, list):
            sanitized_meds = []
            for med in medications:
                if isinstance(med, dict) and "name" in med:
                    sanitized_meds.append({
                        "name": med["name"],
                        "dosage": med.get("dosage"),
                        "dosage_unit": med.get("dosage_unit", "mg"),
                        "frequency": med.get("frequency"),
                        "route": med.get("route", "oral")
                    })
            if sanitized_meds:
                sanitized["medications"] = sanitized_meds

        return sanitized
