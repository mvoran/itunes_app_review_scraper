from distutils.core import setup


setup(
    name='itunes_app_review_scraper',
    version='1.0.0',
    packages=['itunes_app_review_scraper'],
    package_dir={
        'itunes_app_review_scraper': 'scraper',
    },

    author='mbvoran',
    author_email='mbvoran@gmail.com',

    install_requires=[
        'requests>=2.13.0',
        'pandas>=0.18.0',
        'dateparser>=0.6.0'
    ]
)
