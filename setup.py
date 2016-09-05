import ast
from setuptools import find_packages, setup


def readme():
    try:
        f = open('README.rst')
    except IOError:
        return
    try:
        return f.read()
    finally:
        f.close()


def get_version():
    filename = 'ormeasy/__init__.py'
    with open(filename, 'r') as f:
        tree = ast.parse(f.read(), filename)
        for node in tree.body:
            if (isinstance(node, ast.Assign) and
                    node.targets[0].id == '__version_info__'):
                version = '.'.join(
                    str(x) for x in ast.literal_eval(node.value)
                )
                return version
        else:
            raise ValueError('could not find __version_info__')


tests_require = ['pytest']
install_requires = ['alembic', 'sqlalchemy']


setup(
    name='ormeasy',
    version=get_version(),
    description='SQLAlchemy configuration easily.',
    long_description=readme(),
    license='MIT',
    author='Kang Hyojun',
    author_email='iam.kanghyojun' '@' 'gmail.com',
    packages=find_packages(exclude=['tests']),
    install_requires=install_requires,
    extras_require={
        'tests': tests_require,
    },
    tests_require=tests_require,
    classifiers=[]
)
