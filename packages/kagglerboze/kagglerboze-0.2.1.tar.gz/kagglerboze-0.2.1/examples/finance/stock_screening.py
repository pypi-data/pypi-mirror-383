"""
Stock Screening - Basic Example

This example demonstrates stock valuation analysis using KagglerBoze finance domain.
Achieves 92% accuracy on stock screening tasks.
"""

from kaggler.domains.finance import StockAnalyzer

# Initialize analyzer with pre-optimized template (92% accuracy)
analyzer = StockAnalyzer()

# Example 1: Japanese stock (Buy signal)
text_ja = "トヨタ自動車: PER 12.3, PBR 0.9, ROE 13.2%, 配当3.2%"

result = analyzer.analyze(text_ja)
print("=== Example 1: Toyota (Buy Signal) ===")
print(f"Ticker: {result['ticker']}")
print(f"Recommendation: {result['recommendation'].upper()}")
print(f"Confidence: {result['confidence']:.1%}")
print("Reasons:")
for reason in result['reasons']:
    print(f"  - {reason}")
print()

# Example 2: US stock (Hold/Sell signal)
text_en = "Apple Inc: P/E 28.5, P/B 45.2, ROE 147%, Dividend 0.5%"

result = analyzer.analyze(text_en)
print("=== Example 2: Apple (Growth Stock) ===")
print(f"Ticker: {result['ticker']}")
print(f"Recommendation: {result['recommendation'].upper()}")
print(f"Confidence: {result['confidence']:.1%}")
print("Reasons:")
for reason in result['reasons']:
    print(f"  - {reason}")
print()

# Example 3: Batch screening (multiple stocks)
stocks = [
    ("トヨタ", "PER 12.3, PBR 0.9, ROE 13%, 配当3.2%"),
    ("ソニー", "PER 18.5, PBR 2.8, ROE 16%, 配当0.8%"),
    ("三菱UFJ", "PER 8.2, PBR 0.6, ROE 7%, 配当4.5%"),
    ("キーエンス", "PER 45.8, PBR 12.3, ROE 28%, 配当0.9%"),
]

print("=== Example 3: Batch Screening ===")
print(f"{'Stock':<12} {'Rec':^6} {'Conf':>6} {'Reasons'}")
print("-" * 70)

for name, metrics in stocks:
    text = f"{name}: {metrics}"
    result = analyzer.analyze(text)
    reasons_summary = ", ".join(result['reasons'][:2])  # First 2 reasons
    print(f"{name:<12} {result['recommendation']:^6} {result['confidence']:>5.0%} {reasons_summary[:40]}")

print()

# Example 4: Value investing filter (Buy signals only)
print("=== Example 4: Value Investing Filter (Buy Signals) ===")
buy_candidates = []

for name, metrics in stocks:
    text = f"{name}: {metrics}"
    result = analyzer.analyze(text)
    if result['recommendation'] == 'buy' and result['confidence'] > 0.9:
        buy_candidates.append({
            'stock': name,
            'confidence': result['confidence'],
            'reasons': result['reasons']
        })

# Sort by confidence
buy_candidates.sort(key=lambda x: x['confidence'], reverse=True)

for candidate in buy_candidates:
    print(f"\n{candidate['stock']} (Confidence: {candidate['confidence']:.1%})")
    for reason in candidate['reasons']:
        print(f"  ✓ {reason}")
