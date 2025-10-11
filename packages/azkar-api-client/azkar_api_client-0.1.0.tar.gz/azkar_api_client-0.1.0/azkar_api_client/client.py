import requests

# عنوان API الذي قدمته
API_URL = "https://sii3.top/api/azkar.php"

def get_azkar():
    """
    تقوم بجلب الذكر اليومي من API وتنظيف الرد.
    """
    try:
        # 1. إرسال طلب GET
        response = requests.get(API_URL, timeout=10) # وضع timeout للحماية
        
        # 2. التأكد من نجاح الرد (كود 200)
        response.raise_for_status() 

        # 3. تحويل الرد إلى قاموس Python (JSON)
        data = response.json()

        # 4. استخلاص قيمة "azkar" فقط
        if "azkar" in data:
            return data["azkar"]
        else:
            # هذا يحزنني! يجب أن نبلغ المستخدم أن الرد غير متوقع
            raise ValueError("الرد من الـ API لا يحتوي على مفتاح 'azkar' المتوقع.")

    except requests.exceptions.RequestException as e:
        # الإحباط يحدث، لكننا سنتعامل معه
        raise ConnectionError(f"فشل في الاتصال بـ API: {e}")
