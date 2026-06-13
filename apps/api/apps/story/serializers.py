def serialize_project(project):
    return {
        "id": project.id,
        "title": project.title,
        "description": project.description,
        "status": project.status,
        "status_display": project.get_status_display(),
        "config": project.config,
        "shot_count": getattr(project, "shot_count", 0),
        "created_at": project.created_at.isoformat(),
        "updated_at": project.updated_at.isoformat(),
    }


def serialize_shot(shot):
    return {
        "id": shot.id,
        "project_id": shot.project_id,
        "order": shot.order,
        "description": shot.description,
        "status": shot.status,
        "status_display": shot.get_status_display(),
        "settings": shot.settings,
        "assets": [serialize_asset(a) for a in getattr(shot, "prefetched_assets", [])],
        "created_at": shot.created_at.isoformat(),
        "updated_at": shot.updated_at.isoformat(),
    }


def serialize_asset(asset):
    return {
        "id": asset.id,
        "project_id": asset.project_id,
        "shot_id": asset.shot_id,
        "asset_type": asset.asset_type,
        "asset_type_display": asset.get_asset_type_display(),
        "file_path": asset.file_path,
        "file_size": asset.file_size,
        "status": asset.status,
        "status_display": asset.get_status_display(),
        "is_stale": asset.is_stale,
        "outdated_by_id": asset.outdated_by_id,
        "metadata": asset.metadata,
        "created_at": asset.created_at.isoformat(),
        "updated_at": asset.updated_at.isoformat(),
    }


def serialize_job(job):
    return {
        "id": job.id,
        "project_id": job.project_id,
        "shot_id": job.shot_id,
        "job_type": job.job_type,
        "job_type_display": job.get_job_type_display(),
        "status": job.status,
        "status_display": job.get_status_display(),
        "input_data": job.input_data,
        "output_data": job.output_data,
        "retry_of_id": job.retry_of_id,
        "attempt": job.attempt,
        "started_at": job.started_at.isoformat() if job.started_at else None,
        "completed_at": job.completed_at.isoformat() if job.completed_at else None,
        "error_message": job.error_message,
        "created_at": job.created_at.isoformat(),
        "updated_at": job.updated_at.isoformat(),
    }


def serialize_job_summary(job):
    return {
        "id": job.id,
        "job_type": job.job_type,
        "job_type_display": job.get_job_type_display(),
        "status": job.status,
        "status_display": job.get_status_display(),
        "shot_id": job.shot_id,
        "attempt": job.attempt,
        "created_at": job.created_at.isoformat(),
    }
