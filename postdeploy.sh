#!/bin/bash

# Build and deploy the backend
cd backend
heroku git:remote -a wise-cs
git push backend master

# Build and deploy the frontend
cd ../frontend
heroku git:remote -a wise-cs-frontend
git push frontend master
