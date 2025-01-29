# Flask API Project 🚀

This project is an API built with Flask, utilizing Flask-Limiter to enforce rate limits and Redis for caching. It retrieves weather data from [Visual Crossing Weather API](https://www.visualcrossing.com/weather-api) and processes the information to provide clear and structured responses based on the requested data. Additionally, Redis caching improves performance by storing previous queries, allowing for faster retrieval when requesting weather information for the same country again.

## Table of Contents 📑

- [Features](#features)
- [Requirements](#requirements)
- [Installation](#installation)

## Features ✨

- API built with Flask.
- Rate limiting with Flask-Limiter.
- Caching using Redis.

## Requirements ⚙️

Make sure you have the following installed:

- requirements.txt
- Python 3.11 🐍

## Installation 🛠️

1. **Clone the repository**:
   ```bash
   git clone https://github.com/Zarvi16G/Weather_API.git
   cd Weather_API
   ```
