"""
Medical Data Extraction - Basic Example

This example demonstrates basic usage of KagglerBoze medical domain
for extracting temperature, symptoms, and medications from clinical text.

Target accuracy: 96%+
"""

from kaggler.domains.medical import MedicalExtractor, MedicalTemplates

# Initialize extractor with pre-optimized template (96% accuracy)
extractor = MedicalExtractor()

# Example 1: Japanese clinical note
text_ja = """
患者は37.8°Cの発熱があり、咳と頭痛を訴えている。
アセトアミノフェン500mgを処方。
"""

result = extractor.extract_all(text_ja)
print("=== Example 1: Japanese ===")
print(f"Temperature: {result['temperature']['value']}°C ({result['temperature']['classification']})")
print(f"Symptoms: {', '.join(result['symptoms'])}")
print(f"Medications: {', '.join([f\"{m['name']} {m['dosage']}\" for m in result['medications']])}")
print()

# Example 2: English clinical note
text_en = """
Patient presents with fever of 38.2°C, cough, and sore throat.
Prescribed ibuprofen 400mg and rest.
"""

result = extractor.extract_all(text_en)
print("=== Example 2: English ===")
print(f"Temperature: {result['temperature']['value']}°C ({result['temperature']['classification']})")
print(f"Symptoms: {', '.join(result['symptoms'])}")
print(f"Medications: {', '.join([f\"{m['name']} {m['dosage']}\" for m in result['medications']])}")
print()

# Example 3: Edge case - boundary temperature (37.5°C)
text_boundary = "患者は37.5°Cちょうどの体温。"

result = extractor.extract_temperature(text_boundary)
print("=== Example 3: Boundary Case (37.5°C) ===")
print(f"Temperature: {result['value']}°C ({result['classification']})")
print(f"Expected: 'fever' (発熱)")
print()

# Example 4: Batch processing
texts = [
    "37.0°Cの微熱",
    "38.5°Cの高熱",
    "36.5°Cで平熱",
    "39.2°Cの発熱と悪寒",
]

print("=== Example 4: Batch Processing ===")
for text in texts:
    result = extractor.extract_temperature(text)
    print(f"{text:20s} → {result['classification']}")
