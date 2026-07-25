from django.core.management.base import BaseCommand

from apps.modules.models import Module


class Command(BaseCommand):
    help = "预置三个固定业务模块记录（幂等操作）"

    def handle(self, *args, **options):
        modules = [
            {
                "code": "comic",
                "name": "AI 漫剧制作一站式系统",
                "description": "围绕内容导入、分镜工作台、结果校验与导出构成完整主链路。进入后先到模块内项目中心，再进入具体项目。",
                "icon": "🎬",
                "sort_order": 1,
            },
            {
                "code": "stock",
                "name": "AI 股票分析系统",
                "description": "以股票研究、策略判断和持续跟踪为主线，进入后直接承接股票分析模块自己的项目和工作台链路。",
                "icon": "📊",
                "sort_order": 2,
            },
            {
                "code": "blog",
                "name": "个人博客 / 个人内容库",
                "description": "围绕个人内容沉淀、整理、发布与复用展开，作为第三个固定方向出现，支持内容管理与发布。",
                "icon": "📝",
                "sort_order": 3,
            },
        ]

        created_count = 0
        for data in modules:
            _, created = Module.objects.get_or_create(
                code=data["code"],
                defaults=data,
            )
            if created:
                created_count += 1

        if created_count:
            self.stdout.write(self.style.SUCCESS(f"已创建 {created_count} 个模块"))
        else:
            self.stdout.write(self.style.SUCCESS("模块已全部就绪，无需新建"))
