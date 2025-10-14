from django.core.management.base import BaseCommand

from django_issue_capture.models import IssueTemplate


class Command(BaseCommand):
    help = "Set up default issue templates for the conversation system"

    def handle(self, *args, **options):
        templates_data = [
            {
                "name": "bug",
                "display_name": "Bug Report",
                "description": "Report a software bug or defect",
                "discovery_questions": [
                    "What specific problem are you experiencing?",
                    "What steps can I follow to reproduce this issue?",
                    "What did you expect to happen?",
                    "What actually happened instead?",
                    "When did you first notice this issue?",
                    "Does this happen consistently or intermittently?",
                    "What browser/device are you using?",
                    "Are there any error messages displayed?",
                ],
                "required_context": [
                    "problem_description",
                    "steps_to_reproduce",
                    "expected_behavior",
                    "actual_behavior",
                    "environment",
                    "frequency",
                ],
                "discovery_prompt": """
                You are a technical support specialist helping to create comprehensive bug reports.
                Your goal is to gather enough information so developers can understand, reproduce, and fix the issue.

                Ask focused questions to understand:
                1. The specific problem and its symptoms
                2. Step-by-step reproduction instructions
                3. Expected vs actual behavior
                4. Environment details (browser, device, etc.)
                5. When and how often it occurs
                6. Any error messages or patterns

                Be conversational but systematic. Don't ask for information already provided.
                """,
                "generation_prompt": """
                Create a comprehensive bug report with the following structure:

                ## Bug Description
                Clear, specific description of the problem

                ## Steps to Reproduce
                1. Numbered list of exact steps
                2. Include any specific data or inputs
                3. Be detailed enough for anyone to follow

                ## Expected Behavior
                What should happen

                ## Actual Behavior
                What actually happens instead

                ## Environment
                - Browser/device information
                - Any relevant system details

                ## Additional Context
                - Error messages
                - Screenshots or logs (if mentioned)
                - Frequency/timing information

                Make it actionable for developers.
                """,
                "quick_enhancement_prompt": """
                Enhance this bug report:

                Title: {title}
                Description: {description}

                Add structure and missing details:
                - Clear problem statement
                - Reproduction steps (if missing)
                - Expected vs actual behavior
                - Environment context
                - Error messages or symptoms

                Make it comprehensive and actionable for developers.
                """,
                "default_labels": "bug",
                "max_conversation_turns": 10,
            },
            {
                "name": "feature",
                "display_name": "Feature Request",
                "description": "Request a new feature or enhancement",
                "discovery_questions": [
                    "What feature or functionality would you like to see?",
                    "What problem would this solve for you?",
                    "How do you envision this working?",
                    "Who would benefit from this feature?",
                    "Are there any existing solutions you've seen elsewhere?",
                    "How important is this feature to you?",
                    "What would success look like?",
                ],
                "required_context": [
                    "feature_description",
                    "problem_solved",
                    "user_benefit",
                    "expected_behavior",
                    "use_cases",
                ],
                "discovery_prompt": """
                You are a product manager helping to define new features.
                Your goal is to understand the user need and create a clear feature specification.

                Focus on understanding:
                1. What the user wants to accomplish
                2. Why this feature is needed (the problem it solves)
                3. Who would benefit and how
                4. How the feature should work
                5. Success criteria and acceptance criteria
                6. Priority and importance

                Ask clarifying questions to get specifics, not just high-level requests.
                """,
                "generation_prompt": """
                Create a comprehensive feature request with:

                ## Feature Summary
                Brief, clear description of the requested feature

                ## Problem Statement
                What problem this solves and why it matters

                ## User Story
                As a [user type], I want [functionality] so that [benefit]

                ## Detailed Description
                How the feature should work

                ## Acceptance Criteria
                - Clear, testable criteria for completion
                - Edge cases and error handling
                - User interface considerations

                ## Use Cases
                Specific scenarios where this feature would be used

                ## Priority Justification
                Why this feature matters and its relative importance

                Make it actionable for development teams.
                """,
                "quick_enhancement_prompt": """
                Enhance this feature request:

                Title: {title}
                Description: {description}

                Add structure and clarity:
                - Clear problem statement
                - User story format
                - Detailed functionality description
                - Acceptance criteria
                - Use cases and examples
                - Success metrics

                Make it comprehensive and actionable.
                """,
                "default_labels": "feature,enhancement",
                "max_conversation_turns": 12,
            },
            {
                "name": "task",
                "display_name": "Task",
                "description": "General task or work item",
                "discovery_questions": [
                    "What needs to be accomplished?",
                    "What are the specific deliverables?",
                    "Are there any dependencies or prerequisites?",
                    "What does completion look like?",
                    "Are there any constraints or requirements?",
                    "What's the priority and timeline?",
                ],
                "required_context": ["task_description", "deliverables", "completion_criteria", "dependencies"],
                "discovery_prompt": """
                You are helping to define clear, actionable work tasks.
                Your goal is to create tasks that are specific, measurable, and achievable.

                Understand:
                1. What specific work needs to be done
                2. What the deliverables are
                3. Success criteria
                4. Any dependencies or constraints
                5. Priority and timeline considerations

                Make tasks clear and actionable.
                """,
                "generation_prompt": """
                Create a well-defined task with:

                ## Task Overview
                Clear description of what needs to be accomplished

                ## Deliverables
                Specific outputs or results expected

                ## Acceptance Criteria
                How to know when the task is complete

                ## Dependencies
                Any prerequisites or blocking items

                ## Technical Requirements
                Implementation details or constraints

                ## Definition of Done
                Clear completion criteria

                Make it actionable and unambiguous.
                """,
                "quick_enhancement_prompt": """
                Enhance this task:

                Title: {title}
                Description: {description}

                Add clarity and structure:
                - Specific deliverables
                - Clear acceptance criteria
                - Dependencies or prerequisites
                - Technical requirements
                - Definition of done

                Make it actionable and complete.
                """,
                "default_labels": "task",
                "max_conversation_turns": 8,
            },
            {
                "name": "enhancement",
                "display_name": "Enhancement",
                "description": "Improvement to existing functionality",
                "discovery_questions": [
                    "What existing functionality would you like to improve?",
                    "What specific improvements do you have in mind?",
                    "What problems does the current implementation have?",
                    "How would these changes benefit users?",
                    "Are there any examples of how this works elsewhere?",
                    "What would the improved experience look like?",
                ],
                "required_context": [
                    "current_functionality",
                    "proposed_improvements",
                    "problems_addressed",
                    "user_benefit",
                ],
                "discovery_prompt": """
                You are helping to define improvements to existing features.
                Your goal is to understand what currently exists, what's wrong with it, and how to make it better.

                Focus on:
                1. Current functionality and its limitations
                2. Specific improvements proposed
                3. Benefits to users
                4. Impact on existing workflows
                5. Success criteria for the enhancement

                Be specific about what changes are needed.
                """,
                "generation_prompt": """
                Create a comprehensive enhancement request:

                ## Current State
                Description of existing functionality and its limitations

                ## Proposed Enhancement
                Specific improvements and changes

                ## Benefits
                How this improves the user experience

                ## Implementation Considerations
                Technical approach and requirements

                ## Acceptance Criteria
                How to measure success of the enhancement

                ## Impact Assessment
                Effects on existing functionality and users

                Make it clear and actionable for development.
                """,
                "quick_enhancement_prompt": """
                Enhance this improvement request:

                Title: {title}
                Description: {description}

                Add structure and detail:
                - Current state and limitations
                - Specific improvements proposed
                - User benefits
                - Implementation approach
                - Success criteria
                - Impact considerations

                Make it comprehensive and actionable.
                """,
                "default_labels": "enhancement",
                "max_conversation_turns": 10,
            },
        ]

        created_count = 0
        updated_count = 0

        for template_data in templates_data:
            template, created = IssueTemplate.objects.update_or_create(
                name=template_data["name"], defaults=template_data
            )

            if created:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f"Created template: {template.display_name}"))
            else:
                updated_count += 1
                self.stdout.write(self.style.WARNING(f"Updated template: {template.display_name}"))

        self.stdout.write(
            self.style.SUCCESS(
                f"\nSetup complete! Created {created_count} new templates, updated {updated_count} existing templates."
            )
        )

        if created_count > 0 or updated_count > 0:
            self.stdout.write("You can now use the conversation system with these templates.")
