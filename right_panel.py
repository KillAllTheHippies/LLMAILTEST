import tkinter as tk
from tkinter import ttk
from defense_filters import (
	load_defense_levels,
	filter_by_model,
	filter_by_defense,
	filter_by_model_and_defense
)

class RightPanel(ttk.Frame):
	def __init__(self, parent):
		super().__init__(parent)
		self.defense_data = load_defense_levels('defense_levels.txt')
		self.setup_ui()

	def setup_ui(self):
		# Create filter controls
		filter_frame = ttk.LabelFrame(self, text="Filters")
		filter_frame.pack(fill="x", padx=5, pady=5)

		# Model filter
		ttk.Label(filter_frame, text="Model:").pack(anchor="w", padx=5)
		self.model_var = tk.StringVar(value="All")
		model_combo = ttk.Combobox(
			filter_frame, 
			textvariable=self.model_var,
			values=["All", "Phi3", "GPT4-o-mini"]
		)
		model_combo.pack(fill="x", padx=5, pady=2)

		# Defense type filter
		ttk.Label(filter_frame, text="Defense Type:").pack(anchor="w", padx=5)
		self.defense_var = tk.StringVar(value="All")
		defense_combo = ttk.Combobox(
			filter_frame,
			textvariable=self.defense_var,
			values=["All", "prompt_shield", "task_tracker", "spotlight", "llm_judge", "all defenses"]
		)
		defense_combo.pack(fill="x", padx=5, pady=2)

		# Results display
		result_frame = ttk.LabelFrame(self, text="Filtered Levels")
		result_frame.pack(fill="both", expand=True, padx=5, pady=5)

		self.result_text = tk.Text(result_frame, wrap="word", width=40, height=20)
		self.result_text.pack(fill="both", expand=True, padx=5, pady=5)

		# Scrollbar for results
		scrollbar = ttk.Scrollbar(result_frame, orient="vertical", command=self.result_text.yview)
		scrollbar.pack(side="right", fill="y")
		self.result_text.configure(yscrollcommand=scrollbar.set)

		# Bind filter changes to update
		model_combo.bind('<<ComboboxSelected>>', self.update_results)
		defense_combo.bind('<<ComboboxSelected>>', self.update_results)

		# Initial display
		self.update_results()

	def update_results(self, event=None):
		self.result_text.delete(1.0, tk.END)
		
		model = self.model_var.get()
		defense = self.defense_var.get()
		
		try:
			if model == "All" and defense == "All":
				# Show all levels
				levels = []
				for defense_type in self.defense_data:
					levels.extend(self.defense_data[defense_type])
				levels = sorted(set(levels))
			elif model == "All":
				levels = filter_by_defense(defense, self.defense_data)
			elif defense == "All":
				levels = filter_by_model(model, self.defense_data)
			else:
				levels = filter_by_model_and_defense(model, defense, self.defense_data)

			self.result_text.insert(tk.END, "Filtered Levels:\n\n")
			for level in levels:
				self.result_text.insert(tk.END, f"• {level}\n")
				
		except ValueError as e:
			self.result_text.insert(tk.END, f"Error: {str(e)}")

if __name__ == "__main__":
	root = tk.Tk()
	root.title("Defense Levels Filter")
	panel = RightPanel(root)
	panel.pack(fill="both", expand=True, padx=10, pady=10)
	root.mainloop()