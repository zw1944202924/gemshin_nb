from datetime import datetime, timezone

from django.db import transaction
from django.db.models import Count

from apps.story.models import (
    Asset,
    AssetStatus,
    AssetType,
    Job,
    JobStatus,
    JobType,
    Project,
    ProjectStatus,
    Shot,
    ShotStatus,
)


# ---------------------------------------------------------------------------
# 项目
# ---------------------------------------------------------------------------

def create_project(*, user, title: str, description: str = "", config: dict | None = None) -> Project:
    return Project.objects.create(
        user=user,
        title=title,
        description=description,
        config=config or {},
    )


def list_projects(*, user, status: str | None = None, limit: int = 50):
    qs = (
        Project.objects
        .filter(user=user)
        .annotate(shot_count=Count("shots"))
        .order_by("-updated_at", "-id")
    )
    if status:
        qs = qs.filter(status=status)
    return qs[:limit]


def get_project(*, user, project_id: int) -> Project:
    return (
        Project.objects
        .filter(user=user)
        .annotate(shot_count=Count("shots"))
        .get(id=project_id)
    )


def update_project(*, user, project_id: int, title: str | None = None, description: str | None = None, config: dict | None = None) -> Project:
    project = get_project(user=user, project_id=project_id)
    upstream_changed = False
    if title is not None and project.title != title:
        project.title = title
        upstream_changed = True
    if description is not None and project.description != description:
        project.description = description
        upstream_changed = True
    if config is not None:
        if project.config != config:
            project.config = config
            upstream_changed = True

    with transaction.atomic():
        project.save(update_fields=[f for f in ["title", "description", "config"] if locals().get(f) is not None])
        if upstream_changed:
            _mark_project_assets_stale(project)
    return project


# ---------------------------------------------------------------------------
# 分镜
# ---------------------------------------------------------------------------

def create_shot(*, user, project_id: int, order: int, description: str = "", settings: dict | None = None) -> Shot:
    project = get_project(user=user, project_id=project_id)
    return Shot.objects.create(
        project=project,
        order=order,
        description=description,
        settings=settings or {},
    )


def list_shots(*, user, project_id: int) -> list[Shot]:
    project = get_project(user=user, project_id=project_id)
    shots = list(Shot.objects.filter(project=project).order_by("order", "id"))
    asset_map = _build_asset_map(project)
    for s in shots:
        s.prefetched_assets = asset_map.get(s.id, [])
    return shots


def get_shot(*, user, shot_id: int) -> Shot:
    shot = Shot.objects.select_related("project").get(id=shot_id)
    if shot.project.user_id != user.id:
        raise Shot.DoesNotExist()
    shot.prefetched_assets = list(Asset.objects.filter(shot=shot).order_by("asset_type", "-updated_at"))
    return shot


def update_shot(*, user, shot_id: int, description: str | None = None, settings: dict | None = None) -> Shot:
    shot = get_shot(user=user, shot_id=shot_id)
    upstream_changed = False
    if description is not None and shot.description != description:
        shot.description = description
        upstream_changed = True
    if settings is not None:
        if shot.settings != settings:
            shot.settings = settings
            upstream_changed = True

    with transaction.atomic():
        shot.save(update_fields=[f for f in ["description", "settings"] if locals().get(f) is not None])
        if upstream_changed:
            _mark_shot_assets_stale(shot)
    return shot


# ---------------------------------------------------------------------------
# 素材标记传播
# ---------------------------------------------------------------------------

def _mark_project_assets_stale(project: Project):
    """上游项目级变更后，将项目级素材和所有镜头级下游素材一并标记为 stale"""
    Asset.objects.filter(project=project, status=AssetStatus.COMPLETED).update(
        is_stale=True,
        status=AssetStatus.STALE,
    )


def _mark_shot_assets_stale(shot: Shot):
    """单镜头配置变更后，将镜头级素材标记为 stale"""
    Asset.objects.filter(shot=shot, status=AssetStatus.COMPLETED).update(
        is_stale=True,
        status=AssetStatus.STALE,
    )


def _build_asset_map(project: Project) -> dict[int, list[Asset]]:
    asset_map: dict[int, list[Asset]] = {}
    for a in Asset.objects.filter(project=project, shot__isnull=False).order_by("shot", "asset_type", "-updated_at"):
        asset_map.setdefault(a.shot_id, []).append(a)
    return asset_map


