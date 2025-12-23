#!/usr/bin/env python3
"""
Configure GitHub Branch Protection Rules for Hispania repository.

This script automates the setup of branch protection rules for main and develop branches,
ensuring PR-based workflow with proper reviews and status checks.

Requirements:
    pip install PyGithub

Usage:
    python configure-branch-protection.py --token YOUR_GITHUB_TOKEN
    
    Or set GITHUB_TOKEN environment variable:
    export GITHUB_TOKEN=your_token_here
    python configure-branch-protection.py

GitHub Token Permissions Required:
    - repo (full control of private repositories)
"""

import argparse
import os
import sys
from github import Github, GithubException


def configure_branch_protection(repo, branch_name, strict=True):
    """
    Configure branch protection rules.
    
    Args:
        repo: GitHub repository object
        branch_name: Name of the branch to protect
        strict: If True, enforces strict rules for production branches (main).
                If False, allows more flexibility for development branches.
    
    Strict mode (main):
        - Require conversation resolution
        - Enforce linear history
        - Admins cannot bypass
        - Strict status checks (branches must be up to date)
    
    Flexible mode (develop):
        - Admins can bypass for emergencies
        - No linear history requirement
        - More flexible status checks
    """
    icon = "🔒" if strict else "🔓"
    mode = "strict" if strict else "flexible"
    print(f"\n{icon} Configuring {mode} branch protection for '{branch_name}'...")
    
    try:
        # Check if branch exists
        try:
            branch = repo.get_branch(branch_name)
        except GithubException as e:
            if e.status == 404:
                print(f"⚠️  Branch '{branch_name}' does not exist yet. Skipping configuration.")
                print(f"   Run this script again after creating the {branch_name} branch.")
                return True
            raise
        
        # Configure protection with conditional parameters
        protection_args = {
            # Pull request reviews (always required)
            "required_approving_review_count": 1,
            "dismiss_stale_reviews": True,
            "require_code_owner_reviews": False,  # Set to True if you have CODEOWNERS
            
            # Status checks
            "strict": strict,  # Strict: require branches up to date
            "contexts": ["SonarCloud"],  # Required status checks
            
            # Restrictions (always block force pushes and deletions)
            "allow_force_pushes": False,
            "allow_deletions": False,
            
            # Admin enforcement (strict mode only)
            "enforce_admins": strict,
        }
        
        # Add strict-only parameters
        if strict:
            protection_args["require_conversation_resolution"] = True
            protection_args["require_linear_history"] = True
        
        branch.edit_protection(**protection_args)
        
        # Success message
        print(f"✅ Branch protection configured for '{branch_name}'")
        print(f"   - Requires 1 approval")
        print(f"   - Dismisses stale reviews")
        
        if strict:
            print(f"   - Requires conversation resolution")
            print(f"   - Linear history enforced")
            print(f"   - Admins cannot bypass")
        else:
            print(f"   - Admins can bypass (for emergencies)")
        
        print(f"   - Force pushes blocked")
        print(f"   - Deletions blocked")
        
        return True
        
    except GithubException as e:
        print(f"❌ Failed to configure {branch_name} branch: {e.data.get('message', str(e))}")
        return False


def verify_branch_protection(repo, branch_name):
    """Verify and display current branch protection settings."""
    print(f"\n📋 Current protection rules for '{branch_name}':")
    
    try:
        branch = repo.get_branch(branch_name)
        protection = branch.get_protection()
        
        # Pull Request settings
        if protection.required_pull_request_reviews:
            reviews = protection.required_pull_request_reviews
            print(f"   ✓ Required approvals: {reviews.required_approving_review_count}")
            print(f"   ✓ Dismiss stale reviews: {reviews.dismiss_stale_reviews}")
            print(f"   ✓ Code owner reviews: {reviews.require_code_owner_reviews}")
        
        # Status checks
        if protection.required_status_checks:
            checks = protection.required_status_checks
            print(f"   ✓ Strict status checks: {checks.strict}")
            if checks.contexts:
                print(f"   ✓ Required checks: {', '.join(checks.contexts)}")
        
        # Restrictions
        print(f"   ✓ Enforce for admins: {protection.enforce_admins.enabled}")
        print(f"   ✓ Allow force pushes: {protection.allow_force_pushes.enabled}")
        print(f"   ✓ Allow deletions: {protection.allow_deletions.enabled}")
        
        return True
        
    except GithubException as e:
        if e.status == 404:
            print(f"   ⚠️  No protection rules configured")
        else:
            print(f"   ❌ Error: {e.data.get('message', str(e))}")
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Configure GitHub branch protection rules for Hispania repository"
    )
    parser.add_argument(
        "--token",
        help="GitHub personal access token (or set GITHUB_TOKEN env var)",
        default=os.environ.get("GITHUB_TOKEN")
    )
    parser.add_argument(
        "--repo",
        help="Repository in format 'owner/repo'",
        default="ahead-labs-software/hispania"
    )
    parser.add_argument(
        "--verify-only",
        action="store_true",
        help="Only verify current settings without making changes"
    )
    parser.add_argument(
        "--skip-develop",
        action="store_true",
        help="Skip configuring develop branch"
    )
    
    args = parser.parse_args()
    
    # Validate token
    if not args.token:
        print("❌ Error: GitHub token required")
        print("   Set GITHUB_TOKEN environment variable or use --token argument")
        print("\n   To create a token:")
        print("   1. Go to https://github.com/settings/tokens")
        print("   2. Click 'Generate new token (classic)'")
        print("   3. Select 'repo' scope")
        print("   4. Copy the token")
        sys.exit(1)
    
    print("=" * 60)
    print("  GitHub Branch Protection Configuration")
    print("=" * 60)
    print(f"\nRepository: {args.repo}")
    
    # Initialize GitHub client
    try:
        gh = Github(args.token)
        repo = gh.get_repo(args.repo)
        print(f"✓ Connected to repository: {repo.full_name}")
    except GithubException as e:
        print(f"❌ Failed to connect to GitHub: {e.data.get('message', str(e))}")
        sys.exit(1)
    
    # Verify only mode
    if args.verify_only:
        print("\n📊 Verification Mode - Current Settings:")
        verify_branch_protection(repo, "main")
        if not args.skip_develop:
            verify_branch_protection(repo, "develop")
        sys.exit(0)
    
    # Configure branch protections
    success = True
    
    # Configure main branch (strict mode)
    if not configure_branch_protection(repo, "main", strict=True):
        success = False
    else:
        verify_branch_protection(repo, "main")
    
    # Configure develop branch (flexible mode)
    if not args.skip_develop:
        if not configure_branch_protection(repo, "develop", strict=False):
            success = False
        else:
            verify_branch_protection(repo, "develop")
    
    # Summary
    print("\n" + "=" * 60)
    if success:
        print("✅ Branch protection configuration completed successfully!")
        print("\n📝 Next steps:")
        print("   1. Create CODEOWNERS file for automatic reviewer assignment")
        print("   2. Set up GitHub Actions for Terraform validation")
        print("   3. Add status checks to required_status_checks once CI/CD is ready")
        print("\n🔗 View settings:")
        print(f"   https://github.com/{args.repo}/settings/branches")
    else:
        print("⚠️  Branch protection configuration completed with some errors")
        print("   Review the output above for details")
    print("=" * 60)
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
