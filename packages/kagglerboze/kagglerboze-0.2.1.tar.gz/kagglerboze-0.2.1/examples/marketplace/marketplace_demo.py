"""Demo script for the Kaggler Prompt Marketplace.

This script demonstrates the main features of the marketplace:
1. Database initialization
2. Creating users
3. Submitting prompts
4. Rating and reviewing prompts
5. Searching and filtering
6. Downloading prompts
7. Viewing leaderboard

To run this demo:
    python examples/marketplace/marketplace_demo.py
"""

import asyncio
from datetime import datetime
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from kaggler.marketplace import (
    db_manager,
    User,
    Prompt,
    Rating,
    Review,
    Download,
    Benchmark,
)


def print_section(title: str):
    """Print section header."""
    print("\n" + "=" * 80)
    print(f" {title}")
    print("=" * 80)


def demo_database_initialization():
    """Demo: Initialize database and create tables."""
    print_section("1. Database Initialization")

    print("Creating database tables...")
    db_manager.create_all()
    print("✓ Database tables created successfully")

    # Check connection
    if db_manager.check_connection():
        print("✓ Database connection verified")
    else:
        print("✗ Database connection failed")
        return False

    return True


def demo_create_users():
    """Demo: Create sample users."""
    print_section("2. Creating Users")

    with db_manager.session_scope() as session:
        # Create users
        users = [
            User(
                username="alice_ml",
                email="alice@example.com",
                oauth_provider="github",
                oauth_id="github_12345",
            ),
            User(
                username="bob_kaggler",
                email="bob@example.com",
                oauth_provider="google",
                oauth_id="google_67890",
            ),
            User(
                username="charlie_ai",
                email="charlie@example.com",
                oauth_provider="github",
                oauth_id="github_11111",
            ),
        ]

        for user in users:
            session.add(user)
            print(f"✓ Created user: {user.username} ({user.email})")

    print(f"\n✓ Total users created: {len(users)}")


def demo_submit_prompts():
    """Demo: Submit sample prompts."""
    print_section("3. Submitting Prompts")

    with db_manager.session_scope() as session:
        users = session.query(User).all()

        prompts_data = [
            {
                "user_id": users[0].id,
                "title": "Image Classification with Vision Transformer",
                "content": "You are an expert in computer vision. Analyze this image and classify it into one of the following categories: [categories]. Provide confidence scores and explain your reasoning.",
                "description": "High-accuracy prompt for image classification tasks using vision transformers",
                "domain": "vision",
                "task": "classification",
                "accuracy": 0.94,
            },
            {
                "user_id": users[1].id,
                "title": "Time Series Forecasting for Stock Prices",
                "content": "You are a financial analyst with expertise in time series forecasting. Given the historical stock price data: [data], predict the next 30 days. Consider trends, seasonality, and market conditions.",
                "description": "Accurate time series forecasting for financial data",
                "domain": "tabular",
                "task": "regression",
                "accuracy": 0.87,
            },
            {
                "user_id": users[0].id,
                "title": "Sentiment Analysis for Product Reviews",
                "content": "You are a sentiment analysis expert. Analyze the following product review and classify the sentiment as positive, negative, or neutral. Provide reasoning and key phrases that support your classification.",
                "description": "Multi-class sentiment analysis with explanation",
                "domain": "nlp",
                "task": "classification",
                "accuracy": 0.91,
            },
            {
                "user_id": users[2].id,
                "title": "Tabular Data Regression with Feature Engineering",
                "content": "You are a data scientist specializing in tabular data. Given this dataset: [data], perform regression to predict [target]. Suggest feature engineering steps and explain your approach.",
                "description": "Regression prompt with automatic feature engineering suggestions",
                "domain": "tabular",
                "task": "regression",
                "accuracy": 0.89,
            },
            {
                "user_id": users[1].id,
                "title": "Named Entity Recognition for Medical Text",
                "content": "You are a medical NLP expert. Extract named entities (diseases, medications, procedures) from this medical text: [text]. Provide entity types and confidence scores.",
                "description": "Medical NER with high precision",
                "domain": "nlp",
                "task": "ner",
                "accuracy": 0.93,
            },
        ]

        prompts = []
        for data in prompts_data:
            prompt = Prompt(**data)
            session.add(prompt)
            prompts.append(prompt)
            print(f"✓ Created prompt: {data['title']}")

        session.flush()  # Get IDs

        # Add benchmarks
        print("\nAdding benchmarks...")
        benchmarks_data = [
            {"prompt_id": prompts[0].id, "metric": "accuracy", "score": 0.94, "dataset": "ImageNet-1K"},
            {"prompt_id": prompts[0].id, "metric": "f1_score", "score": 0.93, "dataset": "ImageNet-1K"},
            {"prompt_id": prompts[1].id, "metric": "mse", "score": 12.3, "dataset": "S&P500"},
            {"prompt_id": prompts[2].id, "metric": "accuracy", "score": 0.91, "dataset": "Amazon Reviews"},
            {"prompt_id": prompts[3].id, "metric": "r2_score", "score": 0.89, "dataset": "Housing Prices"},
            {"prompt_id": prompts[4].id, "metric": "f1_score", "score": 0.93, "dataset": "Medical Records"},
        ]

        for data in benchmarks_data:
            benchmark = Benchmark(**data)
            session.add(benchmark)

        print(f"✓ Added {len(benchmarks_data)} benchmarks")

    print(f"\n✓ Total prompts created: {len(prompts_data)}")


