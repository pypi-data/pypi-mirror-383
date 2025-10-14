"""
Research Partnership Demo

Demonstrates the Research Partnerships infrastructure with a complete workflow:
1. Register a research dataset
2. Create a benchmark
3. Submit results
4. View leaderboard
5. Create collaboration workspace
6. Track citations
"""

from datetime import datetime
from kaggler.research import (
    DatasetHub,
    DatasetType,
    AccessLevel,
    BenchmarkManager,
    BenchmarkTask,
    MetricType,
    CollaborationWorkspace,
    WorkspaceManager,
    WorkspaceRole,
    CitationTracker,
    ExperimentTracker,
    ExperimentStatus,
    PrivacyControl,
    PrivacyLevel,
    ComplianceRegulation,
    LicenseManager,
    LicenseType,
    EthicsReviewManager,
    EthicsCategory,
    EthicsStatus
)


def print_section(title: str):
    """Print section header"""
    print(f"\n{'=' * 60}")
    print(f"{title:^60}")
    print(f"{'=' * 60}\n")


def demo_dataset_registration():
    """Demo: Register a research dataset"""
    print_section("1. Dataset Registration")

    # Initialize dataset hub
    hub = DatasetHub()

    # Register a medical imaging dataset
    print("Registering medical imaging dataset...")
    dataset = hub.register_dataset(
        name="COVID-19 Chest X-Ray Dataset",
        description="Collection of chest X-ray images for COVID-19 detection research",
        dataset_type=DatasetType.IMAGE,
        owner_id="researcher_001",
        institution="Stanford University",
        access_level=AccessLevel.INSTITUTION_ONLY,
        license="CC-BY-NC-4.0",
        tags=["medical", "covid-19", "chest-xray", "diagnostic"],
        num_records=10000,
        size_bytes=5_000_000_000  # 5GB
    )

    print(f"✓ Dataset registered successfully!")
    print(f"  ID: {dataset.id}")
    print(f"  Name: {dataset.name}")
    print(f"  Type: {dataset.dataset_type.value}")
    print(f"  License: {dataset.license}")
    print(f"  Records: {dataset.num_records:,}")
    print(f"  Size: {dataset.size_bytes / 1_000_000_000:.2f} GB")

    return hub, dataset.id


def demo_benchmark_creation(hub, dataset_id):
    """Demo: Create and submit to benchmark"""
    print_section("2. Benchmark Creation & Submission")

    # Initialize benchmark manager
    benchmark_mgr = BenchmarkManager()

    # Create benchmark
    print("Creating COVID-19 detection benchmark...")
    benchmark = benchmark_mgr.create_benchmark(
        name="COVID-19 Detection Challenge",
        description="Binary classification task for COVID-19 detection from chest X-rays",
        dataset_id=dataset_id,
        task=BenchmarkTask.CLASSIFICATION,
        metric="accuracy",
        metric_type=MetricType.HIGHER_IS_BETTER,
        baseline_score=0.85,
        created_by="researcher_001",
        evaluation_protocol="5-fold cross-validation with stratified splits"
    )

    print(f"✓ Benchmark created!")
    print(f"  ID: {benchmark.benchmark_id}")
    print(f"  Task: {benchmark.task.value}")
    print(f"  Metric: {benchmark.metric}")
    print(f"  Baseline: {benchmark.baseline_score:.3f}")

    # Submit results
    print("\nSubmitting results to benchmark...")
    submissions = [
        ("ResNet50", 0.921, "researcher_002", "MIT"),
        ("EfficientNet-B7", 0.935, "researcher_003", "Stanford"),
        ("Vision Transformer", 0.948, "researcher_004", "Oxford"),
        ("Custom CNN", 0.912, "researcher_005", "Cambridge"),
    ]

    for method, score, user_id, institution in submissions:
        result = benchmark_mgr.submit_result(
            benchmark_id=benchmark.benchmark_id,
            user_id=user_id,
            institution=institution,
            score=score,
            method=method,
            description=f"{method} model trained for 100 epochs",
            code_url=f"https://github.com/{institution.lower()}/{method.lower()}",
            paper_url=f"https://arxiv.org/abs/2024.{user_id}"
        )
        print(f"  ✓ {method}: {score:.3f} (by {institution})")

    return benchmark_mgr, benchmark.benchmark_id


