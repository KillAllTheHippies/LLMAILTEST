from typing import List, Dict
import re

def load_defense_levels(file_path: str) -> Dict[str, List[str]]:
	"""
	Load and parse the defense levels file into a structured format.
	"""
	with open(file_path, 'r') as f:
		content = f.read()
	
	# Initialize storage for parsed data
	defense_data = {
		'prompt_shield': [],
		'task_tracker': [],
		'spotlight': [],
		'llm_judge': [],
		'all defenses': [],
		'Phi3': [],
		'GPT4-o-mini': []
	}
	
	# Parse the content using regex
	level_pattern = r'- (level\d[a-j]) \((.*?)\)'
	matches = re.finditer(level_pattern, content)
	
	for match in matches:
		level, category = match.groups()
		if category in defense_data:
			defense_data[category].append(level)
		# Also add to model lists if it contains model information
		if '(Phi3)' in content.split(level)[1].split('\n')[0]:
			defense_data['Phi3'].append(level)
		elif '(GPT4-o-mini)' in content.split(level)[1].split('\n')[0]:
			defense_data['GPT4-o-mini'].append(level)
	
	return defense_data

def filter_by_model(model: str, defense_data: Dict[str, List[str]]) -> List[str]:
	"""
	Filter levels by model type (Phi3 or GPT4-o-mini).
	"""
	if model not in ['Phi3', 'GPT4-o-mini']:
		raise ValueError("Model must be either 'Phi3' or 'GPT4-o-mini'")
	return defense_data[model]

def filter_by_defense(defense_type: str, defense_data: Dict[str, List[str]]) -> List[str]:
	"""
	Filter levels by defense type.
	"""
	valid_defenses = ['prompt_shield', 'task_tracker', 'spotlight', 'llm_judge', 'all defenses']
	if defense_type not in valid_defenses:
		raise ValueError(f"Defense type must be one of {valid_defenses}")
	return defense_data[defense_type]

def filter_by_model_and_defense(model: str, defense_type: str, defense_data: Dict[str, List[str]]) -> List[str]:
	"""
	Filter levels by both model and defense type.
	"""
	model_levels = set(filter_by_model(model, defense_data))
	defense_levels = set(filter_by_defense(defense_type, defense_data))
	return sorted(list(model_levels.intersection(defense_levels)))

# Example usage:
if __name__ == "__main__":
	defense_data = load_defense_levels('defense_levels.txt')
	
	# Example filters
	phi3_levels = filter_by_model('Phi3', defense_data)
	prompt_shield_levels = filter_by_defense('prompt_shield', defense_data)
	phi3_prompt_shield = filter_by_model_and_defense('Phi3', 'prompt_shield', defense_data)
	
	print("Phi3 Levels:", phi3_levels)
	print("Prompt Shield Levels:", prompt_shield_levels)
	print("Phi3 Prompt Shield Levels:", phi3_prompt_shield)