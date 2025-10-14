"""
Medical Data Extractors

Implements extraction logic for medical information from clinical text.
"""

from typing import Dict, List, Optional, Any
import json
import re


class MedicalExtractor:
    """
    Extract structured medical data from clinical text

    Designed for Kaggle medical NLP competitions
    """

    def __init__(self, model: str = "claude-3-5-sonnet-20241022"):
        self.model = model
        from .templates import MedicalTemplates
        self.templates = MedicalTemplates()

    def extract_temperature(self, text: str) -> Dict[str, Any]:
        """
        Extract and classify temperature from clinical text

        Returns:
            {
                "value": float or null,
                "classification": str ("asymptomatic", "low-grade", "fever", "high-fever"),
                "unit": str ("celsius" or "fahrenheit"),
                "confidence": float
            }
        """
        # Extract numeric temperature
        temp_patterns = [
            r'(\d+\.?\d*)\s*°?[cC]',  # 37.5°C or 37.5C
            r'(\d+\.?\d*)\s*度',       # 37.5度
            r'体温[：:]\s*(\d+\.?\d*)', # 体温: 37.5
        ]

        temp_value = None
        for pattern in temp_patterns:
            match = re.search(pattern, text)
            if match:
                temp_value = float(match.group(1))
                break

        # Classify temperature
        if temp_value is None:
            # Check for explicit statements
            if any(word in text for word in ["症状なし", "無症状", "no symptoms"]):
                classification = "asymptomatic"
            else:
                classification = None
        elif temp_value < 37.0:
            classification = "normal"
        elif 37.0 <= temp_value < 37.5:
            classification = "low-grade"
        elif 37.5 <= temp_value < 38.0:
            classification = "fever"
        else:
            classification = "high-fever"

        return {
            "value": temp_value,
            "classification": classification,
            "unit": "celsius" if temp_value else None,
            "confidence": 0.95 if temp_value else 0.5
        }

    def extract_symptoms(self, text: str) -> List[Dict[str, Any]]:
        """
        Extract symptoms from clinical text

        Returns:
            List of {symptom, severity, duration_days, notes}
        """
        # Symptom keywords (Japanese and English)
        symptom_mapping = {
            # Respiratory
            "咳": "cough",
            "cough": "cough",
            "喉の痛み": "sore throat",
            "sore throat": "sore throat",
            "鼻水": "nasal congestion",
            "nasal congestion": "nasal congestion",
            "息切れ": "shortness of breath",
            "shortness of breath": "shortness of breath",

            # Fever-related
            "発熱": "fever",
            "fever": "fever",
            "熱": "fever",
            "悪寒": "chills",
            "chills": "chills",

            # Gastrointestinal
            "吐き気": "nausea",
            "nausea": "nausea",
            "嘔吐": "vomiting",
            "vomiting": "vomiting",
            "下痢": "diarrhea",
            "diarrhea": "diarrhea",
            "腹痛": "abdominal pain",
            "abdominal pain": "abdominal pain",

            # Neurological
            "頭痛": "headache",
            "headache": "headache",
            "めまい": "dizziness",
            "dizziness": "dizziness",

            # Musculoskeletal
            "筋肉痛": "muscle pain",
            "muscle pain": "muscle pain",
            "関節痛": "joint pain",
            "joint pain": "joint pain",
            "倦怠感": "fatigue",
            "fatigue": "fatigue",
        }

        # Check for negative statements
        negative_indicators = ["なし", "否定", "⊖", "no symptoms", "ない"]
        if any(indicator in text for indicator in negative_indicators):
            return []

        # Extract symptoms
        symptoms = []
        for keyword, canonical in symptom_mapping.items():
            if keyword in text.lower():
                # Avoid duplicates
                if canonical not in [s["symptom"] for s in symptoms]:
                    # Check severity
                    severity = None
                    if "軽度" in text or "mild" in text.lower():
                        severity = "mild"
                    elif "中等度" in text or "moderate" in text.lower():
                        severity = "moderate"
                    elif "重度" in text or "severe" in text.lower():
                        severity = "severe"

                    # Check duration
                    duration_match = re.search(r'(\d+)\s*(日|days?)', text)
                    duration = int(duration_match.group(1)) if duration_match else None

                    symptoms.append({
                        "symptom": canonical,
                        "severity": severity,
                        "duration_days": duration,
                        "notes": ""
                    })

        return symptoms if symptoms else None  # null if not mentioned

    def extract_medications(self, text: str) -> List[Dict[str, Any]]:
        """
        Extract medication information

        Returns:
            List of {name, dosage, dosage_unit, frequency, route}
        """
        # Medication name mapping (brand → generic)
        med_mapping = {
            "ロキソニン": "loxoprofen",
            "バファリン": "aspirin",
            "カロナール": "acetaminophen",
            "アスピリン": "aspirin",
        }

        medications = []

        # Pattern: medication name + dosage + frequency
        # Example: "ロキソニン 60mg 1日3回"
        med_pattern = r'([\w\u3040-\u309F\u30A0-\u30FF]+)\s*(\d+\.?\d*)\s*(mg|mL|錠|tablets?)?\s*(?:1日)?(\d+)回?'

        matches = re.finditer(med_pattern, text)
        for match in matches:
            name_raw = match.group(1)
            dosage = float(match.group(2))
            unit = match.group(3) or "mg"
            frequency = int(match.group(4)) if match.group(4) else None

            # Normalize name
            name = med_mapping.get(name_raw, name_raw.lower())

            medications.append({
                "name": name,
                "dosage": dosage,
                "dosage_unit": unit,
                "frequency": frequency,
                "route": "oral"  # default
            })

        return medications if medications else None

    def extract_all(self, text: str) -> Dict[str, Any]:
        """
        Extract all medical information from text

        Returns complete structured data
        """
        return {
            "temperature": self.extract_temperature(text),
            "symptoms": self.extract_symptoms(text),
            "medications": self.extract_medications(text),
            "raw_text": text
        }

    def extract_with_llm(self, text: str, prompt_template: str) -> Dict[str, Any]:
        """
        Extract using LLM with custom prompt

        This method would call Claude/GPT with the prompt template
        For now, returns rule-based extraction
        """
        # In production, this would call the LLM:
        # response = anthropic.completions.create(
        #     model=self.model,
        #     prompt=f"{prompt_template}\n\nText: {text}",
        #     max_tokens=1000
        # )
        # return json.loads(response.completion)

        # For now, use rule-based
        return self.extract_all(text)
