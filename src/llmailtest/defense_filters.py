def load_defense_levels(filename):
	"""
	Load defense level configurations from a file.
	
	Args:
		filename: Path to defense levels configuration file
		
	Returns:
		Dictionary mapping defense mechanisms to their applicable levels
	"""
	defense_data = {
		'Phi3': set(),
		'GPT4-o-mini': set(),
		'prompt_shield': set(),
		'task_tracker': set(),
		'spotlight': set(),
		'llm_judge': set(),
		'all': set()
	}
	
	try:
		with open(filename, 'r') as f:
			for line in f:
				line = line.strip()
				if line and not line.startswith('#'):
					parts = line.split(':')
					if len(parts) == 2:
						defense, levels = parts
						defense = defense.strip()
						levels = set(level.strip().lower() for level in levels.split(','))
						if defense in defense_data:
							defense_data[defense].update(levels)
	except FileNotFoundError:
		# Return empty sets if file not found
		pass
		
	return defense_data