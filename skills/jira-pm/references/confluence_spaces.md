# Confluence Space Registry

Maintained manually. Add a row whenever a new Confluence space is created.
The jira-pm OPEN flow reads this before creating a PRD page — pick the space
whose domain most closely matches the feature being built.

| Space key | Space name | Root page ID | JIRA project key | Domain / what belongs here |
|---|---|---|---|---|
| `your-space-1` | Your Space 1 | `<page-id>` | `YOUR_PROJECT_1` | Describe what types of features belong in this space |
| `your-space-2` | Your Space 2 | `<page-id>` | `YOUR_PROJECT_2` | Describe what types of features belong in this space |
| `your-space-3` | Your Space 3 | `<page-id>` | `YOUR_PROJECT_3` | Describe what types of features belong in this space |

## How to find page IDs

In Confluence, open the space home page. The page ID appears in the URL:
`https://your-domain.atlassian.net/wiki/spaces/SPACEKEY/pages/<PAGE_ID>`

## How to pick

1. Read the feature name and problem statement from the PRD draft.
2. Match against the Domain column above — pick the closest fit.
3. Use the JIRA project key from the same row when creating JIRA issues.
4. Always set `parent_id` to the Root page ID of the chosen space so the PRD nests correctly under the space home.
5. If no space fits, ask the user before creating the page.
