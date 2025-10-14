from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse
from shortuuid.django_fields import ShortUUIDField
from solo.models import SingletonModel


class IssueTemplate(models.Model):
    """Template for different types of issues with specific discovery questions."""

    TEMPLATE_CHOICES = [
        ("bug", "Bug Report"),
        ("feature", "Feature Request"),
        ("task", "Task"),
        ("enhancement", "Enhancement"),
        ("question", "Question"),
    ]

    name = models.CharField(max_length=100, choices=TEMPLATE_CHOICES, unique=True)
    display_name = models.CharField(max_length=100, help_text="Human-friendly name")
    description = models.TextField(help_text="Description of when to use this template")

    # Discovery questions for conversation
    discovery_questions = models.JSONField(
        default=list, help_text="List of questions to ask during conversation to gather context"
    )

    # Required context fields
    required_context = models.JSONField(
        default=list,
        help_text="List of context fields that should be gathered (e.g., 'steps_to_reproduce', 'expected_behavior')",
    )

    # Conversation settings
    max_conversation_turns = models.PositiveIntegerField(
        default=10, help_text="Maximum number of conversation turns before auto-generating issue"
    )

    # LLM prompts
    discovery_prompt = models.TextField(help_text="System prompt for conducting discovery conversation")
    generation_prompt = models.TextField(help_text="System prompt for generating final issue from conversation context")

    # Enhancement prompt for quick mode
    quick_enhancement_prompt = models.TextField(help_text="Prompt for quick one-shot enhancement without conversation")

    # Default GitHub labels
    default_labels = models.CharField(
        max_length=200, blank=True, help_text="Comma-separated list of default GitHub labels for this issue type"
    )

    # Metadata
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Issue Template"
        verbose_name_plural = "Issue Templates"
        ordering = ["name"]

    def __str__(self) -> str:
        """Return string representation of the template."""
        return self.display_name

    @property
    def required_context_count(self) -> int:
        """Return the number of required context fields."""
        return len(self.required_context) if self.required_context else 0


class IssueConversation(models.Model):
    """Stores conversation history and context for LLM-assisted issue creation."""

    CONVERSATION_STATE_CHOICES = [
        ("discovering", "Discovering Context"),
        ("clarifying", "Clarifying Details"),
        ("summarizing", "Summarizing Information"),
        ("ready", "Ready for Generation"),
        ("complete", "Conversation Complete"),
    ]

    # Core relationships
    template = models.ForeignKey(
        IssueTemplate,
        on_delete=models.CASCADE,
        related_name="conversations",
        help_text="Template being used for this conversation",
    )

    # Conversation state
    conversation_state = models.CharField(max_length=20, choices=CONVERSATION_STATE_CHOICES, default="discovering")
    conversation_id = ShortUUIDField(unique=True, editable=False, help_text="Unique identifier for this conversation")

    # Messages and context
    messages = models.JSONField(
        default=list, help_text="List of conversation messages with role (user/assistant) and content"
    )
    context_gathered = models.JSONField(default=dict, help_text="Extracted context information organized by type")
    initial_description = models.TextField(help_text="User's initial description that started the conversation")

    # Conversation metadata
    turns_count = models.PositiveIntegerField(default=0, help_text="Number of conversation turns completed")
    ready_for_generation = models.BooleanField(
        default=False, help_text="Whether conversation has gathered enough context for issue generation"
    )
    user_abandoned = models.BooleanField(
        default=False, help_text="Whether user abandoned the conversation before completion"
    )

    # User info
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="issue_conversations",
        help_text="User who started this conversation",
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_activity_at = models.DateTimeField(auto_now=True)

    # Generated content
    generated_title = models.CharField(max_length=200, blank=True)
    generated_description = models.TextField(blank=True)
    generated_labels = models.CharField(max_length=200, blank=True)
    confidence_score = models.FloatField(
        null=True, blank=True, help_text="AI confidence in the generated content (0.0 to 1.0)"
    )

    class Meta:
        verbose_name = "Issue Conversation"
        verbose_name_plural = "Issue Conversations"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        """Return string representation of the conversation."""
        return f"Conversation {self.conversation_id} ({self.template.display_name})"

    @property
    def is_active(self) -> bool:
        """Return True if conversation is still active (not complete or abandoned)."""
        return self.conversation_state not in ["complete"] and not self.user_abandoned

    @property
    def can_generate_issue(self) -> bool:
        """Return True if conversation has enough context to generate an issue."""
        return self.ready_for_generation and self.conversation_state in ["ready", "complete"]

    def add_message(self, role: str, content: str) -> None:
        """Add a new message to the conversation."""
        if not self.messages:
            self.messages = []

        self.messages.append(
            {"role": role, "content": content, "timestamp": self.updated_at.isoformat() if self.updated_at else None}
        )

        if role == "user":
            self.turns_count += 1

    def get_context_completeness(self) -> float:
        """Calculate how much of the required context has been gathered."""
        if not self.template.required_context:
            return 1.0

        gathered = len([key for key in self.template.required_context if self.context_gathered.get(key)])
        total = len(self.template.required_context)

        return gathered / total if total > 0 else 1.0