def demo_leaderboard(benchmark_mgr, benchmark_id):
    """Demo: View benchmark leaderboard"""
    print_section("3. Benchmark Leaderboard")

    # Get leaderboard
    leaderboard = benchmark_mgr.get_leaderboard(benchmark_id, top_k=5)

    print("Top 5 Submissions:")
    print(f"{'Rank':<6}{'Method':<25}{'Institution':<20}{'Score':<10}")
    print("-" * 60)

    for rank, entry in enumerate(leaderboard, 1):
        print(f"{rank:<6}{entry['method']:<25}{entry['institution']:<20}{entry['score']:<10.3f}")

    # Get statistics
    stats = benchmark_mgr.get_benchmark_statistics(benchmark_id)
    print(f"\nBenchmark Statistics:")
    print(f"  Total submissions: {stats['total_submissions']}")
    print(f"  Unique institutions: {stats['unique_institutions']}")
    print(f"  Best score: {stats['best_score']:.3f}")
    print(f"  Mean score: {stats['mean_score']:.3f}")


def demo_collaboration_workspace():
    """Demo: Create collaboration workspace"""
    print_section("4. Collaboration Workspace")

    # Initialize workspace manager
    workspace_mgr = WorkspaceManager()

    # Create workspace
    print("Creating multi-institutional collaboration workspace...")
    workspace = workspace_mgr.create_workspace(
        name="Global COVID-19 Research Consortium",
        description="Collaborative workspace for COVID-19 detection research",
        created_by="researcher_001",
        institutions=["Stanford", "MIT", "Oxford", "Cambridge"]
    )

    print(f"✓ Workspace created!")
    print(f"  ID: {workspace.workspace_id}")
    print(f"  Name: {workspace.name}")
    print(f"  Institutions: {', '.join(workspace.institutions)}")

    # Add members
    print("\nAdding collaborators...")
    members = [
        ("researcher_002", WorkspaceRole.CONTRIBUTOR),
        ("researcher_003", WorkspaceRole.CONTRIBUTOR),
        ("researcher_004", WorkspaceRole.ADMIN),
    ]

    for user_id, role in members:
        workspace_mgr.add_member(
            workspace_id=workspace.workspace_id,
            user_id=user_id,
            role=role,
            added_by="researcher_001"
        )
        print(f"  ✓ Added {user_id} as {role.value}")

    return workspace_mgr, workspace.workspace_id


def demo_experiment_tracking(workspace_id):
    """Demo: Track experiments"""
    print_section("5. Experiment Tracking")

    # Initialize experiment tracker
    exp_tracker = ExperimentTracker()

    # Create experiment
    print("Creating experiment...")
    experiment = exp_tracker.create_experiment(
        name="ResNet50 Hyperparameter Tuning",
        workspace_id=workspace_id,
        user_id="researcher_002",
        parameters={
            "model": "ResNet50",
            "learning_rate": 0.001,
            "batch_size": 32,
            "epochs": 100,
            "optimizer": "Adam"
        },
        tags=["deep-learning", "image-classification", "covid-19"]
    )

    print(f"✓ Experiment created: {experiment.experiment_id}")

    # Log metrics over training
    print("\nLogging training metrics...")
    for epoch in [0, 25, 50, 75, 100]:
        accuracy = 0.75 + (epoch / 100) * 0.17  # Simulated improvement
        loss = 0.5 - (epoch / 100) * 0.35

        exp_tracker.log_metrics(
            experiment_id=experiment.experiment_id,
            metrics={"accuracy": accuracy, "loss": loss},
            step=epoch
        )

    print(f"  ✓ Logged metrics for 5 checkpoints")

    # Log artifacts
    exp_tracker.log_artifact(
        experiment_id=experiment.experiment_id,
        name="model_checkpoint",
        path="/models/resnet50_best.pth"
    )
    exp_tracker.log_artifact(
        experiment_id=experiment.experiment_id,
        name="training_plot",
        path="/plots/training_curves.png"
    )

    print(f"  ✓ Logged 2 artifacts")

    # End experiment
    exp_tracker.end_experiment(
        experiment_id=experiment.experiment_id,
        status=ExperimentStatus.COMPLETED
    )

    print(f"  ✓ Experiment completed")

    # Show final results
    final_exp = exp_tracker.get_experiment(experiment.experiment_id)
    final_metrics = final_exp.metrics
    print(f"\nFinal Results:")
    print(f"  Accuracy: {final_metrics['accuracy'][-1][1]:.3f}")
    print(f"  Loss: {final_metrics['loss'][-1][1]:.3f}")

    return exp_tracker


