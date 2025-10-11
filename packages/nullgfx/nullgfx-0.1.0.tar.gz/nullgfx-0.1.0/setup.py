from setuptools import setup, find_packages

setup(
    name="nullgfx",
    version="0.1.0",
    author="EnderNull Studios",
    author_email="youremail@example.com",
    description="Opytimized OpenGL",
    long_description="Optimized OpenGL",
    packages=find_packages(),
    install_requires=[
        "PyOpenGL",
        "glfw",
        "numpy"
    ],
    python_requires='>=3.8',
)
