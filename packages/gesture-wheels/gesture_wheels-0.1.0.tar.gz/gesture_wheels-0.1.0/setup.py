from setuptools import setup, find_packages
setup(
    name='gesture-wheels',
    version='0.1.0',
    packages=find_packages(),
    install_requires=['opencv-python', 'mediapipe', 'pyserial'],
    description='Control ESP32 wheeled robots with hand gestures',
    author='Your Name',
    python_requires='>=3.7',
)