def demo_rate_prompts():
    """Demo: Rate prompts."""
    print_section("4. Rating Prompts")

    with db_manager.session_scope() as session:
        users = session.query(User).all()
        prompts = session.query(Prompt).all()

        ratings_data = [
            {"prompt_id": prompts[0].id, "user_id": users[1].id, "rating": 5},
            {"prompt_id": prompts[0].id, "user_id": users[2].id, "rating": 5},
            {"prompt_id": prompts[1].id, "user_id": users[0].id, "rating": 4},
            {"prompt_id": prompts[1].id, "user_id": users[2].id, "rating": 4},
            {"prompt_id": prompts[2].id, "user_id": users[1].id, "rating": 5},
            {"prompt_id": prompts[2].id, "user_id": users[2].id, "rating": 4},
            {"prompt_id": prompts[3].id, "user_id": users[0].id, "rating": 4},
            {"prompt_id": prompts[3].id, "user_id": users[1].id, "rating": 5},
            {"prompt_id": prompts[4].id, "user_id": users[0].id, "rating": 5},
            {"prompt_id": prompts[4].id, "user_id": users[2].id, "rating": 5},
        ]

        for data in ratings_data:
            rating = Rating(**data)
            session.add(rating)
            prompt = session.query(Prompt).filter(Prompt.id == data["prompt_id"]).first()
            user = session.query(User).filter(User.id == data["user_id"]).first()
            print(f"✓ {user.username} rated '{prompt.title[:40]}...' with {data['rating']} stars")

    print(f"\n✓ Total ratings added: {len(ratings_data)}")


def demo_review_prompts():
    """Demo: Add reviews to prompts."""
    print_section("5. Adding Reviews")

    with db_manager.session_scope() as session:
        users = session.query(User).all()
        prompts = session.query(Prompt).all()

        reviews_data = [
            {
                "prompt_id": prompts[0].id,
                "user_id": users[1].id,
                "content": "Excellent prompt for image classification! Works great with ViT models. Achieved 94% accuracy on my dataset.",
            },
            {
                "prompt_id": prompts[1].id,
                "user_id": users[0].id,
                "content": "Good starting point for time series forecasting. Had to tweak it a bit for crypto data, but overall solid.",
            },
            {
                "prompt_id": prompts[2].id,
                "user_id": users[2].id,
                "content": "Very accurate sentiment analysis. The explanation feature is particularly useful for understanding edge cases.",
            },
            {
                "prompt_id": prompts[4].id,
                "user_id": users[0].id,
                "content": "Outstanding medical NER prompt! High precision on rare entities. Highly recommended for healthcare applications.",
            },
        ]

        for data in reviews_data:
            review = Review(**data)
            session.add(review)
            user = session.query(User).filter(User.id == data["user_id"]).first()
            prompt = session.query(Prompt).filter(Prompt.id == data["prompt_id"]).first()
            print(f"✓ {user.username} reviewed '{prompt.title[:40]}...'")

    print(f"\n✓ Total reviews added: {len(reviews_data)}")


