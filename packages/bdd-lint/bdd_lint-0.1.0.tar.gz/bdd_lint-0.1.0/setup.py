from setuptools import setup, find_packages
from setuptools import setup, find_packages
from pathlib import Path

here = Path(__file__).parent.resolve()
long_description = ''
try:
    long_description = (here / 'README.md').read_text(encoding='utf-8')
except Exception:
    long_description = 'bdd-lint: a linter for BDD feature files.'

setup(
    name='bdd-lint',
    version='0.1.0',
    description='A standalone linter for Gherkin feature files to enforce grammar and best practices',
    long_description=long_description,
    long_description_content_type='text/markdown',
    packages=find_packages(exclude=("tests", "build", "dist")),
    install_requires=[
        'PyYAML>=5.3.1',
    ],
    extras_require={
        'nlp': ['textblob', 'spacy', 'nltk'],
        'test': ['pytest', 'pytest-bdd'],
    },
    entry_points={
        'console_scripts': [
            'bdd-lint=bdd_lint.linter:main'
        ]
    },
    python_requires='>=3.7',
)