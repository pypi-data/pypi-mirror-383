from setuptools import setup, find_packages

# المكتبات الخارجية المطلوبة للتشغيل (requests)
REQUIREMENTS = [
    'requests',
]

setup(
    name='azkar-api-client', 
    version='0.1.0',
    description='مكتبة بايثون لجلب الأذكار من API محدد، مفيدة لتطبيقات إسلامية.',
    author='Your Name', # يرجى تعديل هذا
    author_email='your.email@example.com', # يرجى تعديل هذا
    url='https://github.com/yourusername/azkar-api-client', # يرجى تعديل هذا
    packages=find_packages(),
    install_requires=REQUIREMENTS, 
    license='MIT',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6', 
)
