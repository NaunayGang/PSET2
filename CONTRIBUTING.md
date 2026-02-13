---
title: Contributing Guidelines
---

# Development Workflow

## Branch Naming

Feature branches: `feature/<issue-description>`

Fix branches: `fix/<issue-description>`

## Commit Style

Follow Angular commit style:

- Prefix: `feat`, `fix`, `docs`, `chore`, `test`, `refactor`
- Use imperative form: "adds feature" not "added feature"
- Example: `feat: adds zones CRUD endpoints`

## Pull Request Process

Create a feature branch from `master`

Make your changes

Create a PR to `master`

Request review from team members

Address review comments

Merge after approval

## Issues

All issues must be assigned to a team member

Link PRs to related issues

Use GitHub labels for categorization

## Code Quality

Run tests before submitting PR:

```bash
cd backend
source venv/bin/activate
python -m pytest tests/ -v
```

Ensure Docker builds pass:

```bash
docker compose build
```

## Documentation

Update documentation for any API changes

Reference `docs/api_contract.md` for API documentation standards

## Testing

Add tests for new features

Maintain test coverage above 80%

Run end-to-end tests before merge
