class SiteSettingsMiddleware:
    """میان‌افزار ساده جهت آماده‌سازی برای کش تنظیمات سایت در آینده (فاز Performance)"""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response
