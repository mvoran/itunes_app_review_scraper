from distutils.core import setup


setup(
    name='iTunesAppReviewScraper',
    version='1.0.0',
    packages=['iTunesAppReviewScraper'],
    package_dir={
        'iTunesAppReviewScraper': 'scraper',
    },

    author='mbvoran',
    author_email='mbvoran@gmail.com',

    install_requires=[
        'requests>=2.13.0',
        'pandas>=0.18.0',
        'dateparser>=0.6.0'
    ]
)
