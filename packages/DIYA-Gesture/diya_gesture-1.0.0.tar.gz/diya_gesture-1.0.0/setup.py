from setuptools import setup, find_packages

setup(
    name='DIYA-Gesture',  # the PyPI package name
    version='1.0.0',      # bump version for every upload
    packages=find_packages(),
    install_requires=[
        'opencv-python',
        'mediapipe',
        'pyserial'
    ],
    description='Control ESP32 robots using hand gestures (DIYA Robotics Edition)',
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    author='DIYA Robotics',
    author_email='learn@diyaedulabs.com',
    python_requires='>=3.7',
    url='https://github.com/diyarobotics/DIYA_Gesture',  # optional
    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
        'Topic :: Education',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
    ],
)
