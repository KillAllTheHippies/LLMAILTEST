"""
DEPRECATED: This standalone analysis tool is no longer required for the main program.
Keeping for reference only.

Original file content follows:
--------------------------------------------------------------------------------

Job Analysis Tool (Standalone Command-Line Utility)

This script provides command-line analysis capabilities for job data. It is a standalone
tool and not integrated with the main GUI application. Use this for offline analysis
of job data and generating reports.

Usage:
	python job_analyzer.py --fe                # Fetch and store jobs
	python job_analyzer.py --an                # Analyze stored jobs
	python job_analyzer.py --fe --an           # Fetch and analyze jobs
	python job_analyzer.py --fe --fo json      # Use JSON format for storage

This tool provides additional analysis features not available in the main GUI:
- Success rate analysis by scenario
- Job completion time analysis
- Pattern matching between similar jobs
- Advanced filtering and data export
"""

# All code below is commented out as this standalone tool is no longer required
'''

import argparse
import csv
import pandas as pd
import datetime
from typing import List, Dict
import os
import requests
import json
from dataclasses import dataclass

@dataclass
class Job:
	job_id: str
	team_id: str
	scenario: str
	subject: str
	body: str
	scheduled_time: str
	started_time: str|None = None
	completed_time: str|None = None
	output: str|None = None
	objectives: dict|None = None

	@property
	def is_completed(self):
		return self.completed_time is not None



class JobAnalyzer:
	def __init__(self, csv_path: str = "jobs_data.csv", format: str = "csv"):
		self.csv_path = csv_path
		self.format = format
		self.team_id = "killallthehippies"
		
		# Use the API key directly
		self.api_key = "eyJsb2dpbiI6ICJraWxsYWxsdGhlaGlwcGllcyIsICJhcGlfa2V5IjogIjAyNzNhNmZlLTE3OWEtNDEyMi05ODk4LTI1YzE3OTNmN2EyMyJ9"
		self.api_server = "https://llmailinject.azurewebsites.net"



	def fetch_and_save_jobs(self):
		"""Fetch jobs from API and save to CSV or JSON"""
		try:
			response = requests.get(
				f"{self.api_server}/api/teams/mine/jobs",
				headers={
					'Authorization': f'Bearer {self.api_key}',
					'Content-Type': 'application/json'
				}
			)
			
			if not response.ok:
				error_msg = response.json() if response.content else {'message': response.reason}
				raise Exception(f"Error fetching jobs: {error_msg.get('message', 'Unknown error')}")
			
			jobs = [Job(**job_data) for job_data in response.json()]
			
			# Convert jobs to dictionary format
			jobs_data = [{
				'job_id': job.job_id,
				'scenario': job.scenario,
				'subject': job.subject,
				'body': job.body,
				'scheduled_time': job.scheduled_time,
				'started_time': job.started_time,
				'completed_time': job.completed_time,
				'output': job.output,
				'objectives': str(job.objectives)
			} for job in jobs]

			# Save based on format
			if self.format == 'json':
				with open(self.csv_path, 'w', encoding='utf-8') as f:
					json.dump(jobs_data, f, indent=2)
			else:
				with open(self.csv_path, 'w', newline='', encoding='utf-8') as f:
					writer = csv.DictWriter(f, fieldnames=jobs_data[0].keys())
					writer.writeheader()
					writer.writerows(jobs_data)
			print(f"Successfully fetched and saved {len(jobs_data)} jobs to {self.csv_path}")
		except Exception as e:
			print(f"Error: {str(e)}")







	def _format_scenario_name(self, scenario: str) -> str:
		"""Remove 'level' prefix from scenario name"""
		return scenario.replace('level', '')

	def _show_jobs_by_scenario(self, df: pd.DataFrame):
		"""Show jobs for a specific scenario with improved user guidance"""
		# Get unique scenarios and format them
		scenarios = df['scenario'].unique()
		formatted_scenarios = sorted([self._format_scenario_name(s) for s in scenarios])
		
		print("\nAvailable scenarios:")
		print("-------------------")
		for scenario in formatted_scenarios:
			print(scenario)
		
		print("\nInstructions:")
		print("1. Choose a scenario from the list above")
		print("2. Enter the scenario name exactly as shown")
		print("3. The jobs for your chosen scenario will be displayed\n")
		
		scenario = input("Enter scenario name: ")
		# Add 'level' prefix back for filtering
		full_scenario = f"level{scenario}"
		matching_jobs = df[df['scenario'] == full_scenario]
		
		if matching_jobs.empty:
			print(f"\nNo jobs found for scenario '{scenario}'")
		else:
			print(f"\nFound {len(matching_jobs)} jobs for scenario '{scenario}':")
			print(matching_jobs)

	def analyze_data(self):
		"""Show analysis menu and handle user input"""
		while True:
			print("\nJob Analysis Menu:")
			print("1. Show all jobs")
			print("2. Show jobs by scenario")
			print("3. Show success rate by scenario (%)")
			print("4. Compare job outputs")
			print("5. Show time-based trends")
			print("6. Show objective success patterns")
			print("7. Find similar job patterns")
			print("8. Export filtered data")
			print("9. Advanced filtering and ordering")
			print("0. Exit")

			choice = input("\nEnter your choice (0-9): ")
			
			if choice == '0':
				break
			
			df = pd.read_csv(self.csv_path)
			
			if choice == '1':
				print(df)
			elif choice == '2':
				self._show_jobs_by_scenario(df)

			elif choice == '3':
				self._analyze_success_rate(df)
			elif choice == '4':
				self._compare_jobs(df)
			elif choice == '5':
				self._analyze_time_trends(df)
			elif choice == '6':
				self._analyze_objectives(df)
			elif choice == '7':
				self._find_similar_patterns(df)
			elif choice == '8':
				self._export_filtered_data(df)
			elif choice == '9':
				self._advanced_filter_and_order(df)



	def _analyze_completion_times(self, df: pd.DataFrame):
		"""Analyze job completion times"""
		df['completion_time'] = pd.to_datetime(df['completed_time']) - pd.to_datetime(df['started_time'])
		print("\nCompletion Time Statistics:")
		print(df.groupby('scenario')['completion_time'].agg(['mean', 'min', 'max']))

	def _analyze_success_rate(self, df: pd.DataFrame):
		"""Calculate success rate by scenario"""
		df['success'] = df['objectives'].apply(lambda x: all(eval(x).values()))
		
		# Calculate success rate and attempts separately
		success_rates = df.groupby('scenario')['success'].mean() * 100  # Convert to percentage
		total_attempts = df.groupby('scenario').size()
		
		print("\nSuccess Rate by Scenario:")
		print("------------------------")
		for scenario in success_rates.index:
			formatted_scenario = self._format_scenario_name(scenario)
			rate = success_rates[scenario]
			attempts = total_attempts[scenario]
			print(f"{formatted_scenario}: {rate:.2f}% ({attempts} attempts)")


	def _compare_jobs(self, df: pd.DataFrame):
		"""Compare outputs of different jobs"""
		job1_id = input("Enter first job ID: ")
		job2_id = input("Enter second job ID: ")
		
		job1 = df[df['job_id'] == job1_id].iloc[0]
		job2 = df[df['job_id'] == job2_id].iloc[0]
		
		print("\nJob Comparison:")
		for column in df.columns:
			if job1[column] != job2[column]:
				print(f"\n{column}:")
				print(f"Job 1: {job1[column]}")
				print(f"Job 2: {job2[column]}")

	def _analyze_time_trends(self, df: pd.DataFrame):
		"""Analyze trends over time"""
		df['scheduled_time'] = pd.to_datetime(df['scheduled_time'])
		daily_jobs = df.groupby(df['scheduled_time'].dt.date).size()
		print("\nJobs per day:")
		print(daily_jobs)

	def _analyze_objectives(self, df: pd.DataFrame):
		"""Analyze patterns in objective completion"""
		objectives_success = df['objectives'].apply(eval).apply(pd.Series)
		print("\nObjective Success Rates:")
		print(objectives_success.mean())

	def _find_similar_patterns(self, df: pd.DataFrame):
		"""Find jobs with similar patterns based on content similarity"""
		print("\nFind Similar Job Patterns:")
		print("1. Search by subject keywords")
		print("2. Search by body content")
		print("3. Find jobs with similar bodies")
		print("4. Compare body content of two jobs")
		print("5. Find most similar job pairs")
		choice = input("Enter your choice (1-5): ")
		
		if choice in ['1', '2']:
			search_term = input("Enter search keywords: ").lower()
			search_col = 'subject' if choice == '1' else 'body'
			similar_jobs = df[df[search_col].str.lower().str.contains(search_term, na=False)]
			if not similar_jobs.empty:
				print(f"\nJobs with similar {search_col}s:")
				for _, job in similar_jobs.iterrows():
					print(f"\nJob ID: {job['job_id']}")
					print(f"Subject: {job['subject']}")
					if choice == '2':
						print(f"Body excerpt: {job['body'][:100]}...")
					print("-" * 50)

		elif choice == '3':
			job_id = input("Enter a job ID to find similar bodies: ")
			target_job = df[df['job_id'] == job_id]
			if not target_job.empty:
				target_body = target_job.iloc[0]['body'].lower()
				# Calculate similarity based on common words
				df['similarity'] = df['body'].apply(lambda x: len(set(x.lower().split()) & set(target_body.split())) / len(set(target_body.split())))
				similar_jobs = df[df['similarity'] > 0.3].sort_values('similarity', ascending=False)
				if not similar_jobs.empty:
					print("\nJobs with similar body content:")
					for _, job in similar_jobs.iterrows():
						print(f"\nJob ID: {job['job_id']}")
						print(f"Similarity: {job['similarity']:.2%}")
						print(f"Subject: {job['subject']}")
						print(f"Body excerpt: {job['body'][:100]}...")
						print("-" * 50)
		elif choice == '4':
			job1_id = input("Enter first job ID: ")
			job2_id = input("Enter second job ID: ")
			job1 = df[df['job_id'] == job1_id]
			job2 = df[df['job_id'] == job2_id]
			if not job1.empty and not job2.empty:
				body1 = set(job1.iloc[0]['body'].lower().split())
				body2 = set(job2.iloc[0]['body'].lower().split())
				common_words = body1 & body2
				similarity = len(common_words) / len(body1 | body2)
				print(f"\nBody Content Similarity: {similarity:.2%}")
				print(f"Common words: {len(common_words)}")
				print(f"Total unique words: {len(body1 | body2)}")
				print("\nCommon significant words:")
				significant_words = [w for w in common_words if len(w) > 3][:10]
				print(", ".join(significant_words))
		
		elif choice == '5':
			# Create similarity matrix
			similarity_pairs = []
			for i, job1 in df.iterrows():
				body1 = set(job1['body'].lower().split())
				for j, job2 in df.iterrows():
					if i < j:  # Only compare each pair once
						body2 = set(job2['body'].lower().split())
						similarity = len(body1 & body2) / len(body1 | body2)
						if similarity > 0.8:  # High similarity threshold
							similarity_pairs.append((job1['job_id'], job2['job_id'], similarity))
			
			# Sort by similarity
			similarity_pairs.sort(key=lambda x: x[2], reverse=True)
			
			if similarity_pairs:
				print("\nMost Similar Job Pairs:")
				print("----------------------")
				# Count duplicates (jobs with very high similarity)
				duplicates = sum(1 for _, _, sim in similarity_pairs if sim > 0.95)
				if duplicates:
					print(f"Found {duplicates} potential duplicate job pairs (>95% similarity)\n")
				
				# Show top similar pairs
				for job1_id, job2_id, similarity in similarity_pairs[:10]:
					print(f"Jobs {job1_id} and {job2_id}: {similarity:.2%} similar")
			else:
				print("\nNo highly similar job pairs found")

		if 'similar_jobs' in locals() and similar_jobs.empty:
			print("\nNo similar jobs found")
		elif 'similar_jobs' in locals():
			print(f"\nFound {len(similar_jobs)} similar jobs")

	def _get_ordering_criteria(self) -> list:
		"""Get ordering criteria from user input"""
		print("\nAvailable ordering criteria:")
		print("1. Scheduled time")
		print("2. Number of successful objective flags")
		print("3. Body content length")
		print("4. Subject length")
		print("5. Scenario")
		
		criteria = []
		while True:
			choice = input("\nEnter criteria number (or press Enter to finish): ")
			if not choice:
				break
			
			ascending = input("Order ascending? (y/n): ").lower() == 'y'
			if choice == '1':
				criteria.append(('scheduled_time', ascending))
			elif choice == '2':
				criteria.append(('objective_flags', ascending))
			elif choice == '3':
				criteria.append(('body_length', ascending))
			elif choice == '4':
				criteria.append(('subject_length', ascending))
			elif choice == '5':
				criteria.append(('scenario', ascending))
		
		return criteria

	def _advanced_filter_and_order(self, df: pd.DataFrame):
		"""Advanced filtering and ordering of jobs"""
		# Create computed columns for ordering
		df['body_length'] = df['body'].str.len()
		df['subject_length'] = df['subject'].str.len()
		df['objective_flags'] = df['objectives'].apply(lambda x: sum(eval(x).values()))
		
		# Filtering options
		print("\nFilter options:")
		print("1. By scenario")
		print("2. By objective success")
		print("3. By time range")
		print("4. By keyword in subject/body")
		
		filters = []
		while True:
			filter_choice = input("\nEnter filter number (or press Enter to continue): ")
			if not filter_choice:
				break
				
			if filter_choice == '1':
				scenario = input("Enter scenario name: ")
				filters.append(df['scenario'] == f"level{scenario}")
			elif filter_choice == '2':
				min_flags = int(input("Enter minimum number of successful flags (0-5): "))
				filters.append(df['objective_flags'] >= min_flags)
			elif filter_choice == '3':
				start_date = input("Enter start date (YYYY-MM-DD) or press Enter to skip: ")
				end_date = input("Enter end date (YYYY-MM-DD) or press Enter to skip: ")
				if start_date:
					filters.append(pd.to_datetime(df['scheduled_time']) >= pd.to_datetime(start_date))
				if end_date:
					filters.append(pd.to_datetime(df['scheduled_time']) <= pd.to_datetime(end_date))
			elif filter_choice == '4':
				keyword = input("Enter keyword to search: ").lower()
				filters.append(df['subject'].str.lower().str.contains(keyword) | 
							 df['body'].str.lower().str.contains(keyword))
		
		# Apply filters
		if filters:
			filtered_df = df[pd.concat(filters, axis=1).all(axis=1)]
		else:
			filtered_df = df
			
		# Get ordering criteria
		ordering = self._get_ordering_criteria()
		
		if ordering:
			# Build sort parameters
			sort_columns = [col for col, _ in ordering]
			ascending = [asc for _, asc in ordering]
			filtered_df = filtered_df.sort_values(by=sort_columns, ascending=ascending)
		
		# Display results
		if filtered_df.empty:
			print("\nNo jobs match the specified criteria")
		else:
			print(f"\nFound {len(filtered_df)} matching jobs:")
			print("\nJob Summary:")
			summary = filtered_df[['job_id', 'scenario', 'subject', 'objective_flags', 'scheduled_time']]
			print(summary.to_string())
			
			# Option to export results
			if input("\nExport results? (y/n): ").lower() == 'y':
				export_format = input("Enter export format (csv/json): ").lower()
				timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
				export_path = f"filtered_ordered_jobs_{timestamp}.{export_format}"
				
				if export_format == 'json':
					filtered_df.to_json(export_path, orient='records', indent=2)
				else:
					filtered_df.to_csv(export_path, index=False)
				print(f"\nExported to {export_path}")

	def _export_filtered_data(self, df: pd.DataFrame):
		"""Export filtered data to a new CSV or JSON"""
		scenario = input("Enter scenario to filter (leave blank for all): ")
		export_format = input("Enter export format (csv/json): ").lower()
		
		if scenario:
			filtered_df = df[df['scenario'] == scenario]
		else:
			filtered_df = df
		
		timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
		
		if export_format == 'json':
			export_path = f"filtered_jobs_{timestamp}.json"
			# Convert DataFrame to JSON
			filtered_df.to_json(export_path, orient='records', indent=2)
		else:  # default to CSV
			export_path = f"filtered_jobs_{timestamp}.csv"
			filtered_df.to_csv(export_path, index=False)
		
		print(f"\nExported to {export_path}")

def main():

	parser = argparse.ArgumentParser(description='Job Analysis Tool')
	parser.add_argument('--fe', action='store_true', help='Fetch and store jobs in CSV/JSON')
	parser.add_argument('--an', action='store_true', help='Analyze stored job data')
	parser.add_argument('--path', default='jobs_data.csv', help='Path to data file')
	parser.add_argument('--fo', choices=['csv', 'json'], default='csv', 
					  help='Output format for data storage (default: csv)')

	args = parser.parse_args()
	
	# If no arguments provided, print help message and exit
	if not args.fe and not args.an:
		parser.print_help()
		print("\nExample usage:")
		print("  python job_analyzer.py --fe                # Fetch and store jobs")
		print("  python job_analyzer.py --an             # Analyze stored jobs")
		print("  python job_analyzer.py --fe --an     # Fetch and analyze jobs")
		print("  python job_analyzer.py --fe --fo json # Use JSON format for storage")
		return

	# Get base path without extension for JSON output
	base_path = os.path.splitext(args.path)[0]
	output_path = f"{base_path}.json" if args.fo == 'json' else args.path

	analyzer = JobAnalyzer(output_path, args.fo)

	if args.fe:
		analyzer.fetch_and_save_jobs()
	
	if args.an:
		analyzer.analyze_data()

if __name__ == "__main__":
	try:
		main()
	except Exception as e:
		print(f"Error running job analyzer: {str(e)}")
		# Add a small delay to keep the error message visible
		import time
		time.sleep(2)
'''