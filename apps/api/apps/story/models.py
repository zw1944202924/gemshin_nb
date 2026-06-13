from django.conf import settings
from django.db import models

from apps.core.models import TimestampedModel


class ProjectStatus(models.TextChoices):
    DRAFT = "draft", "草稿"
    PROCESSING = "processing", "处理中"
    COMPLETED = "completed", "已完成"
    FAILED = "failed", "失败"


class ShotStatus(models.TextChoices):
    PENDING = "pending", "待处理"
    PROCESSING = "processing", "处理中"
    COMPLETED = "completed", "已完成"
    FAILED = "failed", "失败"


class AssetType(models.TextChoices):
    IMAGE = "image", "图片"
    VIDEO = "video", "视频"
    AUDIO = "audio", "音频"
    SUBTITLE = "subtitle", "字幕"


class AssetStatus(models.TextChoices):
    PENDING = "pending", "待生成"
    PROCESSING = "processing", "生成中"
    COMPLETED = "completed", "已完成"
    FAILED = "failed", "失败"
    STALE = "stale", "待更新"
    OUTDATED = "outdated", "已过期"


class JobType(models.TextChoices):
    STORY_OUTLINE = "story_outline", "剧情整理"
    STORYBOARD = "storyboard", "分镜脚本"
    IMAGE_GENERATION = "image_generation", "图片生成"
    VIDEO_GENERATION = "video_generation", "视频生成"
    VOICE_GENERATION = "voice_generation", "配音生成"


class JobStatus(models.TextChoices):
    PENDING = "pending", "等待中"
    PROCESSING = "processing", "处理中"
    COMPLETED = "completed", "已完成"
    FAILED = "failed", "失败"


class Project(TimestampedModel):
    """项目 —— 一个漫剧作品的总容器"""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="projects",
    )
    title = models.CharField("标题", max_length=255)
    description = models.TextField("描述", blank=True, default="")
    status = models.CharField(
        "状态",
        max_length=20,
        choices=ProjectStatus.choices,
        default=ProjectStatus.DRAFT,
    )
    config = models.JSONField("项目配置", default=dict, blank=True)

    class Meta:
        db_table = "story_projects"
        ordering = ["-updated_at", "-id"]
        indexes = [
            models.Index(fields=["user", "-updated_at"]),
            models.Index(fields=["user", "status"]),
        ]

    def __str__(self):
        return self.title


class Shot(TimestampedModel):
    """分镜 —— 项目中的单个镜头"""
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name="shots",
    )
    order = models.PositiveIntegerField("序号")
    description = models.TextField("分镜描述", blank=True, default="")
    status = models.CharField(
        "状态",
        max_length=20,
        choices=ShotStatus.choices,
        default=ShotStatus.PENDING,
    )
    settings = models.JSONField("镜头配置", default=dict, blank=True)

    class Meta:
        db_table = "story_shots"
        ordering = ["project", "order", "id"]
        indexes = [
            models.Index(fields=["project", "order"]),
            models.Index(fields=["project", "status"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["project", "order"],
                name="uq_shot_project_order",
            ),
        ]

    def __str__(self):
        return f"{self.project.title} / 镜头 {self.order}"


class Asset(TimestampedModel):
    """素材 —— 镜头或项目级别的产出物"""
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name="assets",
    )
    shot = models.ForeignKey(
        Shot,
        on_delete=models.CASCADE,
        related_name="assets",
        null=True,
        blank=True,
    )
    asset_type = models.CharField(
        "素材类型",
        max_length=20,
        choices=AssetType.choices,
    )
    file_path = models.CharField("文件路径", max_length=500, blank=True, default="")
    file_size = models.BigIntegerField("文件大小(字节)", default=0)
    status = models.CharField(
        "状态",
        max_length=20,
        choices=AssetStatus.choices,
        default=AssetStatus.PENDING,
    )
    is_stale = models.BooleanField("是否待更新", default=False)
    outdated_by = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="superseded_assets",
    )
    metadata = models.JSONField("元数据", default=dict, blank=True)

    class Meta:
        db_table = "story_assets"
        ordering = ["project", "shot", "asset_type", "-updated_at", "-id"]
        indexes = [
            models.Index(fields=["project", "asset_type"]),
            models.Index(fields=["shot", "asset_type"]),
            models.Index(fields=["project", "is_stale"]),
            models.Index(fields=["project", "status"]),
        ]

    def __str__(self):
        label = self.shot.order if self.shot else "项目级"
        return f"{self.project.title} / {label} / {self.get_asset_type_display()}"


class Job(TimestampedModel):
    """任务 —— 不可覆盖的执行记录"""
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name="jobs",
    )
    shot = models.ForeignKey(
        Shot,
        on_delete=models.CASCADE,
        related_name="jobs",
        null=True,
        blank=True,
    )
    job_type = models.CharField(
        "任务类型",
        max_length=30,
        choices=JobType.choices,
    )
    status = models.CharField(
        "状态",
        max_length=20,
        choices=JobStatus.choices,
        default=JobStatus.PENDING,
    )
    input_data = models.JSONField("输入数据", default=dict, blank=True)
    output_data = models.JSONField("输出数据", default=dict, blank=True)
    retry_of = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="retries",
    )
    attempt = models.PositiveSmallIntegerField("尝试次数", default=1)
    started_at = models.DateTimeField("开始时间", null=True, blank=True)
    completed_at = models.DateTimeField("完成时间", null=True, blank=True)
    error_message = models.TextField("错误信息", blank=True, default="")

    class Meta:
        db_table = "story_jobs"
        ordering = ["project", "-created_at", "-id"]
        indexes = [
            models.Index(fields=["project", "job_type"]),
            models.Index(fields=["shot", "job_type"]),
            models.Index(fields=["project", "status"]),
            models.Index(fields=["project", "job_type", "status"]),
        ]

    def __str__(self):
        scope = f"镜头 {self.shot.order}" if self.shot else "项目级"
        return f"{self.project.title} / {scope} / {self.get_job_type_display()} #{self.attempt}"
