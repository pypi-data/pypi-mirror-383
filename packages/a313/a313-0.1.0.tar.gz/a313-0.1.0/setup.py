from setuptools import setup, find_packages

setup(
    name='a313', 
    version='0.1.0',
    description='مكتبة بايثون لجلب الأذكار بالترتيب من قائمة محلية.',
    author='tofey', 
    packages=find_packages(),
    
    # هذا السطر يخبر pip بتضمين ملف a313_data.json
    package_data={
        'a313': ['a313_data.json'],
    },
    
    install_requires=[], # لا يوجد متطلبات خارجية الآن!
    license='MIT',
    python_requires='>=3.8', # نرفع المتطلب لأننا نستخدم importlib.resources
)
