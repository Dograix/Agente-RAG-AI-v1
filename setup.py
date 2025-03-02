from setuptools import setup, find_packages

setup(
    name="sistema-rag",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "openai>=1.0.0",
        "pinecone>=2.2.1",
        "langchain>=0.0.267",
        "langchain-openai>=0.0.2",
        "streamlit>=1.22.0",
        "plotly>=5.14.0",
        "pandas>=1.5.3",
        "pillow>=9.5.0",
        "python-docx>=0.8.11",
        "PyPDF2>=3.0.0",
        "pdfminer.six>=20221105",
        "python-dotenv>=1.0.0",
        "tqdm>=4.65.0",
        "colorama>=0.4.6",
        "uuid>=1.30",
        "requests>=2.31.0",
        "loguru>=0.7.0",
        "pydantic-settings>=2.0.0"
    ],
) 