# ---------------------------------------------------------------------------
# 任务
# ---------------------------------------------------------------------------

def create_job(*, user, project_id: int, shot_id: int | None, job_type: str) -> Job:
    project = get_project(user=user, project_id=project_id)
    shot = None
    if shot_id is not None:
        shot = get_shot(user=user, shot_id=shot_id)
        if shot.project_id != project.id:
            raise ValueError("分镜不属于该项目")

    if job_type not in JobType.values:
        raise ValueError(f"不支持的任务类型: {job_type}")

    # 项目级任务只能是对应的项目级类型
    if shot is None and job_type not in {JobType.STORY_OUTLINE, JobType.STORYBOARD}:
        raise ValueError("项目级任务仅支持剧情整理和分镜脚本")
    # 镜头级任务只能是对应的镜头级类型
    if shot is not None and job_type not in {JobType.IMAGE_GENERATION, JobType.VIDEO_GENERATION, JobType.VOICE_GENERATION}:
        raise ValueError("镜头级任务仅支持图片生成、视频生成和配音生成")

    return Job.objects.create(
        project=project,
        shot=shot,
        job_type=job_type,
        status=JobStatus.PENDING,
        input_data=_build_input_data(project, shot, job_type),
    )


def retry_job(*, user, job_id: int) -> Job:
    """重试 —— 生成新任务记录，不可覆盖旧记录"""
    original = _get_job_for_user(user=user, job_id=job_id)
    return Job.objects.create(
        project=original.project,
        shot=original.shot,
        job_type=original.job_type,
        status=JobStatus.PENDING,
        input_data=original.input_data,
        retry_of=original,
        attempt=original.attempt + 1,
    )


def list_jobs(*, user, project_id: int, shot_id: int | None = None, job_type: str | None = None, limit: int = 100):
    project = get_project(user=user, project_id=project_id)
    qs = Job.objects.filter(project=project).order_by("-created_at", "-id")
    if shot_id is not None:
        qs = qs.filter(shot_id=shot_id)
    if job_type is not None:
        qs = qs.filter(job_type=job_type)
    return qs[:limit]


def get_job(*, user, job_id: int) -> Job:
    return _get_job_for_user(user=user, job_id=job_id)


def _get_job_for_user(*, user, job_id: int) -> Job:
    return Job.objects.select_related("project", "shot").get(id=job_id, project__user=user)


def _build_input_data(project: Project, shot: Shot | None, job_type: str) -> dict:
    data = {
        "project_id": project.id,
        "project_title": project.title,
        "project_config": project.config,
    }
    if shot is not None:
        data["shot_id"] = shot.id
        data["shot_order"] = shot.order
        data["shot_description"] = shot.description
        data["shot_settings"] = shot.settings
    return data


# ---------------------------------------------------------------------------
# 导出
# ---------------------------------------------------------------------------

REQUIRED_ASSET_TYPES = {
    AssetType.IMAGE,
    AssetType.VIDEO,
    AssetType.AUDIO,
    AssetType.SUBTITLE,
}


def get_export_summary(*, user, project_id: int) -> dict:
    """导出摘要 —— 列出每个镜头的素材完成情况与缺口"""
    project = get_project(user=user, project_id=project_id)
    shots = Shot.objects.filter(project=project).order_by("order", "id")
    assets = Asset.objects.filter(project=project, shot__isnull=False).select_related("shot")

    asset_by_shot: dict[int, dict[str, Asset]] = {}
    for a in assets:
        asset_by_shot.setdefault(a.shot_id, {})[a.asset_type] = a

    shot_summaries = []
    total_complete = 0
    total_shots = 0

    for shot in shots:
        shot_assets = asset_by_shot.get(shot.id, {})
        status_map = {}
        missing: list[str] = []
        stale_types: list[str] = []

        for at in REQUIRED_ASSET_TYPES:
            a = shot_assets.get(at.value)
            if a is None:
                status_map[at.value] = "missing"
                missing.append(at.value)
            elif a.is_stale or a.status == AssetStatus.STALE:
                status_map[at.value] = "stale"
                stale_types.append(at.value)
            elif a.status == AssetStatus.COMPLETED:
                status_map[at.value] = "complete"
            else:
                status_map[at.value] = a.status

        is_shot_complete = len(missing) == 0 and len(stale_types) == 0
        if is_shot_complete:
            total_complete += 1
        total_shots += 1

        shot_summaries.append({
            "shot_id": shot.id,
            "shot_order": shot.order,
            "status": shot.status,
            "assets": status_map,
            "missing": missing,
            "stale": stale_types,
            "is_complete": is_shot_complete,
        })

    project_subtitle = Asset.objects.filter(
        project=project,
        shot__isnull=True,
        asset_type=AssetType.SUBTITLE,
    ).first()

    has_project_subtitles = (
        project_subtitle is not None
        and project_subtitle.status == AssetStatus.COMPLETED
        and not project_subtitle.is_stale
        and bool(project_subtitle.file_path)
    )

    return {
        "project_id": project.id,
        "project_title": project.title,
        "project_status": project.status,
        "shot_count": total_shots,
        "complete_shots": total_complete,
        "has_project_subtitles": has_project_subtitles,
        "shots": shot_summaries,
    }


