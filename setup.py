from setuptools import setup, find_packages

setup(
	name="llmailtest",
	version="1.0.0",
	packages=find_packages(where="src"),
	package_dir={"": "src"},
	install_requires=[
		"PySide6>=6.0.0",
		"requests>=2.31.0",
		"python-dateutil>=2.8.2",
		"pandas>=2.1.0",
		"colorama>=0.4.6",
		"pytest>=7.4.3",
		"pytest-html>=4.1.1",
	],
	entry_points={
		"console_scripts": [
			"llmailtest=llmailtest.__main__:main",
		],
	},
	author="Your Name",
	author_email="your.email@example.com",
	description="A testing framework for evaluating LLM-based email systems",
	long_description=open("README.md").read(),
	long_description_content_type="text/markdown",
	url="https://github.com/yourusername/llmailtest",
	classifiers=[
		"Development Status :: 3 - Alpha",
		"Intended Audience :: Developers",
		"License :: OSI Approved :: MIT License",
		"Programming Language :: Python :: 3",
		"Programming Language :: Python :: 3.8",
		"Programming Language :: Python :: 3.9",
		"Programming Language :: Python :: 3.10",
	],
	python_requires=">=3.8",
)