class Issue(models.Model):
    """Represents an issue reported by a user, capturing essential details."""

    STATUS_CHOICES = [
        ("open", "Open"),
        ("in_progress", "In Progress"),
        ("resolved", "Resolved"),
        ("closed", "Closed"),
    ]

    PRIORITY_CHOICES = [
        ("low", "Low"),
        ("medium", "Medium"),
        ("high", "High"),
        ("urgent", "Urgent"),
    ]

    short_uuid = ShortUUIDField(unique=True, editable=False)
    title = models.CharField(max_length=200)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="open")
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default="medium")

    # Context capture
    reported_url = models.URLField(help_text="URL where the issue was reported from")
    user_agent = models.TextField(blank=True, help_text="Browser user agent string")

    # User info
    reported_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reported_issues")
    assigned_to = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name="assigned_issues"
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Flexible metadata storage
    payload = models.JSONField(default=dict, blank=True, help_text="Additional issue metadata")

    # LLM-generated content fields
    acceptance_criteria = models.TextField(
        blank=True, default="", help_text="AI-generated acceptance criteria for the issue"
    )
    technical_specifications = models.TextField(
        blank=True, default="", help_text="AI-generated technical specifications and implementation details"
    )
    implementation_hints = models.TextField(
        blank=True, default="", help_text="AI-generated hints and suggestions for implementation"
    )
    estimated_complexity = models.CharField(
        max_length=20, blank=True, default="", help_text="AI-estimated complexity level (low, medium, high, very-high)"
    )
    suggested_labels = models.TextField(
        blank=True, default="", help_text="AI-suggested GitHub labels (comma-separated)"
    )

    # Issue creation mode and template
    CREATION_MODE_CHOICES = [
        ("form", "Standard Form"),
        ("chat", "AI Conversation"),
        ("quick", "Quick AI Enhancement"),
    ]

    creation_mode = models.CharField(
        max_length=10, choices=CREATION_MODE_CHOICES, default="form", help_text="How this issue was created"
    )
    template = models.ForeignKey(
        IssueTemplate,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="issues",
        help_text="Template used for this issue (if any)",
    )

    # Conversation relationship
    conversation = models.OneToOneField(
        IssueConversation,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_issue",
        help_text="Conversation that led to this issue (if created via chat)",
    )

    # LLM conversation tracking
    has_llm_conversation = models.BooleanField(
        default=False, help_text="Whether this issue was created through LLM conversation"
    )
    llm_confidence_score = models.FloatField(
        null=True, blank=True, help_text="AI confidence score in the generated content (0.0 to 1.0)"
    )
    conversation_summary = models.TextField(
        blank=True, default="", help_text="Summary of key insights from the conversation"
    )

    # GitHub promotion tracking
    github_url = models.URLField(blank=True, help_text="URL of the GitHub issue if promoted")
    github_issue_number = models.PositiveIntegerField(
        null=True, blank=True, help_text="GitHub issue number if promoted"
    )
    github_promoted_at = models.DateTimeField(null=True, blank=True, help_text="When the issue was promoted to GitHub")
    github_promoted_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="promoted_issues",
        help_text="User who promoted the issue to GitHub",
    )

    class Meta:
        """Meta options for the Issue model."""

        ordering = ["-created_at"]
        verbose_name = "Issue"
        verbose_name_plural = "Issues"

    def __str__(self) -> str:
        """Return a string representation of the issue."""
        return f"#{self.short_uuid}: {self.title}"

    def get_absolute_url(self) -> str:
        """Return the absolute URL for the issue detail view."""
        return reverse("django_issue_capture:detail", kwargs={"short_uuid": self.short_uuid})

    @property
    def is_promoted_to_github(self) -> bool:
        """Return True if the issue has been promoted to GitHub."""
        return bool(self.github_url and self.github_issue_number)


