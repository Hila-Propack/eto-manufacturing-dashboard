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
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import List, Dict, Any, Optional, Union

# Import only the required libraries to start with
# We'll add the rest gradually after successful installation
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
        # Placeholder for GitHub client initialization
        # Will be implemented when PyGithub is available
        logger.info("GitHub client initialization is currently disabled")
        return None
    
    def search_repositories(self, query: str = None, **kwargs):
        """
        Search GitHub repositories based on query and filter parameters
        
        Args:
            query: Search query string (overrides config if provided)
            **kwargs: Additional filters to override config
        
        Returns:
            List of RepoData objects representing matching repositories
        """
        # Placeholder implementation until we have PyGithub working
        logger.info(f"Search query: {query}")
        search_config = self.config.get("search", {})
        
        # Log the search parameters that would be used
        if query is None:
            query = search_config.get("query", "")
            
        logger.info(f"Would search for: {query}")
        logger.info("Repository search is currently disabled until PyGithub is installed")
        return []
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
        Clone selected repositories to the local filesystem (placeholder)
        
        Args:
            repositories: List of repositories to clone (uses self.results if None)
            clone_dir: Directory where repositories should be cloned (overrides config)
            max_to_clone: Maximum number of repositories to clone (overrides config)
            
        Returns:
            List of cloned repository data
        """
        logger.info("Repository cloning is currently disabled until gitpython is installed")
        
        # Get configuration
        clone_config = self.config.get("clone", {})
        if clone_dir is None:
            clone_dir = clone_config.get("directory", "cloned_repos")
        
        if max_to_clone is None:
            max_to_clone = clone_config.get("max_repositories", 10)
            
        logger.info(f"Would clone up to {max_to_clone} repositories to {clone_dir}")
        return []
    
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
        
        repositories = cloner.search_repositories(args.query, **search_kwargs)
        
        logger.info(f"Found {len(repositories)} repositories matching criteria")
        
        # Clone repositories if not in search-only mode
        if not args.search_only:
            cloner.clone_repositories(
                repositories=repositories,
                clone_dir=args.clone_dir,
                max_to_clone=args.max_clone
            )
        
        # Export results
        cloner.export_results(
            format=args.export_format,
            output_file=args.output_file
        )
        
    except KeyboardInterrupt:
        logger.info("Operation interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        if args.verbose:
            import traceback
            logger.error(traceback.format_exc())
        sys.exit(1)


if __name__ == "__main__":
    main()
