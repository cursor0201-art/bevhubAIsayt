from rest_framework import serializers
from core.domain.models import Project, Page, Deployment, Workspace, AITask, ProjectFile, ProjectReview, ProjectFixRun, GenerationStep

class GenerationStepSerializer(serializers.ModelSerializer):
    class Meta:
        model = GenerationStep
        fields = [
            'id', 
            'step_name', 
            'status', 
            'started_at', 
            'completed_at', 
            'duration_seconds', 
            'tokens_used', 
            'model_name', 
            'cost', 
            'error_message'
        ]

class ProjectCreateRequestSerializer(serializers.Serializer):
    """
    Validates input prompt for new project generation.
    """
    prompt = serializers.CharField(
        min_length=10, 
        max_length=1000, 
        help_text="Single prompt describing the business concept"
    )


class PageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Page
        fields = ['id', 'slug', 'title', 'layout_ast', 'raw_content', 'created_at']


class DeploymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Deployment
        fields = ['id', 'status', 'commit_hash', 'deploy_url', 'created_at']


class ProjectFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectFile
        fields = ['id', 'path', 'content', 'created_at']


class ProjectDetailSerializer(serializers.ModelSerializer):
    pages = PageSerializer(many=True, read_only=True)
    deployments = DeploymentSerializer(many=True, read_only=True)
    files = ProjectFileSerializer(many=True, read_only=True)

    class Meta:
        model = Project
        fields = [
            'id', 
            'project_name', 
            'subdomain', 
            'custom_domain', 
            'design_system', 
            'pages', 
            'deployments', 
            'files',
            'created_at'
        ]


class WorkspaceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Workspace
        fields = ['id', 'name', 'settings', 'created_at']


class AITaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = AITask
        fields = ['id', 'workspace', 'project', 'prompt', 'status', 'progress', 'logs', 'tokens_used', 'duration_ms', 'created_at']


class ProjectReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectReview
        fields = [
            'id',
            'project',
            'overall_score',
            'architecture_score',
            'performance_score',
            'security_score',
            'seo_score',
            'accessibility_score',
            'ux_score',
            'typescript_score',
            'react_score',
            'deployment_score',
            'issues',
            'recommendations',
            'created_at'
        ]


class ProjectFixRunSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectFixRun
        fields = [
            'id',
            'project',
            'before_score',
            'after_score',
            'fixed_count',
            'remaining_count',
            'rollback_applied',
            'snapshot',
            'logs',
            'created_at'
        ]


