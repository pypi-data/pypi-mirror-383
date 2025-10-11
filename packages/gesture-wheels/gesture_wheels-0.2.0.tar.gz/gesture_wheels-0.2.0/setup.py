from setuptools import setup, find_packages

setup(
    name='gesture-wheels',
    version='0.2.0',   # ⬅️ increase version number
    packages=find_packages(),
    install_requires=['opencv-python', 'mediapipe', 'pyserial'],
    description='Control ESP32 wheeled robots with hand gestures (via Serial)',
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    author='Your Name',
    url='https://pypi.org/project/gesture-wheels/',
    python_requires='>=3.7',
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Intended Audience :: Education",
        "Topic :: Education",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development :: Embedded Systems",
    ],
)
