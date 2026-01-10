#!/bin/bash
# git-worktree-new: Create a new git worktree with hidden files copied over
#
# Usage: git-worktree-new -n <name> [-b <branch>] [-p <path>]
#
# Options:
#   -n, --name     Name for the worktree (required)
#   -b, --branch   Branch to checkout (default: creates new branch with name)
#   -p, --path     Base path for worktrees (default: ../worktrees)
#   -h, --help     Show this help message
#
# Example:
#   git-worktree-new -n feature-auth
#   git-worktree-new -n bugfix -b main
#   git-worktree-new -n experiment -p ~/worktrees

git_worktree_new() {
    local name=""
    local branch=""
    local base_path="../worktrees"
    local create_branch=true

    # Parse arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            -n|--name)
                name="$2"
                shift 2
                ;;
            -b|--branch)
                branch="$2"
                create_branch=false
                shift 2
                ;;
            -p|--path)
                base_path="$2"
                shift 2
                ;;
            -h|--help)
                echo "Usage: git-worktree-new -n <name> [-b <branch>] [-p <path>]"
                echo ""
                echo "Options:"
                echo "  -n, --name     Name for the worktree (required)"
                echo "  -b, --branch   Branch to checkout (default: creates new branch with name)"
                echo "  -p, --path     Base path for worktrees (default: ../worktrees)"
                echo "  -h, --help     Show this help message"
                echo ""
                echo "Hidden files/folders copied: .env*, .claude/, .vscode/, .idea/"
                return 0
                ;;
            *)
                echo "Unknown option: $1"
                echo "Use -h for help"
                return 1
                ;;
        esac
    done

    # Validate required arguments
    if [[ -z "$name" ]]; then
        echo "Error: Name is required (-n <name>)"
        echo "Use -h for help"
        return 1
    fi

    # Check if we're in a git repository
    if ! git rev-parse --git-dir > /dev/null 2>&1; then
        echo "Error: Not in a git repository"
        return 1
    fi

    # Get the root of the current worktree
    local source_root
    source_root=$(git rev-parse --show-toplevel)
    if [[ -z "$source_root" ]]; then
        echo "Error: Could not determine repository root"
        return 1
    fi

    # Resolve base path relative to source root if relative
    if [[ "$base_path" != /* ]]; then
        base_path="$source_root/$base_path"
    fi

    # Create base directory if it doesn't exist
    mkdir -p "$base_path"

    # Full path for the new worktree
    local worktree_path="$base_path/$name"

    # Check if worktree already exists
    if [[ -d "$worktree_path" ]]; then
        echo "Error: Directory already exists: $worktree_path"
        return 1
    fi

    # Determine branch to use
    if [[ -z "$branch" ]]; then
        branch="$name"
    fi

    echo "Creating worktree..."
    echo "  Name:   $name"
    echo "  Path:   $worktree_path"
    echo "  Branch: $branch"
    echo ""

    # Create the worktree
    if $create_branch; then
        # Create new branch from current HEAD
        if ! git worktree add -b "$branch" "$worktree_path"; then
            echo "Error: Failed to create worktree"
            return 1
        fi
    else
        # Use existing branch
        if ! git worktree add "$worktree_path" "$branch"; then
            echo "Error: Failed to create worktree"
            return 1
        fi
    fi

    echo ""
    echo "Copying hidden files and folders..."

    # Define patterns to copy (hidden files/folders that should be copied)
    local patterns=(
        ".env"
        ".env.*"
        ".claude"
        ".vscode"
        ".idea"
        ".devcontainer"
        ".tool-versions"
        ".nvmrc"
        ".python-version"
        ".ruby-version"
        ".node-version"
    )

    local copied=0

    for pattern in "${patterns[@]}"; do
        # Use find for glob patterns, handle both files and directories
        while IFS= read -r -d '' item; do
            local basename
            basename=$(basename "$item")
            local dest="$worktree_path/$basename"

            # Skip if already exists in destination
            if [[ -e "$dest" ]]; then
                continue
            fi

            # Skip .git (it's handled by git worktree)
            if [[ "$basename" == ".git" ]]; then
                continue
            fi

            if [[ -d "$item" ]]; then
                cp -r "$item" "$dest"
                echo "  Copied directory: $basename/"
                ((copied++))
            elif [[ -f "$item" ]]; then
                cp "$item" "$dest"
                echo "  Copied file: $basename"
                ((copied++))
            fi
        done < <(find "$source_root" -maxdepth 1 -name "$pattern" -print0 2>/dev/null)
    done

    if [[ $copied -eq 0 ]]; then
        echo "  No hidden files found to copy"
    fi

    echo ""
    echo "Worktree created successfully!"
    echo ""
    echo "To switch to the new worktree:"
    echo "  cd $worktree_path"
    echo ""
    echo "To list all worktrees:"
    echo "  git worktree list"
    echo ""
    echo "To remove this worktree later:"
    echo "  git worktree remove $worktree_path"
}

# If sourced, export the function; if executed directly, run it
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    git_worktree_new "$@"
fi
