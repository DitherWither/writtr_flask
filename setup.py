from setuptools import setup,find_packages

setup(
    name='blog_mgr',
    version='0.1',
    description='A web application to manage a blog webpage made in flask',
    # TODO: Add url after uploaded to github
    author='DitherWither',
    author_email='demonslayervardhan@gmail.com',
    zip_safe=False,
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'Flask',
        'Flask-Markdown',
        'psycopg2-binary',
        'python-dotenv'
    ]
)
