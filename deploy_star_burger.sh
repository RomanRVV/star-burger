#!/bin/bash
set -e
set -u

source .env

REMOTE_REPO="git@github.com:RomanRVV/star-burger.git"
BRANCH="master"
PROJECT_DIR="/opt/star-burger"
VENV_DIR="/opt/star-burger/env"
STATIC_DIR="/opt/star-burger/staticfiles"
MIGRATION_DIR="/opt/star-burger/foodcartapp/migrations"
GUNICORN_SERVICE="starburger"

update_code() {
    echo "Updating code from the remote repository..."
    cd $PROJECT_DIR
    git pull origin $BRANCH
}


install_dependencies() {
    echo "Installing dependencies..."
    source $VENV_DIR/bin/activate
    pip install -r requirements.txt

    echo "Installing Node.js dependencies..."
    npm ci --dev
}

run_migrations() {
    echo "Applying database migrations..."
    python manage.py migrate
}

collect_static() {
    echo "Collecting static files..."
    python manage.py collectstatic --noinput
}


echo "Starting deployment process..."

update_code
install_dependencies
run_migrations
collect_static

echo "Rebuilding JS code..."
./node_modules/.bin/parcel build bundles-src/index.js --dist-dir bundles --public-url="./"

echo "Restarting Gunicorn..."
sudo systemctl restart $GUNICORN_SERVICE
echo "Gunicorn restarted successfully!"

# Restart Nginx
echo "Restarting Nginx..."
sudo systemctl reload nginx.service
echo "Nginx restarted successfully!"

commit=$(git rev-parse master)

echo "Sending a notification to Rollbar..."
curl -H "X-Rollbar-Access-Token: $ROLLBAR_KEY" \
     -H "accept: application/json" \
     -H "content-type: application/json" \
     -X POST "https://api.rollbar.com/api/1/deploy" \
     -d '{
  "environment": "production",
  "revision": "'"$commit"'",
  "rollbar_username": "'$(whoami)'",
  "local_username": "'$(whoami)'",
  "comment": "deploy",
  "status": "succeeded"
}'

echo "Deployment completed successfully!"