def demo_download_prompts():
    """Demo: Track prompt downloads."""
    print_section("6. Downloading Prompts")

    with db_manager.session_scope() as session:
        users = session.query(User).all()
        prompts = session.query(Prompt).all()

        downloads_data = [
            {"prompt_id": prompts[0].id, "user_id": users[1].id},
            {"prompt_id": prompts[0].id, "user_id": users[2].id},
            {"prompt_id": prompts[1].id, "user_id": users[0].id},
            {"prompt_id": prompts[1].id, "user_id": users[2].id},
            {"prompt_id": prompts[2].id, "user_id": users[0].id},
            {"prompt_id": prompts[2].id, "user_id": users[1].id},
            {"prompt_id": prompts[3].id, "user_id": users[0].id},
            {"prompt_id": prompts[4].id, "user_id": users[0].id},
            {"prompt_id": prompts[4].id, "user_id": users[1].id},
            {"prompt_id": prompts[4].id, "user_id": users[2].id},
        ]

        for data in downloads_data:
            download = Download(**data)
            session.add(download)

        print(f"✓ Tracked {len(downloads_data)} downloads")


def demo_search_and_filter():
    """Demo: Search and filter prompts."""
    print_section("7. Searching and Filtering")

    with db_manager.session_scope() as session:
        # Search by domain
        print("\nPrompts in 'vision' domain:")
        vision_prompts = session.query(Prompt).filter(Prompt.domain == "vision").all()
        for prompt in vision_prompts:
            print(f"  • {prompt.title} (accuracy: {prompt.accuracy})")

        # Search by task
        print("\nPrompts for 'classification' task:")
        classification_prompts = session.query(Prompt).filter(Prompt.task == "classification").all()
        for prompt in classification_prompts:
            print(f"  • {prompt.title} (domain: {prompt.domain})")

        # Search by minimum accuracy
        print("\nHigh-accuracy prompts (>0.90):")
        high_acc_prompts = session.query(Prompt).filter(Prompt.accuracy >= 0.90).all()
        for prompt in high_acc_prompts:
            print(f"  • {prompt.title} (accuracy: {prompt.accuracy})")


def demo_leaderboard():
    """Demo: Display leaderboard."""
    print_section("8. Leaderboard")

    with db_manager.session_scope() as session:
        from sqlalchemy import func

        # Get prompts with average ratings
        results = (
            session.query(
                Prompt,
                func.avg(Rating.rating).label("avg_rating"),
                func.count(Rating.id).label("rating_count"),
                func.count(Download.id).label("download_count"),
            )
            .outerjoin(Rating, Prompt.id == Rating.prompt_id)
            .outerjoin(Download, Prompt.id == Download.prompt_id)
            .group_by(Prompt.id)
            .order_by(func.avg(Rating.rating).desc())
            .all()
        )

        print("\nTop Rated Prompts:")
        print(f"{'Rank':<6}{'Title':<45}{'Avg Rating':<12}{'Downloads':<12}{'Domain':<10}")
        print("-" * 85)

        for idx, (prompt, avg_rating, rating_count, download_count) in enumerate(results, 1):
            avg_rating_str = f"{avg_rating:.2f} ({rating_count})" if avg_rating else "N/A"
            download_str = f"{download_count or 0}"
            print(f"{idx:<6}{prompt.title[:43]:<45}{avg_rating_str:<12}{download_str:<12}{prompt.domain:<10}")


def demo_statistics():
    """Demo: Display statistics."""
    print_section("9. Statistics")

    with db_manager.session_scope() as session:
        total_users = session.query(User).count()
        total_prompts = session.query(Prompt).count()
        total_ratings = session.query(Rating).count()
        total_reviews = session.query(Review).count()
        total_downloads = session.query(Download).count()

        print(f"\nMarketplace Statistics:")
        print(f"  • Total Users:     {total_users}")
        print(f"  • Total Prompts:   {total_prompts}")
        print(f"  • Total Ratings:   {total_ratings}")
        print(f"  • Total Reviews:   {total_reviews}")
        print(f"  • Total Downloads: {total_downloads}")

        # Average rating
        from sqlalchemy import func
        avg_rating = session.query(func.avg(Rating.rating)).scalar()
        print(f"  • Average Rating:  {avg_rating:.2f}/5.0")


def main():
    """Run all demo functions."""
    print("\n" + "=" * 80)
    print(" Kaggler Prompt Marketplace - Demo")
    print("=" * 80)

    try:
        # Run demos
        if not demo_database_initialization():
            return

        demo_create_users()
        demo_submit_prompts()
        demo_rate_prompts()
        demo_review_prompts()
        demo_download_prompts()
        demo_search_and_filter()
        demo_leaderboard()
        demo_statistics()

        print("\n" + "=" * 80)
        print(" Demo completed successfully!")
        print("=" * 80)
        print("\nYou can now:")
        print("  1. Start the API server: uvicorn kaggler.marketplace.api:app --reload")
        print("  2. View API docs: http://localhost:8000/docs")
        print("  3. Database file: ./marketplace.db")
        print()

    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
