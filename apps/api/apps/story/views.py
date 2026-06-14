from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

import csv
import io
import json
import zipfile

from django.http import HttpResponse

from apps.story import serializers, services


class ProjectCollectionView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        project_status = request.query_params.get("status")
        limit = min(int(request.query_params.get("limit", 50)), 200)
        projects = services.list_projects(user=request.user, status=project_status, limit=limit)
        return Response([serializers.serialize_project(p) for p in projects])

    def post(self, request):
        title = request.data.get("title", "").strip()
        if not title:
            return Response({"error": "标题不能为空"}, status=status.HTTP_400_BAD_REQUEST)
        if len(title) > 255:
            return Response({"error": "标题不能超过255个字符"}, status=status.HTTP_400_BAD_REQUEST)

        project = services.create_project(
            user=request.user,
            title=title,
            description=request.data.get("description", ""),
            config=request.data.get("config"),
        )
        return Response(serializers.serialize_project(project), status=status.HTTP_201_CREATED)


class ProjectItemView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, project_id: int):
        project = services.get_project(user=request.user, project_id=project_id)
        return Response(serializers.serialize_project(project))

    def patch(self, request, project_id: int):
        project = services.update_project(
            user=request.user,
            project_id=project_id,
            title=request.data.get("title"),
            description=request.data.get("description"),
            config=request.data.get("config"),
        )
        return Response(serializers.serialize_project(project))


class ShotListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, project_id: int):
        shots = services.list_shots(user=request.user, project_id=project_id)
        return Response([serializers.serialize_shot(s) for s in shots])

    def post(self, request, project_id: int):
        order = request.data.get("order")
        if order is None:
            return Response({"error": "序号不能为空"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            order = int(order)
        except (TypeError, ValueError):
            return Response({"error": "序号必须为整数"}, status=status.HTTP_400_BAD_REQUEST)

        shot = services.create_shot(
            user=request.user,
            project_id=project_id,
            order=order,
            description=request.data.get("description", ""),
            settings=request.data.get("settings"),
        )
        return Response(serializers.serialize_shot(shot), status=status.HTTP_201_CREATED)


class ShotItemView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, shot_id: int):
        shot = services.get_shot(user=request.user, shot_id=shot_id)
        return Response(serializers.serialize_shot(shot))

    def patch(self, request, shot_id: int):
        shot = services.update_shot(
            user=request.user,
            shot_id=shot_id,
            description=request.data.get("description"),
            settings=request.data.get("settings"),
        )
        return Response(serializers.serialize_shot(shot))


class JobListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, project_id: int):
        shot_id = request.query_params.get("shot_id")
        if shot_id is not None:
            try:
                shot_id = int(shot_id)
            except (TypeError, ValueError):
                return Response({"error": "shot_id 必须为整数"}, status=status.HTTP_400_BAD_REQUEST)
        job_type = request.query_params.get("job_type")
        limit = min(int(request.query_params.get("limit", 100)), 500)
        jobs = services.list_jobs(
            user=request.user,
            project_id=project_id,
            shot_id=shot_id,
            job_type=job_type,
            limit=limit,
        )
        return Response([serializers.serialize_job_summary(j) for j in jobs])

    def post(self, request, project_id: int):
        shot_id = request.data.get("shot_id")
        if shot_id is not None:
            try:
                shot_id = int(shot_id)
            except (TypeError, ValueError):
                return Response({"error": "shot_id 必须为整数"}, status=status.HTTP_400_BAD_REQUEST)

        job_type = request.data.get("job_type", "").strip()
        if not job_type:
            return Response({"error": "任务类型不能为空"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            job = services.create_job(
                user=request.user,
                project_id=project_id,
                shot_id=shot_id,
                job_type=job_type,
            )
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(serializers.serialize_job(job), status=status.HTTP_201_CREATED)


class JobItemView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, job_id: int):
        job = services.get_job(user=request.user, job_id=job_id)
        return Response(serializers.serialize_job(job))


class JobRetryView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, job_id: int):
        job = services.retry_job(user=request.user, job_id=job_id)
        return Response(serializers.serialize_job(job), status=status.HTTP_201_CREATED)


class ExportSummaryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, project_id: int):
        summary = services.get_export_summary(user=request.user, project_id=project_id)
        return Response(summary)


class ExportValidateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, project_id: int):
        result = services.validate_export(user=request.user, project_id=project_id)
        return Response(result)


class ExportDownloadView(APIView):
    """结构化产物包下载 —— 生成 ZIP 含 project.json / storyboard.json / manifest.csv 及素材目录"""
    permission_classes = [IsAuthenticated]

    def get(self, request, project_id: int):
        package = services.build_export_package(user=request.user, project_id=project_id)
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
            zf.writestr(
                package["project_file_name"],
                json.dumps(package["project"], ensure_ascii=False, indent=2),
            )
            zf.writestr(
                package["storyboard_file_name"],
                json.dumps(package["shots"], ensure_ascii=False, indent=2),
            )
            csv_buffer = io.StringIO()
            writer = csv.DictWriter(csv_buffer, fieldnames=["shot_order", "asset_type", "file_path", "status"])
            writer.writeheader()
            for row in package["manifest"]:
                writer.writerow(row)
            zf.writestr(package["manifest_file_name"], csv_buffer.getvalue())

            for dir_name, paths in package.get("asset_directories", {}).items():
                if paths:
                    zf.writestr(f"{dir_name}/.keep", "")
                    zf.writestr(f"{dir_name}/_manifest.json", json.dumps(paths, ensure_ascii=False, indent=2))

        buf.seek(0)
        project_title = package["project"].get("title", "export")
        response = HttpResponse(buf.getvalue(), content_type="application/zip")
        response["Content-Disposition"] = f'attachment; filename="{project_title}_export.zip"'
        return response
