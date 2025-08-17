from setuptools import setup

package_name = 'odom_receiver'

setup(
    name=package_name,
    version='0.0.0',
    packages=[package_name],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='angelina',
    maintainer_email='angelina.benhardi@gmail.com',
    description='Odom receiver ROS2 node receiving odom data from socket',
    license='MIT',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'odom_receiver = odom_receiver.odom_receiver:main',
        ],
    },
)