def demo_citation_tracking(dataset_id):
    """Demo: Track citations"""
    print_section("6. Citation Tracking")

    # Initialize citation tracker
    citation_tracker = CitationTracker()

    # Add citations
    print("Adding research citations...")
    citations_data = [
        {
            "paper_title": "Deep Learning for COVID-19 Detection: A Comprehensive Review",
            "paper_authors": ["Smith, J.", "Johnson, A.", "Williams, R."],
            "venue": "Nature Medicine",
            "doi": "10.1038/s41591-2024-00001",
            "publication_date": datetime(2024, 3, 15)
        },
        {
            "paper_title": "Automated COVID-19 Diagnosis Using Transfer Learning",
            "paper_authors": ["Chen, L.", "Zhang, W."],
            "venue": "IEEE Transactions on Medical Imaging",
            "doi": "10.1109/TMI.2024.00123",
            "publication_date": datetime(2024, 5, 20)
        },
        {
            "paper_title": "Multi-Modal Fusion for COVID-19 Classification",
            "paper_authors": ["Kumar, P.", "Singh, R.", "Patel, M."],
            "venue": "Medical Image Analysis",
            "doi": "10.1016/j.media.2024.00456",
            "publication_date": datetime(2024, 7, 10)
        }
    ]

    for cite_data in citations_data:
        citation = citation_tracker.add_citation(
            dataset_id=dataset_id,
            **cite_data
        )
        citation_tracker.verify_citation(citation.citation_id, True)
        print(f"  ✓ {cite_data['paper_title'][:50]}...")

    # Get citation statistics
    stats = citation_tracker.get_citation_statistics(dataset_id)
    print(f"\nCitation Statistics:")
    print(f"  Total citations: {stats['total_citations']}")
    print(f"  Verified citations: {stats['verified_citations']}")
    print(f"  Recent citations (last year): {stats['recent_citations']}")

    # Get impact metrics
    impact = citation_tracker.get_impact_metrics(dataset_id)
    print(f"\nImpact Metrics:")
    print(f"  H-index: {impact['h_index']}")
    print(f"  Impact score: {impact['impact_score']:.2f}")

    return citation_tracker


def demo_privacy_compliance(dataset_id):
    """Demo: Privacy and compliance controls"""
    print_section("7. Privacy & Compliance")

    # Initialize privacy control
    privacy_ctrl = PrivacyControl()

    # Set privacy level
    print("Configuring privacy settings...")
    privacy_ctrl.set_privacy_level(dataset_id, PrivacyLevel.CONFIDENTIAL)
    privacy_ctrl.add_compliance_requirement(dataset_id, ComplianceRegulation.HIPAA)
    privacy_ctrl.add_compliance_requirement(dataset_id, ComplianceRegulation.GDPR)

    print(f"  ✓ Privacy level: CONFIDENTIAL")
    print(f"  ✓ Compliance: HIPAA, GDPR")

    # Grant consent
    print("\nManaging user consent...")
    consent = privacy_ctrl.consent_manager.grant_consent(
        user_id="patient_12345",
        dataset_id=dataset_id,
        purpose="COVID-19 detection research",
        expires_in_days=365
    )
    print(f"  ✓ Consent granted for patient_12345")

    # Check consent
    has_consent = privacy_ctrl.consent_manager.check_consent(
        user_id="patient_12345",
        dataset_id=dataset_id,
        purpose="COVID-19 detection research"
    )
    print(f"  ✓ Consent verified: {has_consent}")

    # Generate report
    report = privacy_ctrl.generate_privacy_report(dataset_id)
    print(f"\nPrivacy Report:")
    print(f"  Privacy level: {report['privacy_level']}")
    print(f"  Compliance regulations: {', '.join(report['compliance_regulations'])}")
    print(f"  Valid consents: {report['valid_consents']}")


