# from setuptools import setup

# setup(
#     name="distributions",
#     version="0.1",
#     description="Gaussian distributions",
#     packages=["distributions"],
#     zip_safe=False,
# )

from setuptools import setup

setup(
    name='ubajaka_distributions',  # <-- change this line
    version='0.1',
    description='Gaussian and Binomial distributions package',
    author='Ubajaka Chijioke',
    author_email='your_email@example.com',
    packages=['distributions'],
    zip_safe=False
)



# twine upload dist/* -u __token__ -p pypi-AgEIcHlwaS5vcmcCJDA2YWUwZWE0LThkOGItNDUxZi1hMDYwLTgwN2UyYzZmNjVjOQACKlszLCI1ZGFhNTQ1OC1jN2RiLTRmYjctYmYyOS0wNTVkZmFkNDQ5YzgiXQAABiA8ZgBxSA8cCfeGwYrLH8lF--n5dTjub3IaqE5SekpVvA