def validate_export(*, user, project_id: int):
    """标准导出校验 —— 所有镜头必备素材齐全且非 stale"""
    summary = get_export_summary(user=user, project_id=project_id)
    errors: list[str] = []
    for s in summary["shots"]:
        if s.get("missing"):
            errors.append(f"镜头 {s['shot_order']} 缺少素材: {', '.join(s['missing'])}")
        if s.get("stale"):
            errors.append(f"镜头 {s['shot_order']} 素材已过期: {', '.join(s['stale'])}")
    if not summary.get("has_project_subtitles"):
        errors.append("项目级字幕不可用（缺失、未完成、待更新或无文件路径）")
    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "summary": summary,
    }


def build_export_package(*, user, project_id: int) -> dict:
    """构建结构化产物包 —— 聚合 project.json / storyboard.json / manifest.csv 及素材目录清单"""
    project = get_project(user=user, project_id=project_id)
    shots = Shot.objects.filter(project=project).order_by("order", "id")
    all_assets = Asset.objects.filter(project=project).select_related("shot")

    shots_data = []
    shot_asset_buckets: dict[int, list[dict]] = {}
    asset_dir_entries: dict[str, list[str]] = {
        "images": [],
        "videos": [],
        "audio": [],
        "subtitles": [],
    }
    manifest_rows: list[dict] = []
    project_assets: list[dict] = []

    for a in all_assets:
        asset_info = {
            "type": a.asset_type,
            "file_path": a.file_path,
            "file_size": a.file_size,
            "status": a.status,
            "is_stale": a.is_stale,
        }
        if a.shot_id is not None:
            shot_asset_buckets.setdefault(a.shot_id, []).append(asset_info)
            manifest_rows.append({
                "shot_order": 0,  # 将在分镜循环中填充
                "asset_type": a.asset_type,
                "file_path": a.file_path,
                "status": a.status,
            })
        else:
            project_assets.append(asset_info)
            manifest_rows.append({
                "shot_order": -1,  # -1 表示项目级
                "asset_type": a.asset_type,
                "file_path": a.file_path,
                "status": a.status,
            })

        # 按类型归入素材目录
        dir_key = _asset_type_to_dir(a.asset_type)
        if dir_key and a.file_path:
            asset_dir_entries[dir_key].append(a.file_path)

    manifest_rows = []
    for shot in shots:
        shot_assets = shot_asset_buckets.get(shot.id, [])
        shots_data.append({
            "order": shot.order,
            "description": shot.description,
            "settings": shot.settings,
            "status": shot.status,
            "assets": shot_assets,
        })
        for a in shot_assets:
            manifest_rows.append({
                "shot_order": shot.order,
                "asset_type": a["type"],
                "file_path": a["file_path"],
                "status": a["status"],
            })

    for a in project_assets:
        manifest_rows.append({
            "shot_order": -1,
            "asset_type": a["type"],
            "file_path": a["file_path"],
            "status": a["status"],
        })

    project_json = {
        "title": project.title,
        "description": project.description,
        "config": project.config,
        "status": project.status,
    }

    return {
        "project": project_json,
        "shots": shots_data,
        "manifest": manifest_rows,
        "asset_directories": asset_dir_entries,
        "project_file_name": "project.json",
        "storyboard_file_name": "storyboard.json",
        "manifest_file_name": "manifest.csv",
    }


def _asset_type_to_dir(asset_type: str) -> str:
    return {
        AssetType.IMAGE: "images",
        AssetType.VIDEO: "videos",
        AssetType.AUDIO: "audio",
        AssetType.SUBTITLE: "subtitles",
    }.get(asset_type, "")
