#! /usr/bin/env bash
set -e

# Change current working directory to be the root, regardless of how this script is invoked
cd "$(dirname "${BASH_SOURCE[0]}")/.." || exit 1

# Build a function to get secrets as inputs to the build
function set_parameters() {
                while [[ $# -gt 0 ]]
                do
                                key="$1"

                                case $key in
                                                --token)
                                                export TOKEN="$2"
                                                shift
                                                shift
                                                ;;
                                                --organization)
                                                export ORGANIZATION="$2"
                                                shift
                                                shift
                                                ;;
                                                --project)
                                                export PROJECT="$2"
                                                shift
                                                shift
                                                ;;
                                                --project-identifier)
                                                export PROJECT_IDENTIFIER="$2"
                                                shift
                                                shift
                                                ;;
                                                --azure-openai-key)
                                                export AZURE_OPENAI_KEY="$2"
                                                shift
                                                shift
                                                ;;
                                                --azure-openai-endpoint)
                                                export AZURE_OPENAI_ENDPOINT="$2"
                                                shift
                                                shift
                                                ;;
                                                --azure-openai-deployment-name)
                                                export AZURE_OPENAI_DEPLOYMENT_NAME="$2"
                                                shift
                                                shift
                                                ;;
                                                --help)
                                                echo "Usage: $0 [options]"
                                                echo "Options:"
                                                echo "  --token <token>                          Personal access token for Azure DevOps (do not base64 encode)"
                                                echo "  --organization <ORGANIZATION>            Azure DevOps organization name"
                                                echo "  --project <project>                      Azure DevOps project name"
                                                echo "  --project-identifier <project-identifier> Azure DevOps project identifier"
                                                echo "  --azure-openai-key <azure-openai-key>     Azure OpenAI API key"
                                                echo "  --azure-openai-endpoint <azure-openai-endpoint> Azure OpenAI API endpoint"
                                                echo "  --azure-openai-deployment-name <azure-openai-deployment-name> Azure OpenAI deployment name"
                                                echo "  --help                                   Display this help message"
                                                exit 0
                                                ;;
                                                *)
                                                echo "Unknown parameter: $1"
                                                shift
                                                ;;
                                esac
                done
}

function build_secrets_file() {
                # Create the secrets directory if it doesn't exist
                mkdir -p docker/env/secrets

                # Build the secrets file
                cat <<EOF > docker/env/secrets/secrets.env
TOKEN=$TOKEN
ORGANIZATION=$ORGANIZATION
PROJECT=$PROJECT
PROJECT_IDENTIFIER=$PROJECT_IDENTIFIER
AZURE_OPENAI_KEY=$AZURE_OPENAI_KEY
AZURE_OPENAI_ENDPOINT=$AZURE_OPENAI_ENDPOINT
AZURE_OPENAI_DEPLOYMENT_NAME=$AZURE_OPENAI_DEPLOYMENT_NAME
EOF
}

function run_app() {
        docker compose -f docker/docker-compose.yml up
}

function main() {
        # Check to see if help was requested
        if [[ "$*" == *--help* ]]; then
                set_parameters "$@"
        else
                if [ $# -eq 0 ]; then
                        echo "No input parameters detected, skip adding build secrets"
                        echo "Run the script with --help to see the list of parameters"
                else
                        echo "Parameters detected, adding build secrets from input parameters"
                        set_parameters "$@"
                        build_secrets_file
                fi
                run_app
        fi
}

main "$@"
