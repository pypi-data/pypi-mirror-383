# Django Issue Capture

AI-powered GitHub issue creation and management system for Django with conversational UX and LLM enhancement.

## Features

- **AI-Powered Issue Generation**: Use LiteLLM to generate comprehensive issues from basic descriptions
- **Model Optionality**: Support for OpenAI, Anthropic, Ollama, and any LiteLLM-compatible provider
- **Conversational UI**: Chat-based interface for gathering issue context
- **GitHub Integration**: Direct promotion of issues to GitHub repositories
- **Template System**: Predefined templates for bugs, features, tasks, and enhancements
- **HTMX Admin**: Interactive admin interface with one-click GitHub promotion
- **Markdown Support**: Full markdown rendering with sanitization

## Installation

```bash
pip install django-issue-capture
```

## Quick Start

1. Add to `INSTALLED_APPS`:

```python
INSTALLED_APPS = [
    # ...
    "solo",  # Required dependency
    "django_markdownify",  # For markdown rendering
    "django_issue_capture",
]
```

2. Add context processor (optional, for floating button):

```python
TEMPLATES = [{
    'OPTIONS': {
        'context_processors': [
            # ...
            'django_issue_capture.context_processors.issue_capture_settings',
        ],
    },
}]
```

3. Include URLs:

```python
from django.urls import include, path

urlpatterns = [
    # ...
    path("issues/", include("django_issue_capture.urls")),
]
```

4. Run migrations:

```bash
python manage.py migrate
```

5. Configure in Django Admin:

Navigate to **Issue Capture Settings** and configure:
- **GitHub**: Repository (`owner/repo`) and Personal Access Token
- **LLM**: API key and model (e.g., `gpt-4o-mini`, `claude-3-5-sonnet-20241022`)

6. Set up issue templates:

```bash
python manage.py setup_issue_templates
```

## Configuration

### LLM Models

Supports any LiteLLM-compatible model:

- **OpenAI**: `gpt-4o-mini`, `gpt-4o`, `gpt-3.5-turbo`
- **Anthropic**: `claude-3-5-sonnet-20241022`, `claude-3-opus-20240229`
- **Local**: `ollama/llama3`, `ollama/mistral`
- **Others**: See [LiteLLM docs](https://docs.litellm.ai/docs/)

### GitHub Integration

Requires a Personal Access Token with `repo` scope:
1. Go to GitHub Settings → Developer settings → Personal access tokens
2. Generate new token with `repo` scope
3. Add to **Issue Capture Settings** in Django admin

### Environment Variables (Production)

For production, use environment variables:

```python
# settings.py
from django.conf import settings

# Override singleton defaults with env vars
ISSUE_CAPTURE_LLM_API_KEY = os.getenv("ISSUE_CAPTURE_LLM_API_KEY")
ISSUE_CAPTURE_GITHUB_API_KEY = os.getenv("GITHUB_API_KEY")
```

## Usage

### Create Issue via UI

1. Navigate to `/issues/create/`
2. Choose creation mode:
   - **Standard Form**: Manual entry
   - **AI Quick Generate**: One-shot AI enhancement
   - **AI Chat**: Conversational context gathering

### Promote to GitHub

1. View issues at `/issues/list/`
2. Click issue to view details
3. Click "Promote to GitHub" (or use admin interface)

### Admin Interface

The Django admin provides:
- Issue management with status tracking
- One-click GitHub promotion (HTMX-powered)
- Template configuration
- Conversation history viewing

## Development

```bash
# Clone and install
git clone https://github.com/directory-platform/django-issue-capture
cd django-issue-capture
uv sync --extra dev

# Run tests
PYTHONPATH=. uv run python tests/manage.py test

# Run quality checks
ruff check src/ tests/
ruff format src/ tests/
mypy src/
```

## Dependencies

- Django ≥ 4.2
- django-solo ≥ 2.0
- shortuuid ≥ 1.0
- requests ≥ 2.32
- litellm ≥ 1.70
- django-markdownify ≥ 0.9

## License

MIT License - see LICENSE file for details.

## Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## Support

- **Issues**: https://github.com/directory-platform/django-issue-capture/issues
- **Docs**: https://github.com/directory-platform/django-issue-capture

## Credits

Part of the Directory Platform ecosystem. Extracted from [directory-builder](https://github.com/heysamtexas/directory-builder).