def demo_license_management(dataset_id):
    """Demo: License management"""
    print_section("8. License Management")

    # Initialize license manager
    license_mgr = LicenseManager()

    # Assign license
    print("Assigning dataset license...")
    license_obj = license_mgr.assign_license(dataset_id, LicenseType.CC_BY_NC)

    print(f"✓ License assigned: {license_obj.name}")
    print(f"  Commercial use: {license_obj.allows_commercial}")
    print(f"  Modification: {license_obj.allows_modification}")
    print(f"  Attribution required: {license_obj.requires_attribution}")

    # Validate usage
    print("\nValidating usage scenarios...")
    scenarios = [
        ("Academic research", False, True, False),
        ("Commercial product", True, True, True),
        ("Open-source tool", False, True, True),
    ]

    for name, commercial, modification, distribution in scenarios:
        result = license_mgr.validate_usage(
            dataset_id=dataset_id,
            commercial=commercial,
            modification=modification,
            distribution=distribution
        )
        status = "✓ Allowed" if result['valid'] else "✗ Not allowed"
        print(f"  {status}: {name}")
        if not result['valid']:
            print(f"    Reason: {result['violations'][0]}")


def demo_ethics_review(dataset_id):
    """Demo: Ethics review process"""
    print_section("9. Ethics Review")

    # Initialize ethics review manager
    ethics_mgr = EthicsReviewManager()

    # Submit for review
    print("Submitting dataset for ethics review...")
    review = ethics_mgr.submit_review(
        dataset_id=dataset_id,
        categories=[
            EthicsCategory.HUMAN_SUBJECTS,
            EthicsCategory.SENSITIVE_DATA,
            EthicsCategory.BIAS_FAIRNESS
        ],
        institution="Stanford IRB",
        concerns=[
            "Patient privacy must be protected",
            "Potential bias in training data distribution"
        ]
    )

    print(f"✓ Review submitted: {review.review_id}")
    print(f"  Status: {review.status.value}")
    print(f"  Categories: {', '.join([c.value for c in review.categories])}")

    # Assign reviewer
    ethics_mgr.assign_reviewer(review.review_id, "irb_reviewer_001")
    print(f"  ✓ Reviewer assigned")

    # Complete review
    print("\nCompleting ethics review...")
    ethics_mgr.complete_review(
        review_id=review.review_id,
        status=EthicsStatus.CONDITIONAL_APPROVAL,
        reviewer_id="irb_reviewer_001",
        conditions=[
            "All patient identifiers must be anonymized",
            "Regular bias audits required every 6 months"
        ],
        recommendations=[
            "Implement differential privacy techniques",
            "Ensure diverse representation in validation set"
        ],
        notes="Dataset approved with conditions for COVID-19 research",
        approval_period_days=365
    )

    print(f"  ✓ Review completed")
    print(f"  Status: CONDITIONAL_APPROVAL")

    # Check approval
    is_approved = ethics_mgr.check_approval(dataset_id)
    print(f"  ✓ Approval status: {'Valid' if is_approved else 'Invalid'}")

    # Generate report
    report = ethics_mgr.generate_ethics_report(dataset_id)
    print(f"\nEthics Report:")
    print(f"  Reviews: {report['total_reviews']}")
    print(f"  Status: {report['latest_status']}")
    print(f"  Concerns: {report['total_concerns']}")
    print(f"  Approved: {report['is_approved']}")


def main():
    """Run complete research partnership demo"""
    print("\n" + "=" * 60)
    print("Research Partnerships Infrastructure Demo".center(60))
    print("=" * 60)

    # Run all demos
    hub, dataset_id = demo_dataset_registration()
    benchmark_mgr, benchmark_id = demo_benchmark_creation(hub, dataset_id)
    demo_leaderboard(benchmark_mgr, benchmark_id)
    workspace_mgr, workspace_id = demo_collaboration_workspace()
    exp_tracker = demo_experiment_tracking(workspace_id)
    citation_tracker = demo_citation_tracking(dataset_id)
    demo_privacy_compliance(dataset_id)
    demo_license_management(dataset_id)
    demo_ethics_review(dataset_id)

    # Final summary
    print_section("Summary")
    print("✓ Dataset registered and published")
    print("✓ Benchmark created with 4 submissions")
    print("✓ Collaboration workspace with 4 institutions")
    print("✓ Experiment tracked with metrics and artifacts")
    print("✓ 3 citations tracked")
    print("✓ Privacy compliance configured (HIPAA, GDPR)")
    print("✓ License assigned (CC-BY-NC)")
    print("✓ Ethics review completed with approval")

    print("\n" + "=" * 60)
    print("Demo completed successfully!".center(60))
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
