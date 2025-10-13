from setuptools import setup, find_packages

setup(
    name="alt-legibilidade",
    version="0.1.2",
    author="Equipe ALT",
    author_email="marcopolo@unir.br", 
    description="Ferramenta para análise de legibilidade de textos em português",
    long_description="Ferramenta do projeto ALT (https://legibilidade.com) para contar letras, palavras, sílabas, frases e calcular índices como Flesch, Gunning Fog, ARI, CLI e Gulpease em língua portuguesa. Suporta arquivos .txt, .pdf e .docx.",
    long_description_content_type="text/markdown",
    url="https://github.com/marcopolomoreno/alt-python",
    packages=find_packages(),
    include_package_data=True,
    package_data={
        "alt_legibilidade": ["banco/*.txt", "banco/*.csv", "banco/*.json"],
    },
    install_requires=[
        "pymupdf",
        "python-docx"
    ],
    entry_points={
        "console_scripts": [
            "alt-legibilidade = alt_legibilidade.cli:main"
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Natural Language :: Portuguese"
    ],
    python_requires='>=3.7',
    license="MIT",
)
