from setuptools import setup, find_packages

setup(
    name='yfinance_fetch',
    version='0.0.1',
    description='A module for analyzing stock technical, financial, and candlestick pattern data with yfinance and Google Sheets integration.',
    author='Prasad',
    author_email='mr.xprasadx@gmail.com',
    # url='https://github.com/yourusername/stock_analysis',  # Optional: Update with your repo URL
    packages=find_packages(),
    install_requires=[
        'yfinance>=0.2.40',
        'pandas>=2.0.0',
        'numpy>=1.24.0',
        'requests>=2.31.0',
        'tqdm>=4.66.0',
        'ta>=0.10.2',
        'gspread>=5.12.0',
        'oauth2client>=4.1.3',
        'gspread-dataframe>=3.3.0'
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.8',
)