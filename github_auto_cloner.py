#!/usr/bin/env python3
"""
GitHub Auto Cloner - A CLI tool for finding, filtering, and cloning relevant GitHub repositories

This tool helps users search for GitHub repositories based on keywords, industry relevance,
popularity metrics, and other criteria. It can automatically clone repositories that meet
specified criteria and export search results to JSON or CSV formats.
"""

import os
import sys
import json
import csv
import argparse
import datetime
import logging
import yaml
import time
import subprocess
import re
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import List, Dict, Any, Optional, Union

# Import only the required libraries to start with
# We'll add these libraries as the project progresses
# import pandas as pd
# import git
# from github import Github, RateLimitExceededException, GithubException
# from github.Repository import Repository

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class RepoData:
    """Data class for repository information"""
    name: str
    owner: str
    url: str
    clone_url: str
    description: str
    stars: int
    forks: int
    watchers: int
    language: str
    created_at: str
    updated_at: str
    pushed_at: str
    industry_relevance: float = 0.0
    cloned: bool = False
    clone_path: str = ""


class GitHubAutoCloner:
    """Main class for GitHub repository searching, filtering, and cloning"""
    
    def __init__(self, config_path: str = "config.yaml"):
        """Initialize the GitHub Auto Cloner with configuration"""
        self.config = self._load_config(config_path)
        # We'll implement GitHub client initialization later
        # self.github = self._init_github_client()
        self.results = []
        
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load configuration from YAML file"""
        try:
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
            logger.info(f"Configuration loaded from {config_path}")
            return config
        except FileNotFoundError:
            logger.error(f"Configuration file not found: {config_path}")
            sys.exit(1)
        except yaml.YAMLError as e:
            logger.error(f"Error parsing YAML configuration: {e}")
            sys.exit(1)
    
    def _init_github_client(self):
        """Initialize GitHub client with token from environment or config"""
        # Placeholder for GitHub client initialization that uses subprocess to make GitHub API calls
        token = os.getenv("GITHUB_TOKEN", self.config.get("github_token", ""))
        if not token:
            logger.warning("GitHub token not found. Limited functionality available.")
            logger.warning("Set GITHUB_TOKEN environment variable for full functionality.")
        return token
    
    def search_repositories(self, query: str = None, **kwargs) -> List[RepoData]:
        """
        Search GitHub repositories based on query and filter parameters
        
        Args:
            query: Search query string (overrides config if provided)
            **kwargs: Additional filters to override config
        
        Returns:
            List of RepoData objects representing matching repositories
        """
        search_config = self.config.get("search", {})
        
        # Build the search query
        if query is None:
            query = search_config.get("query", "")
            
        # Add industry-relevant keywords if configured
        if "industry_keywords" in search_config and search_config.get("add_industry_keywords", True):
            industry_keywords = " ".join([f'"{kw}"' for kw in search_config["industry_keywords"]])
            query = f"{query} {industry_keywords}" if query else industry_keywords
            
        # Add minimum stars filter
        min_stars = kwargs.get("min_stars", search_config.get("min_stars", 10))
        query = f"{query} stars:>={min_stars}"
        
        # Add language filter if specified
        languages = kwargs.get("languages", search_config.get("languages", []))
        if languages:
            lang_filter = " ".join([f'language:"{lang}"' for lang in languages])
            query = f"{query} {lang_filter}"
            
        logger.info(f"Searching repositories with query: {query}")
        
        # Create sample results for demonstration
        # In a full implementation, this would call the GitHub API
        sample_repos = []
        
        # Add some sample repositories based on the query
        if "food packaging" in query.lower():
            relevance = 0.8
            prefix = "food-packaging"
        elif "automation" in query.lower():
            relevance = 0.7
            prefix = "automation"
        elif "operations management" in query.lower():
            relevance = 0.9
            prefix = "operations-mgmt" 
        else:
            relevance = 0.5
            prefix = "sample"
            
        # Create a few sample repositories
        for i in range(1, min(kwargs.get("max_results", search_config.get("max_results", 5)), 10) + 1):
            repo_data = RepoData(
                name=f"{prefix}-repo-{i}",
                owner=f"example-user-{i}",
                url=f"https://github.com/example-user-{i}/{prefix}-repo-{i}",
                clone_url=f"https://github.com/example-user-{i}/{prefix}-repo-{i}.git",
                description=f"This is a sample repository about {query} for demonstration purposes.",
                stars=min_stars + i * 10,
                forks=i * 5,
                watchers=i * 3,
                language="Python" if i % 2 == 0 else "JavaScript",
                created_at=datetime.datetime.now().replace(month=i, day=i).isoformat(),
                updated_at=datetime.datetime.now().isoformat(),
                pushed_at=datetime.datetime.now().isoformat(),
                industry_relevance=relevance - (i * 0.05)
            )
            sample_repos.append(repo_data)
            
        # Filter by minimum relevance
        min_relevance = kwargs.get("min_relevance", search_config.get("min_industry_relevance", 0.0))
        if min_relevance > 0:
            sample_repos = [r for r in sample_repos if r.industry_relevance >= min_relevance]
            
        self.results = sample_repos
        logger.info(f"Found {len(sample_repos)} sample repositories")
        
        return sample_repos
    def _calculate_industry_relevance(self, name: str, description: str, topics: List[str] = None) -> float:
        """
        Calculate industry relevance score for a repository based on available data
        
        Args:
            name: Repository name
            description: Repository description
            topics: List of repository topics/tags
            
        Returns:
            A relevance score between 0.0 and 1.0
        """
        relevance_score = 0.0
        industry_keywords = self.config.get("search", {}).get("industry_keywords", [])
        
        if not industry_keywords:
            return 1.0  # No industry filtering if no keywords specified
        
        # Check repository description
        description = description or ""
        for keyword in industry_keywords:
            if keyword.lower() in description.lower():
                relevance_score += 0.3
        
        # Check repository topics
        if topics:
            for topic in topics:
                for keyword in industry_keywords:
                    if keyword.lower() in topic.lower():
                        relevance_score += 0.5
        
        # Check repository name
        for keyword in industry_keywords:
            if keyword.lower() in name.lower():
                relevance_score += 0.2
        
        # Cap at 1.0
        return min(relevance_score, 1.0)
    
    def clone_repositories(self, repositories=None, clone_dir=None, max_to_clone=None):
        """
        Clone selected repositories to the local filesystem
        
        Args:
            repositories: List of repositories to clone (uses self.results if None)
            clone_dir: Directory where repositories should be cloned (overrides config)
            max_to_clone: Maximum number of repositories to clone (overrides config)
            
        Returns:
            List of cloned repository data
        """
        if repositories is None:
            repositories = self.results
            
        if not repositories:
            logger.warning("No repositories to clone")
            return []
        
        # Get configuration
        clone_config = self.config.get("clone", {})
        if clone_dir is None:
            clone_dir = clone_config.get("directory", "cloned_repos")
        
        if max_to_clone is None:
            max_to_clone = clone_config.get("max_repositories", 10)
            
        # Create clone directory if it doesn't exist
        clone_path = Path(clone_dir)
        clone_path.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Cloning up to {max_to_clone} repositories to {clone_path}")
        
        # Sort repositories by stars or industry relevance
        sort_by = clone_config.get("sort_by", "stars")
        if sort_by == "industry_relevance":
            repositories = sorted(repositories, key=lambda r: r.industry_relevance, reverse=True)
        else:  # Default to sorting by stars
            repositories = sorted(repositories, key=lambda r: r.stars, reverse=True)
        
        # Limit number of repositories to clone
        to_clone = repositories[:max_to_clone]
        cloned_repos = []
        
        for repo in to_clone:
            target_dir = clone_path / f"{repo.owner}_{repo.name}"
            
            try:
                # Instead of using gitpython, use subprocess to clone
                logger.info(f"Cloning {repo.clone_url} to {target_dir}")
                
                if target_dir.exists():
                    logger.info(f"Repository directory already exists. Updating...")
                    if (target_dir / ".git").exists():
                        # If it's a git repo, update it
                        cmd = ["git", "-C", str(target_dir), "pull", "origin", "main"]
                        result = subprocess.run(cmd, capture_output=True, text=True)
                        if result.returncode != 0:
                            # Try master branch if main fails
                            cmd = ["git", "-C", str(target_dir), "pull", "origin", "master"]
                            result = subprocess.run(cmd, capture_output=True, text=True)
                    else:
                        # If directory exists but isn't a git repo, remove and clone
                        import shutil
                        shutil.rmtree(target_dir)
                        cmd = ["git", "clone", repo.clone_url, str(target_dir)]
                        result = subprocess.run(cmd, capture_output=True, text=True)
                else:
                    # Clone new repository
                    cmd = ["git", "clone", repo.clone_url, str(target_dir)]
                    result = subprocess.run(cmd, capture_output=True, text=True)
                
                if result.returncode == 0:
                    repo.cloned = True
                    repo.clone_path = str(target_dir)
                    cloned_repos.append(repo)
                    logger.info(f"Successfully cloned/updated {repo.name}")
                else:
                    logger.error(f"Failed to clone {repo.name}: {result.stderr}")
                    
            except Exception as e:
                logger.error(f"Error while cloning {repo.clone_url}: {str(e)}")
        
        logger.info(f"Successfully cloned {len(cloned_repos)} repositories")
        return cloned_repos
    
    def export_results(self, format: str = "json", output_file: str = None) -> str:
        """
        Export search results to JSON or CSV file
        
        Args:
            format: Output format ('json' or 'csv')
            output_file: Output filename (overrides config)
            
        Returns:
            Path to the output file
        """
        if not self.results:
            logger.warning("No results to export")
            return ""
        
        logger.info("Export functionality is limited until pandas is installed")
        
        export_config = self.config.get("export", {})
        
        if output_file is None:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            if format.lower() == "csv":
                output_file = export_config.get("csv_file", f"github_results_{timestamp}.csv")
            else:
                output_file = export_config.get("json_file", f"github_results_{timestamp}.json")
        
        try:
            # Convert results to dictionaries
            results_dict = [asdict(repo) for repo in self.results]
            
            if format.lower() == "csv":
                # Basic CSV export without pandas
                logger.info("CSV export using pandas is not available")
                # Use basic CSV module instead
                with open(output_file, 'w', newline='') as f:
                    if results_dict:
                        writer = csv.DictWriter(f, fieldnames=results_dict[0].keys(), 
                                               quoting=csv.QUOTE_NONNUMERIC)
                        writer.writeheader()
                        writer.writerows(results_dict)
            else:
                # JSON export
                with open(output_file, 'w') as f:
                    json.dump(results_dict, f, indent=2)
            
            logger.info(f"Exported {len(self.results)} results to {output_file}")
            return output_file
            
        except Exception as e:
            logger.error(f"Error exporting results: {str(e)}")
            return ""


def main():
    """Main entry point for the CLI application"""
    parser = argparse.ArgumentParser(
        description="GitHub Auto Cloner - Find, filter, and clone relevant GitHub repositories"
    )
    
    parser.add_argument(
        "--config", "-c",
        default="config.yaml",
        help="Path to configuration YAML file"
    )
    
    parser.add_argument(
        "--query", "-q",
        help="GitHub search query (overrides config file)"
    )
    
    parser.add_argument(
        "--min-stars",
        type=int,
        help="Minimum stars filter (overrides config file)"
    )
    
    parser.add_argument(
        "--date-range",
        choices=["week", "month", "quarter", "year"],
        help="Filter by repository activity date range (overrides config file)"
    )
    
    parser.add_argument(
        "--max-results",
        type=int,
        help="Maximum number of search results to process (overrides config file)"
    )
    
    parser.add_argument(
        "--min-relevance",
        type=float,
        help="Minimum industry relevance score (0.0-1.0, overrides config file)"
    )
    
    parser.add_argument(
        "--languages",
        nargs="+",
        help="Filter by programming languages (overrides config file)"
    )
    
    parser.add_argument(
        "--clone-dir",
        help="Directory to clone repositories (overrides config file)"
    )
    
    parser.add_argument(
        "--max-clone",
        type=int,
        help="Maximum number of repositories to clone (overrides config file)"
    )
    
    parser.add_argument(
        "--export-format",
        choices=["json", "csv"],
        default="json",
        help="Export format for results (default: json)"
    )
    
    parser.add_argument(
        "--output-file",
        help="Output filename for export (overrides config file)"
    )
    
    parser.add_argument(
        "--search-only",
        action="store_true",
        help="Only search repositories, don't clone them"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose logging"
    )
    
    args = parser.parse_args()
    
    # Set logging level based on verbosity
    if args.verbose:
        logger.setLevel(logging.DEBUG)
    
    # Print header
    print("\n" + "="*80)
    print(" GitHub Auto Cloner ".center(80, "="))
    print("="*80)
    
    try:
        # Initialize auto cloner with config
        cloner = GitHubAutoCloner(args.config)
        
        # Search for repositories
        search_kwargs = {}
        if args.min_stars is not None:
            search_kwargs["min_stars"] = args.min_stars
        if args.date_range is not None:
            search_kwargs["date_range"] = args.date_range
        if args.max_results is not None:
            search_kwargs["max_results"] = args.max_results
        if args.min_relevance is not None:
            search_kwargs["min_relevance"] = args.min_relevance
        if args.languages:
            search_kwargs["languages"] = args.languages
        
        # Print search criteria
        print("\n📋 Search Criteria:")
        print(f"  Query: {args.query or cloner.config.get('search', {}).get('query', 'Not specified')}")
        print(f"  Min Stars: {args.min_stars or cloner.config.get('search', {}).get('min_stars', 'Not specified')}")
        if args.languages or cloner.config.get('search', {}).get('languages'):
            print(f"  Languages: {args.languages or cloner.config.get('search', {}).get('languages', [])}")
        print()
            
        # Perform search
        print("🔍 Searching repositories...")
        repositories = cloner.search_repositories(args.query, **search_kwargs)
        
        if repositories:
            print(f"\n✅ Found {len(repositories)} repositories matching criteria:")
            for i, repo in enumerate(repositories[:5], 1):
                print(f"  {i}. {repo.name} by {repo.owner} ({repo.stars} ⭐) - Relevance: {repo.industry_relevance:.2f}")
            if len(repositories) > 5:
                print(f"  ... and {len(repositories)-5} more")
            print()
        else:
            print("\n❌ No repositories found matching the criteria")
            print("  Try adjusting your search parameters or query.")
            sys.exit(0)
        
        # Clone repositories if not in search-only mode
        if not args.search_only:
            print("📥 Cloning repositories...")
            cloned = cloner.clone_repositories(
                repositories=repositories,
                clone_dir=args.clone_dir,
                max_to_clone=args.max_clone
            )
            
            if cloned:
                print(f"\n✅ Successfully cloned {len(cloned)} repositories to {args.clone_dir or cloner.config.get('clone', {}).get('directory', 'cloned_repos')}")
            else:
                print("\n⚠️ No repositories were cloned")
        
        # Export results
        if args.export_format or args.output_file:
            print("\n📊 Exporting results...")
            output_file = cloner.export_results(
                format=args.export_format,
                output_file=args.output_file
            )
            if output_file:
                print(f"✅ Results exported to {output_file}")
            
        print("\n✅ Operation completed successfully!")
        print("="*80 + "\n")
        
    except KeyboardInterrupt:
        print("\n\n⚠️ Operation interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Error: {str(e)}")
        if args.verbose:
            import traceback
            print(traceback.format_exc())
        sys.exit(1)


if __name__ == "__main__":
    main()
