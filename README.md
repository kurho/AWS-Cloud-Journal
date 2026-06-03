Cloud Journal is a mini project built on AWS using EC2, RDS, and S3. It demonstrates how a cloud-hosted web application can interact with a managed database service and object storage while following fundamental cloud architecture principles.

## Project Overview

This project allows users to create and view journal entries through a web interface built with Flask. Journal data is stored in Amazon RDS (MySQL), while images are stored in Amazon S3. The application is deployed on an Amazon EC2 instance.

## Architecture

User
↓
EC2 (Flask Application)
↓
Amazon RDS (MySQL Database)

Amazon S3 (Image Storage)

## AWS Services Used

- Amazon EC2
  - Hosts the Flask web application
  - Handles incoming HTTP requests

- Amazon RDS (MySQL)
  - Stores journal entries
  - Provides managed database services

- Amazon S3
  - Stores application images and assets
  - Demonstrates cloud object storage

## Technologies Used

- Python
- Flask
- MySQL
- Amazon EC2
- Amazon RDS
- Amazon S3

## Features

- Create journal entries
- View journal entries
- Store journal data in RDS
- Display images from S3
- Cloud-based deployment on EC2

## Screenshots

### Application Homepage

<img width="1912" height="977" alt="Screenshot 2026-06-03 230747" src="https://github.com/user-attachments/assets/4769ec49-5457-4e6c-80e6-8aaf62000a0d" />

### AWS Architecture

<img width="810" height="597" alt="mermaid-diagram" src="https://github.com/user-attachments/assets/1d3fe8ef-3eb4-46d6-9ef2-9d1cd656313b" />


## What I Learned

Through this project, I gained hands-on experience with:

- Launching and configuring EC2 instances
- Connecting applications to Amazon RDS
- Working with Amazon S3 object storage
- Using environment variables for configuration
- Deploying Flask applications on cloud infrastructure
- Troubleshooting networking and connectivity issues
- Connecting VS Code to remote servers through SSH

## Future Improvements

- User authentication
- Rich text journal entries
- File uploads
- Search and filtering
- Custom domain and HTTPS
- Load balancing and auto scaling

## Author

Rhome Louie D. Saringayat

BS Information Technology
Polytechnic University of the Philippines
