import json
import random # استيراد مكتبة random لاختيار الذكر عشوائياً
from importlib import resources 

# اسم الملف داخليًا
DATA_FILE = 'azkar_data.json'

def _load_azkar_list():
    """تحميل قائمة الأذكار من ملف JSON داخل الحزمة."""
    try:
        # استخدام importlib.resources لقراءة الملف المضمّن
        data = resources.files('azkar_local_client').joinpath(DATA_FILE).read_text(encoding='utf-8')
        return json.loads(data)
    except Exception as e:
        # الإبلاغ عن فشل في قراءة ملف الأذكار الأساسي
        raise FileNotFoundError(f"فشل في تحميل قائمة الأذكار من الملف الداخلي: {e}")

def get_random_zikr():
    """
    تقوم بجلب ذكر عشوائي من القائمة المحفوظة.
    """
    # 1. تحميل القائمة
    azkar_list = _load_azkar_list()
    
    # 2. التحقق للتأكد من أن القائمة ليست فارغة
    if not azkar_list:
        return "لا توجد أذكار متاحة حالياً."
        
    # 3. اختيار الذكر عشوائياً
    random_zikr = random.choice(azkar_list)

    # 4. إرجاع الذكر
    return random_zikr
