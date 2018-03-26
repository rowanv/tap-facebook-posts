from setuptools import setup, find_packages

setup(name="tap-facebook-posts",
      version="0.0.3.dev1",
      description="Singer.io tap for extracting posts data from the Facebook Graph API",
      author="rowanv",
      license='Apache 2.0',
      url="https://github.com/rowanv",
      classifiers=["Programming Language :: Python :: 3 :: Only"],
      py_modules=["tap_facebook_posts"],
      install_requires=[
        'python-dateutil==2.6.0',  # This is required by singer-python,
          # without this being here explicitly, there are dependency issues
        'requests',
        'singer-python==5.0.12',
      ],
      python_requires='>=3',
      entry_points="""
          [console_scripts]
          tap-facebook-posts=tap_facebook_posts:main
      """,
      packages=["tap_facebook_posts"],
      package_data = {
          "schemas": ["tap_facebook_posts/schemas/*.json"]
      },
      include_package_data=True,
)
