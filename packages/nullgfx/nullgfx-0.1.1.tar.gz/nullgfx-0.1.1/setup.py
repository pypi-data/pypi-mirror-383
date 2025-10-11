from setuptools import setup, find_packages

setup(
    name="nullgfx",
    version="0.1.1",
    author="EnderNull Studios",
    author_email="enderyt6222@gmail.com",
    description="OpenGL but its for potatoes",
    long_description="Optimized OpenGL",
    packages=find_packages(),
    install_requires=[
        "PyOpenGL",
        "glfw",
        "numpy"
    ],
    python_requires='>=3.8',
)
