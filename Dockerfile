# Use an official Python runtime as a parent image
FROM python:3.10

# Встановимо змінну середовища
ENV APP_HOME /app

# Встановимо робочу директорію всередині контейнера
WORKDIR $APP_HOME

# Copy the current directory contents into the container at /usr/src/app
COPY . .

# Install any needed packages specified in requirements.txt
RUN pip install -r requirements.txt

# Run bot.py when the container launches
ENTRYPOINT ["python", "app.py"]