class IssueCaptureSettings(SingletonModel):
    """Singleton model for issue capture configuration including GitHub and LLM settings."""

    # Feature toggle
    enabled = models.BooleanField(default=True, help_text="Enable issue capture floating button for staff/superusers")

    # GitHub integration (REQUIRED for promotion)
    github_repo = models.CharField(
        max_length=255,
        blank=True,
        default="",
        help_text="GitHub repository in format: owner/repo (e.g., 'octocat/Hello-World')",
    )
    github_api_key = models.CharField(
        max_length=255, blank=True, default="", help_text="GitHub Personal Access Token with repo access"
    )
    github_label = models.CharField(
        max_length=50, default="issue-capture", help_text="Label to apply to created GitHub issues"
    )

    # LLM integration (REQUIRED for AI features)
    llm_api_key = models.CharField(
        max_length=255,
        blank=True,
        default="",
        help_text="API key for LLM provider (OpenAI, Anthropic, etc.). Set via environment for production.",
    )
    llm_model = models.CharField(
        max_length=100,
        default="gpt-4o-mini",
        help_text="LLM model identifier (e.g., gpt-4o-mini, claude-3-5-sonnet-20241022, ollama/llama3)",
    )
    llm_enabled = models.BooleanField(default=True, help_text="Enable LLM-powered issue enhancement and generation")
    llm_temperature = models.FloatField(
        default=0.7, help_text="Temperature for LLM generation (0.0-1.0, higher = more creative)"
    )
    llm_max_tokens = models.PositiveIntegerField(
        default=2000, help_text="Maximum tokens for LLM generation (higher = longer responses)"
    )

    class Meta:
        verbose_name = "Issue Capture Settings"

    def clean(self):
        """Validate settings before saving."""
        # Validate GitHub repo format (owner/repo)
        if self.github_repo and "/" not in self.github_repo:
            raise ValidationError({"github_repo": "Repository must be in format: owner/repo"})

        # Validate GitHub API key format (basic validation)
        if self.github_api_key:
            if len(self.github_api_key) < 20:
                raise ValidationError(
                    {"github_api_key": "GitHub API key appears to be too short. Please check your token."}
                )
            if not self.github_api_key.startswith(("ghp_", "gho_", "ghu_", "ghs_", "ghr_")):
                raise ValidationError(
                    {"github_api_key": "GitHub API key should start with ghp_, gho_, ghu_, ghs_, or ghr_"}
                )

        # Validate LLM temperature range
        if not 0.0 <= self.llm_temperature <= 1.0:
            raise ValidationError({"llm_temperature": "Temperature must be between 0.0 and 1.0"})

        # Validate LLM max tokens
        if self.llm_max_tokens < 100 or self.llm_max_tokens > 10000:
            raise ValidationError({"llm_max_tokens": "Max tokens must be between 100 and 10,000"})

    def __str__(self):
        """Return string representation of issue capture settings."""
        return "Issue Capture Settings"
