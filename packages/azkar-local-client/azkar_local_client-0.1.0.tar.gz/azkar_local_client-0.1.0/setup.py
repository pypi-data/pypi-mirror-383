from setuptools import setup, find_packages

setup(
    name='azkar-local-client', 
    version='0.1.0',
    description='مكتبة بايثون لجلب الأذكار بالترتيب من قائمة محلية.',
    author='Your Name', 
    packages=find_packages(),
    
    # هذا السطر يخبر pip بتضمين ملف azkar_data.json
    package_data={
        'azkar_local_client': ['azkar_data.json'],
    },
    
    install_requires=[], # لا يوجد متطلبات خارجية الآن!
    license='MIT',
    python_requires='>=3.8', # نرفع المتطلب لأننا نستخدم importlib.resources
)
