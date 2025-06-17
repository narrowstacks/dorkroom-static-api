# Maintainer Guide: Automated Data Submission System

This guide explains how to manage the automated data submission system for the Dorkroom Static API.

## Overview

The system allows users to submit data via GitHub issue forms, which are then automatically processed into pull requests when approved by maintainers.

## Workflow

### 1. User Submission

Users submit data using one of three issue templates:

- Film Stock: `.github/ISSUE_TEMPLATE/add-film-stock.yml`
- Developer: `.github/ISSUE_TEMPLATE/add-developer.yml`
- Development Combination: `.github/ISSUE_TEMPLATE/add-combination.yml`

### 2. Initial Review

When a submission comes in:

1. **Check for completeness**: Ensure all required fields are filled
2. **Verify sources**: Check that reliable sources are provided
3. **Check for duplicates**: Look for existing entries
4. **Validate data**: Ensure information appears accurate

### 3. Approval Process

To approve a submission:

1. Add the `approved` label to the issue
2. This triggers the automated processing workflow
3. The system will:
   - Parse the issue data
   - Validate the format
   - Check for duplicates in the database
   - Generate UUIDs
   - Create a properly formatted pull request
   - Comment on the original issue with status

### 4. Final Review

1. Review the auto-generated pull request
2. Check the JSON formatting and data accuracy
3. Run validation workflows (automatic)
4. Merge when satisfied

## Managing Issues

### Labels Used

- `data-submission` - Automatically added by issue templates
- `film-stock` / `developer` / `development-combination` - Type labels
- `approved` - **Trigger label** - adds this to start processing
- `needs-review` - Needs maintainer attention
- `invalid-data` - Incomplete or incorrect submission
- `duplicate` - Already exists in database

### Common Actions

#### Approve a Submission

```
Add label: approved
```

#### Request More Information

```
Add label: needs-review
Comment with specific requests for missing information
```

#### Mark as Invalid

```
Add label: invalid-data
Comment explaining the issues
Close the issue
```

#### Mark as Duplicate

```
Add label: duplicate
Comment referencing existing entry
Close the issue
```

## Troubleshooting

### Processing Failed

If the automation fails (you'll see a failure comment on the issue):

1. Check the [workflow logs](../../actions) for specific errors
2. Common issues:

   - Missing required fields
   - Invalid data format (non-numeric ISO speeds, etc.)
   - Duplicate entries detected
   - Referenced film/developer not found (for combinations)

3. Fix by:
   - Asking user to update their submission
   - Remove `approved` label, wait for updates, then re-add

### Manual Processing

If automation fails and you need to process manually:

1. Use the Python processing script:

```bash
python .github/scripts/process_issue.py \
  --issue-body "$(cat issue.txt)" \
  --issue-type film-stock \
  --dry-run
```

2. Or use the original Python tools:

```bash
python add_film_stock.py
python add_developer.py
python add_development_combination.py
```

## Data Validation

### Automatic Validation

The system automatically validates:

- JSON structure and syntax
- Required fields presence
- Data types (numeric fields, valid enums)
- Foreign key references (film/developer IDs for combinations)
- Duplicate detection

### Manual Validation Checklist

- [ ] Sources are reliable and accessible
- [ ] Data appears accurate based on sources
- [ ] No obvious errors or typos
- [ ] Manufacturer notes are consistent with description
- [ ] ISO speeds and development times are reasonable

## Safety Features

### Preventing Data Loss

- All changes go through pull request review
- Original data is never overwritten
- Duplicate detection prevents accidental additions
- Dry-run validation before creating PRs
- Full audit trail through issues and PRs

### Rollback Process

If bad data gets merged:

1. Create a new pull request removing the bad entry
2. Reference the original issue and PR in the description
3. Update the contributor if needed

## Best Practices

### For Reviews

- Be encouraging - thank contributors for their submissions
- Be specific when requesting changes
- Provide examples of correct format when needed
- Link to similar existing entries as examples

### For Processing

- Don't rush approvals - accuracy is more important than speed
- When in doubt, ask for additional sources or clarification
- Use the `needs-review` label to collaborate with other maintainers
- Document any special cases or decisions in issue comments

## Configuration

Settings can be adjusted in `.github/config.yml`:

- Label names and colors
- Required fields for validation
- File size limits
- Branch naming patterns

## Getting Help

- Check workflow logs for specific error messages
- Use the dry-run option to test processing without making changes
- Ask other maintainers for second opinions on unclear submissions
- Open issues for bugs or improvements to the automation system
