from setuptools import setup, find_packages

setup(
    name='indico-plugin-phonebook',
    version='1.0.1',
    description='Webhook endpoint to sync categories from the phonebook',
    author='You',
    packages=find_packages(),
    zip_safe=False,
    include_package_data=True,
    install_requires=[
        'requests>=2.32.3',
        'jsonschema>=4.23.0'
    ],
    entry_points={
        'indico.plugins': {
            'phonebook = indico_plugin_phonebook.plugin:PhonebookPlugin'
        }
    }
)

