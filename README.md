# Archetype

ARCHETYPE is an exercise in LLM API wrappers.
It aims at building a multimodal and dynamical i.e. variable scope chatbot within one closure, in such a way that it facilitates quick templating and integration into your own macros.

## Included examples

* Dialogos - Helps users externalize emotional issues and manage them effectively.
* Thesis - Assists in planning and organizing a high school essay or thesis project.

## Requirements

* Python 3.11+
* Streamlit
* Langchain
* OpenAI API key

## Installation

* Clone the repository:
```bash
git clone <repository-url>
cd <repository-directory>
```

* Install the required packages:
```bash
pip install -r src/requirements.txt*
```

## Usage

* Run the application:
```bash
streamlit run src/main.py
```
## Contributing

Contributions are welcome! Please submit issues or pull requests for any improvements or bug fixes.
License

This project is licensed under the MIT License - see the [LICENSE.mc](LICENSE.md) file for details.

## Versioning

This project uses [commit-and-tag-version](https://github.com/absolute-version/commit-and-tag-version) to generate an automated [CHANGELOG.md](CHANGELOG.md).
Please use [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/#summary) when pushing.

Commands:

* ```bash
    make alpha # -> releases and tags as alpha
    ```

* ```bash
    make beta # -> releases and tags as beta
    ```

* ```bash
    make minor # -> releases and tags as minor
    ```

* ```bash
    make release # -> standard release and tag
    ```
