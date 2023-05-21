#!/bin/bash

# Build and deploy the backend
cd backend
heroku create --remote backend
git push backend master

# Build and deploy the frontend
cd ../frontend
heroku create --remote frontend
git push frontend master
