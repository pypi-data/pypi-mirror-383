from setuptools import setup, find_packages

with open("README.md", "r", encoding="UTF-8") as f:
    readme = f.read()

setup(
    name="aionetschool",
    version="1.0.1",
    description="Неофициальная Python-библиотека для работы с API инстансов "
    "сервиса «Сетевой Город. Образование»",
    long_description=readme,
    long_description_content_type="text/markdown",
    author="kamekuro",
    author_email="me@kamekuro.ru",
    url="https://github.com/kamekuro/aionetschool",
    packages=find_packages(),
    classifiers=[
        "License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)",
        "Natural Language :: Russian",
    ],
    keywords="python netschool netcity api wrapper library client "
    "питон пайтон нетскул сетевой город апи обёртка библиотека клиент",
    license="AGPLv3+",
    install_requires=open("requirements.txt", "r", encoding="UTF-8")
    .read()
    .strip()
    .split("\n"),
    python_requires=">=3.10",
)
